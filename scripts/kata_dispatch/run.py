"""The dispatcher loop: fill free slots with non-overlapping issues, land finished workers, write a ledger."""
import os
import signal
import time
from dataclasses import dataclass
from pathlib import Path

from . import claims, gate, gitops, landing, scheduler, surface, worker
from .kata import KataClient
from .state import AgentRecord, Paths, pid_alive
from .status import STALL_SECONDS, rows


@dataclass
class Options:
    agents: int = 4
    cap: int = 8
    model: str = "opus"
    budget_usd: float = 25.0
    gate: bool = True
    gate_model: str = "opus"
    poll_s: float = 15.0
    issues: list | None = None
    use_systemd: bool = True
    stall_action: str = "report"     # report | kill
    run_id: str | None = None
    target: str = "integration"


def _candidates(paths: Paths, kata: KataClient, only: list | None):
    ready = kata.ready()
    if only:
        order = {r: i for i, r in enumerate(only)}
        ready = sorted([i for i in ready if i["short_id"] in order], key=lambda i: order[i["short_id"]])
    return scheduler.candidates_from_ready(ready, surface_fn=lambda t, b: surface.predict(paths.repo, t, b), epic_fn=kata.is_epic)


def plan(paths: Paths, kata: KataClient, only: list | None = None) -> str:
    lines = [f"{'ref':6} {'labels':22} surface"]
    for c in _candidates(paths, kata, only):
        surf = "*" if c.surface == surface.WILDCARD else ", ".join(sorted(c.surface))
        lines.append(f"{c.ref:6} {','.join(sorted(c.labels)):22} {surf}")
    return "\n".join(lines)


def _record_failure(rec: AgentRecord, what: str, err: Exception):
    rec.outcome = f"{rec.outcome}; {what} failed: {err}"


def _land_safe(paths: Paths, rec: AgentRecord, kata: KataClient, gate_fn, target: str, gate_model: str) -> AgentRecord:
    """Wrap landing.land: an exception there must never kill the run loop or leave a live-pid
    lock behind -- record it as a blocked outcome, release the claim (robust after Task 8), and
    hand the record back so the caller can keep going."""
    try:
        return landing.land(paths, rec, kata, gate_fn, target, gate_model)
    except Exception as e:
        rec.state, rec.outcome = "blocked", f"landing raised: {e!r}"
        claims.release(paths, rec.ref, rec.actor, kata)
        rec.save(paths.agent(rec.ref))
        return rec


def run(paths: Paths, kata: KataClient, opts: Options) -> list[AgentRecord]:
    if not gitops.is_clean(paths.repo):
        raise RuntimeError(f"main checkout {paths.repo} is not clean; refusing to dispatch")
    if not kata.healthy():
        raise RuntimeError("kata daemon is not healthy")
    paths.ensure()
    landing.ensure_integration(paths, opts.target)
    run_id = opts.run_id or time.strftime("%m%d%H%M")
    cfg = worker.Config(model=opts.model, budget_usd=opts.budget_usd, use_systemd=opts.use_systemd)
    gate_fn = gate.run_gate if opts.gate else gate.NO_GATE
    t0 = time.time()
    active: dict[str, tuple[AgentRecord, object, frozenset]] = {}
    finished: list[AgentRecord] = []
    skipped: dict[str, str] = {}
    dispatched = 0
    stop = {"flag": False}

    def _sig(*_):
        stop["flag"] = True
    old = (signal.signal(signal.SIGINT, _sig), signal.signal(signal.SIGTERM, _sig))
    try:
        while True:
            for ref in list(active):
                rec, proc, surf = active[ref]
                if proc.poll() is None:
                    continue
                del active[ref]
                finished.append(_land_safe(paths, rec, kata, gate_fn, opts.target, opts.gate_model))
            if opts.stall_action == "kill":
                for r in rows(paths):
                    if r.flag == "STALLED" and r.ref in active:
                        active[r.ref][1].terminate()
            if not stop["flag"]:
                while len(active) < opts.agents and dispatched < opts.cap:
                    cands = _candidates(paths, kata, opts.issues)
                    exclude = set(active) | {r.ref for r in finished}
                    pick, sk = scheduler.pick(cands, [s for _, _, s in active.values()], exclude)
                    for ref, why in sk:
                        if ref not in exclude:
                            skipped[ref] = why
                    if pick is None:
                        break
                    actor = f"claude-dispatch-{run_id}-{pick.ref}"
                    if not claims.acquire(paths, pick.ref, actor, kata):
                        skipped[pick.ref] = "claim lost"
                        finished.append(AgentRecord(ref=pick.ref, actor=actor, run_id=run_id, branch="", worktree="", log="", state="skipped", outcome="claim lost"))
                        continue
                    rec, proc = worker.spawn(paths, pick.ref, actor, run_id, cfg, opts.target)
                    active[pick.ref] = (rec, proc, pick.surface)
                    dispatched += 1
                    skipped.pop(pick.ref, None)
            if not active and (stop["flag"] or dispatched >= opts.cap or scheduler.pick(_candidates(paths, kata, opts.issues), [], {r.ref for r in finished})[0] is None):
                break
            time.sleep(opts.poll_s)
    finally:
        signal.signal(signal.SIGINT, old[0]); signal.signal(signal.SIGTERM, old[1])
        if active:
            for ref, (rec, proc, _) in active.items():
                proc.terminate()
            for ref, (rec, proc, _) in active.items():
                try:
                    proc.wait(timeout=30)
                except Exception:
                    proc.kill()
                finished.append(_land_safe(paths, rec, kata, gate.NO_GATE, opts.target, opts.gate_model) if gitops.commits_ahead(paths.repo, opts.target, rec.branch) == 0
                                else _abandon(paths, rec, kata))
        _ledger(paths, run_id, finished, skipped, t0, opts)
    return [r for r in finished if r.state != "skipped"]


