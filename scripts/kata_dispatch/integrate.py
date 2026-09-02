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
    if not gitops.is_clean(paths.repo):
        return False, "main checkout is dirty"
    iw = paths.integration_worktree
    if iw.is_dir():
        # This worktree is dispatcher-owned and ephemeral; a prior red test run may have left
        # build artifacts (tracked-file edits, untracked junk) behind. Reset it before
        # ensure_integration's is_clean(iw) check runs, so a dirty leftover never blocks the
        # next attempt.
        gitops.git(["checkout", "--", "."], iw, check=False)
        gitops.git(["clean", "-fdx"], iw, check=False)
    try:
        ensure_integration(paths, target)
    except (RuntimeError, subprocess.CalledProcessError, OSError) as e:
        return False, f"integration worktree not usable: {e}"
    rb = gitops.git(["rebase", "main"], iw, check=False)
    if rb.returncode != 0:
        gitops.git(["rebase", "--abort"], iw, check=False)
        return False, f"rebase of {target} onto main conflicts:\n{rb.stderr.strip()[-800:]}"
    logdir = paths.repo / ".scratchpad" / "tmp" / "dispatch"
    logdir.mkdir(parents=True, exist_ok=True)
    log = logdir / f"integrate-{int(time.time())}.log"
    p = subprocess.run(["bash", "-c", test_cmd], cwd=str(iw), stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, text=True)
    log.write_text(p.stdout)
    if p.returncode != 0:
        tail = p.stdout.strip().splitlines()[-30:]
        return False, f"tests failed ({p.returncode}); log {log}\n" + "\n".join(tail)
    ff = gitops.git(["merge", "--ff-only", target], paths.repo, check=False)
    if ff.returncode != 0:
        return False, f"ff-only merge into main failed: {ff.stderr.strip()}"
    return True, f"main now at {gitops.cite(paths.repo, 'main')}; tests green, log {log}"
