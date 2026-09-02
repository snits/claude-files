import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from test_kata_dispatch_fakes import install_fake_kata, make_repo  # noqa: E402

from kata_dispatch import claims, landing, reap, state, status  # noqa: E402
from kata_dispatch.kata import KataClient, KataError  # noqa: E402

DEAD = 2**22 - 1


def _record(paths, ref, pid, started=None, commit=False):
    wt = paths.worktree(ref)
    subprocess.run(["git", "worktree", "add", "-q", "-b", f"dispatch/{ref}", str(wt), "integration"], cwd=paths.repo, check=True)
    if commit:
        (wt / "f.txt").write_text("x")
        subprocess.run(["git", "add", "f.txt"], cwd=wt, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "work"], cwd=wt, check=True)
    log = paths.run_dir("r1") / f"{ref}.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("{}\n")
    rec = state.AgentRecord(ref=ref, actor=f"claude-dispatch-r1-{ref}", run_id="r1", branch=f"dispatch/{ref}", worktree=str(wt), log=str(log), pid=pid, started=started or time.time())
    rec.save(paths.agent(ref))
    return rec


def test_status_flags_stalled_and_dead(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    live = _record(paths, "aaaa", os.getpid())
    old = time.time() - 1000
    stale = _record(paths, "bbbb", os.getpid(), started=old)
    os.utime(stale.log, (old, old))
    dead = _record(paths, "cccc", DEAD)
    rows = {r.ref: r for r in status.rows(paths)}
    assert rows["aaaa"].flag == "" and rows["aaaa"].idle_s < 60
    assert rows["bbbb"].flag == "STALLED" and rows["bbbb"].idle_s >= 600
    assert rows["cccc"].flag == "DEAD"
    text = status.render(list(rows.values()))
    assert "STALLED" in text and "dispatch/bbbb" in text and "cccc" in text


def test_idle_uses_latest_of_commit_and_log(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    rec = _record(paths, "aaaa", os.getpid(), commit=True)
    old = time.time() - 5000
    os.utime(rec.log, (old, old))
    r = status.rows(paths)[0]
    assert r.idle_s < 60 and r.last_commit.endswith('("work")')


def test_reap_orphaned_with_commits_is_kept_and_labeled(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    st = install_fake_kata(tmp_path, monkeypatch, [{"short_id": "aaaa", "title": "t", "body": "b"}])
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    k = KataClient(repo)
    assert claims.acquire(paths, "aaaa", "claude-dispatch-r1-aaaa", k)
    rec = _record(paths, "aaaa", DEAD, commit=True)
    lines = reap.reap(paths, k)
    assert any("aaaa" in l and "kept" in l for l in lines)
    assert Path(rec.worktree).exists()
    assert "needs-review" in k.labels("aaaa") and k.owner("aaaa") is None and not paths.lock("aaaa").exists()
    assert state.AgentRecord.load(paths.agent("aaaa")).state == "orphaned"


def test_reap_orphaned_without_commits_is_removed(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [{"short_id": "aaaa", "title": "t", "body": "b"}])
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    k = KataClient(repo)
    assert claims.acquire(paths, "aaaa", "claude-dispatch-r1-aaaa", k)
    rec = _record(paths, "aaaa", DEAD)
    reap.reap(paths, k)
    assert not Path(rec.worktree).exists()
    assert subprocess.run(["git", "branch", "--list", "dispatch/aaaa"], cwd=repo, capture_output=True, text=True).stdout == ""
    assert k.owner("aaaa") is None


def test_reap_recovers_record_stuck_in_landing(tmp_path, monkeypatch):
    """A dispatcher that died mid-land leaves state=="landing". Before the fix reap skipped
    anything not "running", so the branch, worktree and claim were stranded with nothing left
    to recover them."""
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [{"short_id": "aaaa", "title": "t", "body": "b"}])
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    k = KataClient(repo)
    assert claims.acquire(paths, "aaaa", "claude-dispatch-r1-aaaa", k)
    rec = _record(paths, "aaaa", DEAD, commit=True)
    rec.state = "landing"
    rec.save(paths.agent("aaaa"))
    lock = json.loads(paths.lock("aaaa").read_text())
    lock["pid"] = DEAD                       # the dispatcher that was landing is gone
    paths.lock("aaaa").write_text(json.dumps(lock))
    lines = reap.reap(paths, k)
    assert any("aaaa" in l and "kept" in l for l in lines), lines
    assert Path(rec.worktree).exists()
    assert "needs-review" in k.labels("aaaa") and k.owner("aaaa") is None and not paths.lock("aaaa").exists()
    assert state.AgentRecord.load(paths.agent("aaaa")).state == "orphaned"


def test_reap_leaves_a_live_landing_alone(tmp_path, monkeypatch):
    """The other direction, and the one that costs a worktree if the fix reads the wrong pid:
    during a healthy landing the worker has already exited, so rec.pid is dead by construction.
    Only the lock's pid (the dispatcher's) says whether the landing is still in progress."""
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [{"short_id": "aaaa", "title": "t", "body": "b"}])
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    k = KataClient(repo)
    assert claims.acquire(paths, "aaaa", "claude-dispatch-r1-aaaa", k)   # lock pid == os.getpid()
    rec = _record(paths, "aaaa", DEAD, commit=True)
    rec.state = "landing"
    rec.save(paths.agent("aaaa"))
    assert json.loads(paths.lock("aaaa").read_text())["pid"] == os.getpid()
    lines = reap.reap(paths, k)
    assert lines == [], lines
    assert Path(rec.worktree).exists() and paths.lock("aaaa").exists()
    assert k.owner("aaaa") == "claude-dispatch-r1-aaaa"
    assert state.AgentRecord.load(paths.agent("aaaa")).state == "landing"


def test_reap_stale_lock_without_record_respects_foreign_owner(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [{"short_id": "aaaa", "title": "t", "body": "b"}])
    paths = state.Paths(repo); paths.ensure()
    k = KataClient(repo)
    subprocess.run(["kata", "claim", "aaaa", "--as", "human"], check=True, capture_output=True)
    paths.lock("aaaa").write_text(json.dumps({"actor": "claude-dispatch-r0-aaaa", "pid": DEAD, "host": os.uname().nodename, "started": 0}))
    reap.reap(paths, k)
    assert not paths.lock("aaaa").exists() and k.owner("aaaa") == "human"


def test_reap_leaves_live_agents_alone(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [{"short_id": "aaaa", "title": "t", "body": "b"}])
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    k = KataClient(repo)
    assert claims.acquire(paths, "aaaa", "claude-dispatch-r1-aaaa", k)
    rec = _record(paths, "aaaa", os.getpid())
    reap.reap(paths, k)
    assert Path(rec.worktree).exists() and k.owner("aaaa") == "claude-dispatch-r1-aaaa"


def test_reap_stale_lock_owner_lookup_failure_leaves_claim_alone(tmp_path, monkeypatch):
    """A kata.owner() failure on the stale-lock path must never fall through to unassigning --
    claims.release's lookup-failure fallback calls `kata unassign` unconditionally, and that
    succeeds for any actor. Simulate the failure and confirm the foreign claim survives."""
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [{"short_id": "aaaa", "title": "t", "body": "b"}])
    paths = state.Paths(repo); paths.ensure()
    k = KataClient(repo)
    subprocess.run(["kata", "claim", "aaaa", "--as", "human"], check=True, capture_output=True)
    paths.lock("aaaa").write_text(json.dumps({"actor": "claude-dispatch-r0-aaaa", "pid": DEAD, "host": os.uname().nodename, "started": 0}))
    orig_owner = KataClient.owner

    def raising_owner(self, ref):
        if ref == "aaaa":
            raise KataError("simulated show failure")
        return orig_owner(self, ref)

    with monkeypatch.context() as m:
        m.setattr(KataClient, "owner", raising_owner)
        lines = reap.reap(paths, k)
    assert not paths.lock("aaaa").exists()
    assert any("aaaa" in l and "left alone" in l for l in lines)
    # Fresh, unpatched client: the foreign claim must still stand.
    assert KataClient(repo).owner("aaaa") == "human"