def _abandon(paths: Paths, rec: AgentRecord, kata: KataClient) -> AgentRecord:
    """Cleanup for a worker interrupted mid-run with commits already made. Release-first
    (Task 7 review ordering, applied here per the Task 10 orchestrator amendment): the claim
    and lock are gone before any kata label/comment call gets a chance to fail mid-cleanup, and
    each of those later calls is wrapped so a failure lands in rec.outcome as text rather than
    raising."""
    rec.state, rec.outcome = "blocked", "dispatcher stopped while worker had commits; worktree kept"
    claims.release(paths, rec.ref, rec.actor, kata)
    try:
        if "needs-review" not in kata.labels(rec.ref):
            kata.label_add(rec.ref, rec.actor, "needs-review")
    except Exception as e:
        _record_failure(rec, "kata label", e)
    try:
        kata.comment(rec.ref, rec.actor, f"kata-dispatch run {rec.run_id}: {rec.outcome} at {rec.worktree}")
    except Exception as e:
        _record_failure(rec, "kata comment", e)
    rec.save(paths.agent(rec.ref))
    return rec


def _ledger(paths: Paths, run_id: str, finished: list[AgentRecord], skipped: dict, t0: float, opts: Options):
    wall = time.time() - t0
    real = [r for r in finished if r.state != "skipped"]
    merged = [r for r in real if r.state == "done"]
    nochange = [r for r in real if r.state == "no-change"]
    esc = [r for r in real if r.state in ("escalated", "blocked")]
    per_issue = sum((r.finished or time.time()) - r.started for r in real)
    lines = [f"# kata-dispatch ledger — run {run_id}", "",
             f"repo {paths.repo}; agents {opts.agents}; cap {opts.cap}; model {opts.model}; gate {'on' if opts.gate else 'off'}", "",
             "| ref | state | outcome | merge commit | wall clock | cost USD |", "|---|---|---|---|---|---|"]
    for r in real:
        mins = ((r.finished or time.time()) - r.started) / 60
        lines.append(f"| {r.ref} | {r.state} | {r.outcome} | {r.merge_commit} | {mins:.1f} min | {r.cost_usd:.2f} |")
    for ref, why in skipped.items():
        if ref not in {r.ref for r in real}:
            lines.append(f"| {ref} | skipped | {why} | | | |")
    rate = f"{len(esc)}/{len(real)}" if real else "0/0"
    lines += ["", f"- dispatched: {len(real)}; merged: {len(merged)}; no-change: {len(nochange)}; escalated or blocked: {len(esc)}; escalation rate: {rate}",
              f"- run wall clock: {wall / 60:.1f} min; sum of per-issue wall clocks: {per_issue / 60:.1f} min; speedup: {per_issue / wall if wall else 0:.2f}x",
              f"- throughput: {len(merged) / (wall / 3600):.2f} issues/hour landed" if wall else "- throughput: n/a",
              f"- worker cost (self-reported by claude -p): ${sum(r.cost_usd for r in real):.2f}"]
    out = paths.repo / ".scratchpad" / f"{time.strftime('%Y%m%d')}-dispatch-{run_id}-ledger.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
