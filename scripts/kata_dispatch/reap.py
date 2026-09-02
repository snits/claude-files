"""Clean up after a crashed dispatcher or a dead worker, keeping anything that has commits.

Release-first ordering (orchestrate-issues rule, applied here per the Task 7 review): every
cleanup path releases the claim before touching kata labels/comments or the worktree/branch,
and each later call is wrapped so a failure lands in rec.outcome as text rather than raising --
a raised exception mid-cleanup would otherwise leak the claim and lock.
"""
from pathlib import Path

from . import claims, gitops, landing
from .kata import KataClient
from .state import AgentRecord, Paths, pid_alive


def _record_failure(rec: AgentRecord, what: str, err: Exception):
    rec.outcome = f"{rec.outcome}; {what} failed: {err}"


def reap(paths: Paths, kata: KataClient, target: str = "integration") -> list[str]:
    landing.ensure_integration(paths, target)
    report = []
    seen = set()
    for rec in AgentRecord.load_all(paths):
        seen.add(rec.ref)
        if rec.state != "running" or pid_alive(rec.pid):
            continue
        rec.state = "orphaned"
        wt = Path(rec.worktree)
        ahead = gitops.commits_ahead(paths.repo, target, rec.branch) if gitops.branch_exists(paths.repo, rec.branch) else 0

        # Release first: claims.release never raises, so the claim and lock are gone before
        # any of the kata/git calls below get a chance to fail mid-cleanup.
        claims.release(paths, rec.ref, rec.actor, kata)

        if ahead > 0:
            rec.outcome = f"worker died with {ahead} commit(s); worktree kept"
            try:
                if "needs-review" not in kata.labels(rec.ref):
                    kata.label_add(rec.ref, rec.actor, "needs-review")
            except Exception as e:
                _record_failure(rec, "kata label", e)
            try:
                kata.comment(rec.ref, rec.actor, f"kata-dispatch reap: {rec.outcome} at {wt}")
            except Exception as e:
                _record_failure(rec, "kata comment", e)
            report.append(f"{rec.ref}: kept {wt} ({ahead} commits), labeled needs-review")
        else:
            # Set the optimistic outcome first: _record_failure appends onto rec.outcome, so a
            # teardown failure must land as an addition to this text, never get clobbered by it.
            rec.outcome = "worker died with no commits; worktree removed"
            try:
                if wt.exists():
                    gitops.worktree_remove(paths.repo, wt, force=True)
                elif gitops.branch_exists(paths.repo, rec.branch):
                    # Worktree dir is already gone (e.g. removed by hand) but git still has it
                    # registered -- prune the stale registration before touching the branch.
                    gitops.git(["worktree", "prune"], paths.repo, check=False)
            except Exception as e:
                _record_failure(rec, "teardown", e)
            try:
                # branch -d judges "merged" against the cwd checkout's HEAD; main has not seen
                # these commits, integration has -- same fix as landing._teardown (Task 7).
                if not gitops.branch_delete_merged(paths.integration_worktree, rec.branch):
                    rec.outcome += "; branch -d refused"
            except Exception as e:
                _record_failure(rec, "teardown", e)
            if "failed" in rec.outcome or "refused" in rec.outcome:
                report.append(f"{rec.ref}: {rec.outcome}")
            else:
                report.append(f"{rec.ref}: removed empty worktree and branch")
        rec.save(paths.agent(rec.ref))

    for lock in claims.stale_locks(paths):
        if lock["ref"] in seen:
            continue
        try:
            owner = kata.owner(lock["ref"])
        except Exception:
            owner = None
        # Branch on the owner we just looked up, never route through claims.release here:
        # its lookup-failure fallback calls `kata unassign` unconditionally, and `kata unassign`
        # succeeds for any actor (verified 2026-09-01) -- safe only when we provably hold the
        # claim, which an owner()-raise or owner-mismatch means we do not.
        if owner == lock["actor"]:
            claims.release(paths, lock["ref"], lock["actor"], kata)
            report.append(f"{lock['ref']}: stale lock (pid {lock['pid']} dead), claim released")
        else:
            paths.lock(lock["ref"]).unlink(missing_ok=True)
            report.append(f"{lock['ref']}: stale lock removed; kata owner is {owner!r}, left alone")
    return report
