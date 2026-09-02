"""Run /verify-branch headlessly from the primary checkout and read its artifacts, fail closed.

The skill writes `<primary>/.scratchpad/{YYYYMMDD}-verify-branch-{auditor}-{branch}.md`, each
ending in `VERDICT: PASS|BLOCK`. Three auditors. A missing artifact or a missing VERDICT line
is a BLOCK recorded as "no verdict", never a pass.
"""
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

AUDITORS = 3
VERDICT_RE = re.compile(r"^VERDICT:\s*(PASS|BLOCK)\s*$", re.M)


@dataclass
class Verdict:
    passed: bool
    detail: str
    artifacts: list = field(default_factory=list)


def NO_GATE(*args, **kwargs) -> Verdict:
    return Verdict(True, "gate disabled", [])


def _artifacts_since(repo: Path, ref: str, branch: str, since: float) -> list[Path]:
    d = repo / ".scratchpad"
    if not d.is_dir():
        return []
    keys = {branch, branch.replace("/", "-")}
    out = []
    for p in d.glob("*verify-branch*.md"):
        # No slop on the mtime window: mtime resolution here is sub-millisecond (measured),
        # so no buffer is needed, and any widening would admit a prior run's overwritten
        # artifact for the same branch. Fail closed instead — a borderline timestamp reads
        # as missing, not as a stale pass.
        if p.stat().st_mtime >= since and any(k in p.name for k in keys):
            out.append(p)
    return sorted(out)


BUDGET_USD = 15.0     # per gate session; three auditors run inside it


def run_gate(repo, ref: str, branch: str, target: str, model: str, log_path: Path,
             budget_usd: float = BUDGET_USD, timeout: int = 3600) -> Verdict:
    # budget_usd sits after log_path so landing.land's six positional args are unaffected; an
    # ungated session can outspend the whole run's worker budget on one branch. Exceeding it
    # exits non-zero, which the returncode check below already turns into a fail-closed BLOCK.
    repo = Path(repo)
    started = time.time()
    prompt = f"/verify-branch {target} kata#{ref} {branch}"
    with open(log_path, "ab") as logf:
        p = subprocess.run(["claude", "-p", prompt, "--model", model, "--max-budget-usd", str(budget_usd),
                            "--permission-mode", "bypassPermissions",
                            "--output-format", "stream-json", "--verbose", "--name", f"gate-{ref}"],
                           cwd=str(repo), stdin=subprocess.DEVNULL, stdout=logf, stderr=subprocess.STDOUT, timeout=timeout)
    arts = _artifacts_since(repo, ref, branch, started)
    verdicts = {}
    for a in arts:
        m = VERDICT_RE.findall(a.read_text(errors="replace"))
        verdicts[a.name] = m[-1] if m else None
    missing = [n for n, v in verdicts.items() if v is None]
    if p.returncode != 0:
        return Verdict(False, f"gate session exited {p.returncode}: no verdict", [str(a) for a in arts])
    if len(arts) < AUDITORS or missing:
        return Verdict(False, f"gate returned no verdict ({len(arts)}/{AUDITORS} artifacts, {len(missing)} without VERDICT)", [str(a) for a in arts])
    blocks = [n for n, v in verdicts.items() if v == "BLOCK"]
    if blocks:
        return Verdict(False, "BLOCK from " + ", ".join(blocks), [str(a) for a in arts])
    return Verdict(True, "PASS from all auditors", [str(a) for a in arts])
