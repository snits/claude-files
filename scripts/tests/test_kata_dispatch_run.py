import os
import signal
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
from test_kata_dispatch_fakes import install_fake_claude, install_fake_kata, make_repo  # noqa: E402

from kata_dispatch import run, state  # noqa: E402
from kata_dispatch.kata import KataClient  # noqa: E402

# a fake worker that commits a file named after FAKE_REF, sleeping so overlap gating is observable
FAKE_CLAUDE_SLOW = r'''#!/usr/bin/env python3
import json, os, subprocess, sys, time
ref = os.environ["KATA_AUTHOR"].rsplit("-", 1)[-1]
time.sleep(float(os.environ.get("FAKE_SLEEP", "1")))
open(ref + ".txt", "w").write(ref)
subprocess.run(["git", "add", ref + ".txt"], check=True)
subprocess.run(["git", "commit", "-q", "-s", "-m", "feat: " + ref], check=True)
print(json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 0.2, "is_error": False, "session_id": "s-" + ref, "result": "OUTCOME: reviewed-branch"}))
'''

ISSUES = [
    {"short_id": "a1", "title": "edit src/app.py", "body": "change src/app.py"},
    {"short_id": "b2", "title": "also src/app.py", "body": "conflicts with a1 on src/app.py"},
    {"short_id": "c3", "title": "edit README.md", "body": "README.md wording"},
    {"short_id": "d4", "title": "Decide something", "body": "no files", "labels": ["needs-decision"]},
    {"short_id": "e5", "title": "edit src/util.py", "body": "src/util.py"},
]


def _opts(**kw):
    base = dict(agents=2, cap=8, model="sonnet", budget_usd=1.0, gate=False, poll_s=0.2, use_systemd=False, run_id="t1")
    base.update(kw)
    return run.Options(**base)


def test_run_lands_all_dispatchable_issues_and_never_overlaps(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    st = install_fake_kata(tmp_path, monkeypatch, ISSUES)
    install_fake_claude(tmp_path, monkeypatch, FAKE_CLAUDE_SLOW)
    paths = state.Paths(repo); paths.ensure()
    recs = run.run(paths, KataClient(repo), _opts())
    by = {r.ref: r for r in recs}
    assert set(by) == {"a1", "b2", "c3", "e5"} and all(r.state == "done" for r in recs)
    # a1 and b2 share src/app.py: the second must have started after the first finished
    assert by["b2"].started >= by["a1"].finished or by["a1"].started >= by["b2"].finished
    log = subprocess.run(["git", "log", "--format=%s", "integration"], cwd=repo, capture_output=True, text=True).stdout
    assert log.count("Merge dispatch/") == 4
    assert not any(paths.worktree(r).exists() for r in by)
    assert all(KataClient(repo).owner(r) is None for r in by)
    ledger = next((repo / ".scratchpad").glob("*-dispatch-t1-ledger.md"))
    text = ledger.read_text()
    assert "d4" in text and "label:needs-decision" in text and "issues/hour" in text
    assert "a1" in text and "merged" in text


def test_run_respects_cap_and_explicit_issue_list(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, ISSUES)
    install_fake_claude(tmp_path, monkeypatch, FAKE_CLAUDE_SLOW)
    paths = state.Paths(repo); paths.ensure()
    recs = run.run(paths, KataClient(repo), _opts(cap=1, issues=["c3", "e5"]))
    assert [r.ref for r in recs] == ["c3"]


def test_run_refuses_dirty_main_checkout(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, ISSUES)
    (repo / "dirty.txt").write_text("x")
    paths = state.Paths(repo); paths.ensure()
    try:
        run.run(paths, KataClient(repo), _opts())
    except RuntimeError as e:
        assert "clean" in str(e)
    else:
        raise AssertionError("expected RuntimeError on dirty tree")


def test_plan_prints_predictions(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, ISSUES)
    paths = state.Paths(repo); paths.ensure()
    text = run.plan(paths, KataClient(repo))
    assert "a1" in text and "src/app.py" in text and "d4" in text and "*" in text


def test_cli_status_and_reap_run(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, ISSUES)
    cli = Path(__file__).resolve().parent.parent / "kata-dispatch"
    p = subprocess.run([sys.executable, str(cli), "status", "--repo", str(repo)], capture_output=True, text=True)
    assert p.returncode == 0 and "no agents" in p.stdout
    p = subprocess.run([sys.executable, str(cli), "reap", "--repo", str(repo)], capture_output=True, text=True)
    assert p.returncode == 0
    p = subprocess.run([sys.executable, str(cli), "preflight"], capture_output=True, text=True, cwd=repo)
    assert p.returncode == 2


def test_run_landing_exception_is_isolated_and_run_continues(tmp_path, monkeypatch):
    """Orchestrator amendment 2: a landing.land exception on one ref must not kill the run,
    must leave that ref blocked with its claim released, and must not stop other refs from
    landing normally."""
    from kata_dispatch import landing as landing_mod

    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, ISSUES)
    install_fake_claude(tmp_path, monkeypatch, FAKE_CLAUDE_SLOW)
    paths = state.Paths(repo); paths.ensure()

    orig_land = landing_mod.land

    def boom(paths_, rec, kata_, gate_fn, target, gate_model):
        if rec.ref == "a1":
            raise RuntimeError("kaboom")
        return orig_land(paths_, rec, kata_, gate_fn, target, gate_model)

    monkeypatch.setattr(run.landing, "land", boom)
    recs = run.run(paths, KataClient(repo), _opts(issues=["a1", "c3"], agents=1))
    by = {r.ref: r for r in recs}
    assert by["a1"].state == "blocked" and "landing raised" in by["a1"].outcome
    assert by["c3"].state == "done"
    assert KataClient(repo).owner("a1") is None
    # A landing that raised must also be visible in kata, or the next run picks the issue up
    # as if nothing had ever touched it.
    assert "needs-review" in KataClient(repo).labels("a1")


