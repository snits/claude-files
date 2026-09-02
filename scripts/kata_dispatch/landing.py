"""Land one finished worker: rebase inside its worktree, gate, --no-ff merge into integration.

Order is fixed (orchestrate-issues rules): rebase, then gate the post-rebase diff, then merge
from the integration worktree. Conflicts are never resolved here. A branch that fails to land
keeps its worktree; a branch with nothing to land loses it.
"""
import time
from pathlib import Path

from . import claims, gitops
from .kata import KataClient
from .state import AgentRecord, Paths
from .worker import parse_result


def ensure_integration(paths: Paths, target: str = "integration"):
    repo = paths.repo
    if not gitops.branch_exists(repo, target):
        gitops.git(["branch", target, "main"], repo)
    iw = paths.integration_worktree
    if not iw.exists():
        iw.parent.mkdir(parents=True, exist_ok=True)
        gitops.worktree_add(repo, iw, target, target, new_branch=False)
    if gitops.current_branch(iw) != target:
        raise RuntimeError(f"{iw} is on {gitops.current_branch(iw)}, expected {target}")
    if not gitops.is_clean(iw):
        raise RuntimeError(f"integration worktree {iw} is dirty")


def _escalate(paths: Paths, rec: AgentRecord, kata: KataClient, label: str, why: str, keep_worktree: bool):
    try:
        if label and label not in kata.labels(rec.ref):
            kata.label_add(rec.ref, rec.actor, label)
        kata.comment(rec.ref, rec.actor, f"kata-dispatch run {rec.run_id}: {why}")
    finally:
        if not keep_worktree:
            _teardown(paths, rec)
        claims.release(paths, rec.ref, rec.actor, kata)


def _teardown(paths: Paths, rec: AgentRecord):
    wt = Path(rec.worktree)
    if wt.exists():
        gitops.worktree_remove(paths.repo, wt, force=True)
    # `branch -d`'s merged-into-HEAD check is relative to the cwd's checked-out branch; the
    # primary checkout stays on main, but the merge landed on integration, so the check must
    # run from the integration worktree or an unmerged-looking dispatch branch never deletes.
    gitops.branch_delete_merged(paths.integration_worktree, rec.branch)


def land(paths: Paths, rec: AgentRecord, kata: KataClient, gate_fn, target: str = "integration", gate_model: str = "opus") -> AgentRecord:
    repo = paths.repo
    rec.state = "landing"
    rec.finished = time.time()
    result = parse_result(Path(rec.log))
    rec.cost_usd, rec.session_id = result["cost_usd"], result["session_id"]
    rec.save(paths.agent(rec.ref))
    wt = Path(rec.worktree)

    ahead = gitops.commits_ahead(repo, target, rec.branch) if gitops.branch_exists(repo, rec.branch) else 0
    if ahead == 0:
        label = result["label"] if result["outcome"] == "escalated" else ""
        rec.state = "no-change" if result["outcome"] == "no-change" else "escalated"
        rec.outcome = f"{result['outcome']} {label}".strip() if result["outcome"] != "unknown" else f"no commits, worker ended {result['subtype'] or 'without result'}"
        _escalate(paths, rec, kata, label, rec.outcome, keep_worktree=False)
        rec.save(paths.agent(rec.ref))
        return rec

    if not gitops.is_clean(wt):
        rec.state, rec.outcome = "blocked", "worktree left dirty by worker"
        _escalate(paths, rec, kata, "needs-review", rec.outcome, keep_worktree=True)
        rec.save(paths.agent(rec.ref)); return rec

    rb = gitops.git(["rebase", target], wt, check=False)
    if rb.returncode != 0:
        gitops.git(["rebase", "--abort"], wt, check=False)
        rec.state, rec.outcome = "blocked", f"rebase onto {target} conflicts: {rb.stderr.strip()[:300]}"
        _escalate(paths, rec, kata, "needs-review", rec.outcome, keep_worktree=True)
        rec.save(paths.agent(rec.ref)); return rec

    verdict = gate_fn(repo, rec.ref, rec.branch, target, gate_model, paths.run_dir(rec.run_id) / f"{rec.ref}.gate.jsonl")
    if not verdict.passed:
        rec.state, rec.outcome = "blocked", f"gate: {verdict.detail}"
        _escalate(paths, rec, kata, "needs-review", rec.outcome + "; artifacts: " + ", ".join(verdict.artifacts), keep_worktree=True)
        rec.save(paths.agent(rec.ref)); return rec

    iw = paths.integration_worktree
    m = gitops.git(["merge", "--no-ff", "--signoff", "-m", f"Merge {rec.branch} (kata#{rec.ref})", rec.branch], iw, check=False)
    if m.returncode != 0:
        gitops.git(["merge", "--abort"], iw, check=False)
        rec.state, rec.outcome = "blocked", f"merge failed: {m.stderr.strip()[:300]}"
        _escalate(paths, rec, kata, "needs-review", rec.outcome, keep_worktree=True)
        rec.save(paths.agent(rec.ref)); return rec

    if gitops.commits_ahead(repo, target, rec.branch) != 0 or not gitops.diff_empty(repo, target, rec.branch):
        rec.state, rec.outcome = "blocked", "landing verification failed: branch not fully contained in integration"
        _escalate(paths, rec, kata, "needs-review", rec.outcome, keep_worktree=True)
        rec.save(paths.agent(rec.ref)); return rec

    rec.merge_commit = gitops.cite(repo, target)
    rec.state, rec.outcome = "done", "merged"
    kata.comment(rec.ref, rec.actor, f"kata-dispatch run {rec.run_id}: landed on {target} as {rec.merge_commit}; gate: {verdict.detail}")
    _teardown(paths, rec)
    claims.release(paths, rec.ref, rec.actor, kata)
    rec.save(paths.agent(rec.ref))
    return rec
