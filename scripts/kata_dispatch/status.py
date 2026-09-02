"""What each agent is doing, and whether it has gone quiet."""
import os
import time
from dataclasses import dataclass
from pathlib import Path

from . import gitops
from .state import AgentRecord, Paths, pid_alive

STALL_SECONDS = 600


@dataclass
class Row:
    ref: str
    actor: str
    branch: str
    worktree: str
    last_commit: str
    idle_s: int
    state: str
    flag: str


def _idle(rec: AgentRecord, repo: Path, now: float) -> tuple[int, str]:
    ts, cite = 0, ""
    if gitops.branch_exists(repo, rec.branch):
        ts, cite = gitops.last_commit(repo, rec.branch)
        # No integration branch yet (e.g. status run before setup) means no ahead-count to
        # compute -- treat that the same as "0 ahead": base commit only, not worker activity.
        if not gitops.branch_exists(repo, "integration") or gitops.commits_ahead(repo, "integration", rec.branch) == 0:
            cite, ts = f"(none yet) base {cite}", 0      # the base commit is not worker activity
    try:
        log_ts = os.stat(rec.log).st_mtime
    except FileNotFoundError:
        log_ts = 0
    latest = max(ts, log_ts, rec.started)
    return int(now - latest), cite


def rows(paths: Paths, now: float | None = None) -> list[Row]:
    now = now or time.time()
    out = []
    for rec in AgentRecord.load_all(paths):
        idle, cite = _idle(rec, paths.repo, now)
        flag = ""
        if rec.state == "running":
            if not pid_alive(rec.pid):
                flag = "DEAD"
            elif idle > STALL_SECONDS:
                flag = "STALLED"
        out.append(Row(rec.ref, rec.actor, rec.branch, rec.worktree, cite, idle, rec.state, flag))
    return out


def render(rs: list[Row]) -> str:
    if not rs:
        return "no agents recorded"
    hdr = f"{'ref':6} {'state':10} {'idle':>7} {'flag':8} {'branch':16} last commit"
    lines = [hdr, "-" * len(hdr)]
    for r in rs:
        idle = f"{r.idle_s // 60}m{r.idle_s % 60:02d}s"
        lines.append(f"{r.ref:6} {r.state:10} {idle:>7} {r.flag:8} {r.branch:16} {r.last_commit}")
    return "\n".join(lines)