def test_reap_no_commits_branch_delete_refused_surfaces_in_outcome(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [{"short_id": "aaaa", "title": "t", "body": "b"}])
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    k = KataClient(repo)
    assert claims.acquire(paths, "aaaa", "claude-dispatch-r1-aaaa", k)
    _record(paths, "aaaa", DEAD)
    monkeypatch.setattr(reap.gitops, "branch_delete_merged", lambda repo, branch: False)
    lines = reap.reap(paths, k)
    saved = state.AgentRecord.load(paths.agent("aaaa"))
    assert "branch -d refused" in saved.outcome
    assert any("aaaa" in l and "refused" in l for l in lines)


def test_reap_no_commits_worktree_dir_already_removed(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [{"short_id": "aaaa", "title": "t", "body": "b"}])
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    k = KataClient(repo)
    assert claims.acquire(paths, "aaaa", "claude-dispatch-r1-aaaa", k)
    rec = _record(paths, "aaaa", DEAD)
    shutil.rmtree(rec.worktree)
    lines = reap.reap(paths, k)
    assert subprocess.run(["git", "branch", "--list", "dispatch/aaaa"], cwd=repo, capture_output=True, text=True).stdout == ""
    assert any("aaaa" in l and "removed" in l for l in lines)


def test_status_rows_without_integration_branch(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    _record(paths, "aaaa", os.getpid())
    subprocess.run(["git", "worktree", "remove", "--force", str(paths.integration_worktree)], cwd=repo, check=True)
    subprocess.run(["git", "branch", "-D", "integration"], cwd=repo, check=True)
    rows = status.rows(paths)
    assert len(rows) == 1