def test_run_survives_a_spawn_failure_after_the_claim(tmp_path, monkeypatch):
    """worker.spawn raising after claims.acquire must not kill the run or leak the claim. A
    pre-existing dispatch/c3 branch makes `git worktree add -b` fail for exactly one ref; with
    the bug the exception escapes run() entirely and e5 never lands."""
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, ISSUES)
    install_fake_claude(tmp_path, monkeypatch, FAKE_CLAUDE_SLOW)
    subprocess.run(["git", "branch", "dispatch/c3", "integration"], cwd=repo, check=True)
    paths = state.Paths(repo); paths.ensure()
    recs = run.run(paths, KataClient(repo), _opts(issues=["c3", "e5"], agents=1))
    by = {r.ref: r for r in recs}
    assert "c3" not in by, "a never-spawned ref is not a dispatched agent"
    assert by["e5"].state == "done", "the other ref must still land"
    kata = KataClient(repo)
    assert kata.owner("c3") is None and not paths.lock("c3").exists(), "claim must be released"
    ledger = next((repo / ".scratchpad").glob("*-dispatch-t1-ledger.md")).read_text()
    assert "c3" in ledger and "spawn failed" in ledger


# Commits immediately (so the dispatcher has something to keep), then sleeps long enough that
# a SIGINT sent to the dispatcher must interrupt it -- if the dispatcher didn't stop and
# terminate the worker, the test would have to wait out the sleep.
FAKE_CLAUDE_COMMIT_THEN_SLEEP = r'''#!/usr/bin/env python3
import json, os, subprocess, sys, time
ref = os.environ["KATA_AUTHOR"].rsplit("-", 1)[-1]
open(ref + ".txt", "w").write(ref)
subprocess.run(["git", "add", ref + ".txt"], check=True)
subprocess.run(["git", "commit", "-q", "-s", "-m", "feat: " + ref], check=True)
time.sleep(60)
print(json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 0.2, "is_error": False, "session_id": "s-" + ref, "result": "OUTCOME: reviewed-branch"}))
'''

_DISPATCH_IN_SUBPROCESS = '''
import sys
sys.path.insert(0, {scripts_dir!r})
from pathlib import Path
from kata_dispatch import run, state
from kata_dispatch.kata import KataClient
paths = state.Paths(Path({repo!r}))
paths.ensure()
kata = KataClient(paths.repo)
opts = run.Options(agents=1, cap=8, model="sonnet", budget_usd=1.0, gate=False, poll_s=0.2,
                    use_systemd=False, run_id="sigtest", issues=["e5"])
run.run(paths, kata, opts)
'''


def test_sigint_stops_the_run_and_terminates_the_worker(tmp_path, monkeypatch):
    """C1/C2/C3/I4: a SIGINT while a worker is active must break the loop even though the
    worker is still running, terminate that worker, and land it as blocked-with-worktree-kept
    rather than losing the ledger or the claim. Runs the dispatcher in a real subprocess so a
    real signal is delivered to the main thread that installed the handler."""
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, ISSUES)
    install_fake_claude(tmp_path, monkeypatch, FAKE_CLAUDE_COMMIT_THEN_SLEEP)
    paths = state.Paths(repo); paths.ensure()

    code = _DISPATCH_IN_SUBPROCESS.format(scripts_dir=str(SCRIPTS_DIR), repo=str(repo))
    dispatcher = subprocess.Popen([sys.executable, "-c", code], cwd=str(repo), env=dict(os.environ))

    rec_path = paths.agent("e5")

    def _committed():
        if not rec_path.exists():
            return False
        log = subprocess.run(["git", "log", "--oneline", "dispatch/e5"], cwd=repo, capture_output=True, text=True)
        return log.returncode == 0 and "feat: e5" in log.stdout

    deadline = time.time() + 20
    while time.time() < deadline and not _committed():
        time.sleep(0.1)
    assert _committed(), "worker never committed before the deadline"

    rec_before = state.AgentRecord.load(rec_path)
    dispatcher.send_signal(signal.SIGINT)
    try:
        dispatcher.wait(timeout=30)
    except subprocess.TimeoutExpired:
        dispatcher.kill()
        raise AssertionError("dispatcher did not exit within 30s of SIGINT")

    assert not state.pid_alive(rec_before.pid)
    rec_after = state.AgentRecord.load(rec_path)
    assert rec_after.state == "blocked"
    assert paths.worktree("e5").exists()
    kata = KataClient(repo)
    assert "needs-review" in kata.labels("e5")
    assert kata.owner("e5") is None
    assert not paths.lock("e5").exists()
    ledger = next((repo / ".scratchpad").glob("*-dispatch-sigtest-ledger.md"))
    assert ledger.exists()
