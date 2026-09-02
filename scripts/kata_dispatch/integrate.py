"""Reviewer pass: with every agent idle, rebase integration onto main, run the suite, ff main."""
import subprocess
import time

from . import gitops
from .landing import ensure_integration
from .state import AgentRecord, Paths, pid_alive


def _active(paths: Paths) -> list[str]:
    out = []
    for rec in AgentRecord.load_all(paths):
        if rec.state == "landing" or (rec.state == "running" and pid_alive(rec.pid)):
            out.append(rec.ref)
    return out


def integrate(paths: Paths, test_cmd: str, target: str = "integration") -> tuple[bool, str]:
    active = _active(paths)
    if active:
        return False, f"agents still active: {', '.join(active)}"
    ensure_integration(paths, target)
    iw = paths.integration_worktree
    if not gitops.is_clean(paths.repo):
        return False, "main checkout is dirty"
    rb = gitops.git(["rebase", "main"], iw, check=False)
    if rb.returncode != 0:
        gitops.git(["rebase", "--abort"], iw, check=False)
        return False, f"rebase of {target} onto main conflicts:\n{rb.stderr.strip()[-800:]}"
    logdir = paths.repo / ".scratchpad" / "tmp" / "dispatch"
    logdir.mkdir(parents=True, exist_ok=True)
    log = logdir / f"integrate-{int(time.time())}.log"
    p = subprocess.run(["bash", "-c", test_cmd], cwd=str(iw), capture_output=True, text=True)
    log.write_text(p.stdout + p.stderr)
    if p.returncode != 0:
        tail = (p.stdout + p.stderr).strip().splitlines()[-30:]
        return False, f"tests failed ({p.returncode}); log {log}\n" + "\n".join(tail)
    ff = gitops.git(["merge", "--ff-only", target], paths.repo, check=False)
    if ff.returncode != 0:
        return False, f"ff-only merge into main failed: {ff.stderr.strip()}"
    return True, f"main now at {gitops.cite(paths.repo, 'main')}; tests green, log {log}"
