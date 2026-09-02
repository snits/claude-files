"""Spawn one headless claude session per issue in its own worktree."""
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from . import gitops
from .state import AgentRecord, Paths, branch_for

PREFLIGHT = Path(__file__).resolve().parent / "preflight.py"
MODEL_TRAILER = {"opus": "claude-opus-5", "sonnet": "claude-sonnet-5", "fable": "claude-fable-5-1", "haiku": "claude-haiku-4-5"}


@dataclass
class Config:
    model: str = "opus"
    budget_usd: float = 25.0
    permission_mode: str = "bypassPermissions"
    memory_high: str = "4G"
    memory_max: str = "6G"
    use_systemd: bool = True


def brief(ref: str, target: str, actor: str, worktree, run_id: str, model: str) -> str:
    trailer = MODEL_TRAILER.get(model, model)
    return f"""/super-do {ref} {target}

Dispatcher constraints (kata-dispatch run {run_id}, worker for {ref}). These override anything in /super-do that conflicts:
- You are in worktree {worktree} on branch dispatch/{ref}, based on {target}. You are ALREADY in your worktree: do NOT run `git worktree add`, do NOT create or switch branches; /super-do's "base your worktree off" step is already done for you. Every edit stays in this worktree. Run `python3 {PREFLIGHT}` before your first edit; a PreToolUse hook enforces the same check on every Edit/Write and will refuse edits outside this worktree.
- The issue is already claimed for you as actor {actor}, and KATA_AUTHOR is set to that actor, so every kata mutation you make is attributed correctly. Do not claim, do not use --force.
- Stop at a reviewed branch. do NOT merge, do NOT run /verify-branch, do NOT touch {target} or main. The dispatcher rebases, runs the gate, and merges. Commit with `git commit -s` and the trailer `Assisted-by: Claude:{trailer}`. Leave the worktree clean (no uncommitted changes) when you stop.
- If you need a fact only a person can supply, a ruling between defensible options, or you hit the review cap: `kata label add {ref} <needsinfo|needs-decision|needs-review>`, `kata comment {ref} --body "<why>"`, then `kata unassign {ref}`, and stop.
- If the issue needs no code change, comment the finding on the issue and stop; do not close it.
- Your final message MUST begin with exactly one of these lines:
  OUTCOME: reviewed-branch
  OUTCOME: escalated <label>
  OUTCOME: no-change
"""


def write_settings(run_dir: Path, ref: str) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    p = run_dir / f"{ref}.settings.json"
    p.write_text(json.dumps({"hooks": {"PreToolUse": [{"matcher": "Edit|Write|MultiEdit|NotebookEdit",
                                                        "hooks": [{"type": "command", "command": f"python3 {PREFLIGHT} --hook"}]}]}}, indent=1))
    return p


def _link_shared_dirs(repo: Path, wt: Path):
    """Mirror Claude Code's worktree shared-dirs: .scratchpad points at the primary's."""
    for name in (".scratchpad",):
        src, dst = repo / name, wt / name
        if src.is_dir() and not dst.exists():
            dst.symlink_to(src, target_is_directory=True)


def spawn(paths: Paths, ref: str, actor: str, run_id: str, cfg: Config, target: str = "integration"):
    wt = paths.worktree(ref)
    branch = branch_for(ref)
    run_dir = paths.run_dir(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    gitops.worktree_add(paths.repo, wt, branch, target)
    _link_shared_dirs(paths.repo, wt)
    settings = write_settings(run_dir, ref)
    log = run_dir / f"{ref}.jsonl"
    cmd = ["claude", "-p", brief(ref, target, actor, str(wt), run_id, cfg.model),
           "--model", cfg.model, "--max-budget-usd", str(cfg.budget_usd),
           "--permission-mode", cfg.permission_mode, "--settings", str(settings),
           "--output-format", "stream-json", "--verbose", "--name", f"dispatch-{ref}"]
    if cfg.use_systemd and shutil.which("systemd-run"):
        cmd = ["systemd-run", "--user", "--scope", "--quiet", "-p", f"MemoryHigh={cfg.memory_high}", "-p", f"MemoryMax={cfg.memory_max}", *cmd]
    env = dict(os.environ, KATA_AUTHOR=actor, KATA_DISPATCH_MAIN_CHECKOUT=str(paths.repo))
    with open(log, "ab") as logf, open(run_dir / f"{ref}.stderr", "ab") as errf:
        proc = subprocess.Popen(cmd, cwd=str(wt), env=env, stdin=subprocess.DEVNULL, stdout=logf, stderr=errf)
    rec = AgentRecord(ref=ref, actor=actor, run_id=run_id, branch=branch, worktree=str(wt), log=str(log), pid=proc.pid)
    rec.save(paths.agent(ref))
    return rec, proc


def parse_result(log_path: Path) -> dict:
    out = {"outcome": "unknown", "label": "", "cost_usd": 0.0, "session_id": "", "subtype": "", "note": ""}
    try:
        lines = log_path.read_text().splitlines()
    except FileNotFoundError:
        return out
    for line in reversed(lines):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") != "result":
            continue
        out["cost_usd"] = float(d.get("total_cost_usd") or 0.0)
        out["session_id"] = d.get("session_id", "")
        out["subtype"] = d.get("subtype", "")
        text = d.get("result") or ""
        # An ambiguous result -- more than one OUTCOME line that don't all agree -- must fail
        # closed to unknown rather than pick whichever regex match happened to be found first
        # (re.search stops at the first match, silently preferring an earlier, possibly quoted
        # or hypothetical, OUTCOME line over the worker's actual final answer).
        matches = list(re.finditer(r"^[\s`*_>]*OUTCOME:\s*([A-Za-z-]+)(?:\s+([\w-]+))?", text, re.M))
        if matches:
            words = {m.group(1).lower() for m in matches}
            if len(words) == 1:
                m = matches[0]
                out["outcome"] = m.group(1).lower()
                if out["outcome"] == "escalated":
                    out["label"] = m.group(2) or ""
            else:
                out["outcome"] = "unknown"
                out["label"] = ""
                out["note"] = "ambiguous OUTCOME lines"
        break
    return out
