import json
import multiprocessing as mp
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from test_kata_dispatch_fakes import install_fake_kata, kata_calls, make_repo  # noqa: E402

from kata_dispatch import claims, state  # noqa: E402
from kata_dispatch.kata import KataClient  # noqa: E402

ISSUE = {"short_id": "ab12", "title": "fix thing", "body": "touch src/app.py"}


def test_acquire_takes_lock_and_kata_claim(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    st = install_fake_kata(tmp_path, monkeypatch, [ISSUE])
    paths = state.Paths(repo)
    paths.ensure()
    k = KataClient(repo)
    assert claims.acquire(paths, "ab12", "claude-dispatch-r1-ab12", k) is True
    lock = json.loads(paths.lock("ab12").read_text())
    assert lock["actor"] == "claude-dispatch-r1-ab12" and lock["pid"] == os.getpid()
    assert k.owner("ab12") == "claude-dispatch-r1-ab12"
    assert ["claim", "ab12", "--as", "claude-dispatch-r1-ab12"] in kata_calls(st)


def test_acquire_fails_when_kata_owned_by_other_and_unwinds_lock(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [ISSUE])
    subprocess.run(["kata", "claim", "ab12", "--as", "someone-else"], check=True, capture_output=True)
    paths = state.Paths(repo)
    paths.ensure()
    assert claims.acquire(paths, "ab12", "claude-dispatch-r1-ab12", KataClient(repo)) is False
    assert not paths.lock("ab12").exists()
    assert KataClient(repo).owner("ab12") == "someone-else"


def test_acquire_rolls_back_kata_claim_when_readback_raises(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [ISSUE])
    paths = state.Paths(repo)
    paths.ensure()
    k = KataClient(repo)

    from kata_dispatch.kata import KataError

    def boom(self, ref):
        raise KataError("read-back exploded")

    with pytest.MonkeyPatch.context() as mp_ctx:
        mp_ctx.setattr(KataClient, "owner", boom)
        with pytest.raises(KataError):
            claims.acquire(paths, "ab12", "claude-dispatch-r1-ab12", k)

    assert not paths.lock("ab12").exists()
    assert KataClient(repo).owner("ab12") is None


def test_release_only_unassigns_own_claim(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [ISSUE])
    paths = state.Paths(repo)
    paths.ensure()
    k = KataClient(repo)
    subprocess.run(["kata", "claim", "ab12", "--as", "someone-else"], check=True, capture_output=True)
    paths.lock("ab12").write_text(json.dumps({"actor": "me", "pid": 1, "host": "h", "started": 0}))
    claims.release(paths, "ab12", "me", k)
    assert not paths.lock("ab12").exists()
    assert k.owner("ab12") == "someone-else"        # not ours, so not unassigned


def _racer(args):
    repo, ref, actor, env = args
    os.environ.update(env)
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from kata_dispatch import claims, state
    from kata_dispatch.kata import KataClient
    paths = state.Paths(Path(repo))
    return actor, claims.acquire(paths, ref, actor, KataClient(Path(repo)))


def test_race_sixteen_claimers_one_winner(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    st = install_fake_kata(tmp_path, monkeypatch, [ISSUE])
    state.Paths(repo).ensure()
    env = {"PATH": os.environ["PATH"], "KATA_FAKE_DIR": os.environ["KATA_FAKE_DIR"]}
    actors = [f"claude-dispatch-r{i}-ab12" for i in range(16)]
    with mp.get_context("spawn").Pool(16) as pool:
        results = pool.map(_racer, [(str(repo), "ab12", a, env) for a in actors])
    winners = [a for a, ok in results if ok]
    assert len(winners) == 1, results
    assert KataClient(repo).owner("ab12") == winners[0]
    assert sum(1 for c in kata_calls(st) if c[0] == "claim") == 1, "lock file must stop losers before kata"


def test_stale_lock_detected_by_dead_pid(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [ISSUE])
    paths = state.Paths(repo)
    paths.ensure()
    paths.lock("ab12").write_text(json.dumps({"actor": "dead", "pid": 2**22 - 1, "host": os.uname().nodename, "started": 0}))
    paths.lock("zz99").write_text(json.dumps({"actor": "live", "pid": os.getpid(), "host": os.uname().nodename, "started": 0}))
    stale = claims.stale_locks(paths)
    assert [s["ref"] for s in stale] == ["ab12"]


def test_ready_returns_issues_list(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [ISSUE, {"short_id": "cd34", "title": "other", "body": "b"}])
    k = KataClient(repo)
    refs = {i["short_id"] for i in k.ready()}
    assert refs == {"ab12", "cd34"}


def test_labels_from_show(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [
        {"short_id": "ab12", "title": "t", "body": "b", "labels": ["needs-review", "retitle"]},
        {"short_id": "cd34", "title": "t2", "body": "b2"},
    ])
    k = KataClient(repo)
    assert k.labels("ab12") == {"needs-review", "retitle"}
    assert k.labels("cd34") == set()


def test_comment_and_label_add_call_fake(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    st = install_fake_kata(tmp_path, monkeypatch, [ISSUE])
    k = KataClient(repo)
    k.comment("ab12", "claude-dispatch-r1-ab12", "hello there")
    k.label_add("ab12", "claude-dispatch-r1-ab12", "needs-review")
    calls = kata_calls(st)
    assert ["comment", "ab12", "--body", "hello there", "--as", "claude-dispatch-r1-ab12"] in calls
    assert ["label", "add", "ab12", "needs-review", "--as", "claude-dispatch-r1-ab12"] in calls


def test_is_epic_open_child(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [{
        "short_id": "ab12", "title": "epic", "body": "b",
        "links": [{"type": "parent", "from": {"short_id": "kid1", "status": "open"}, "to": {"short_id": "ab12", "status": "open"}}],
    }])
    assert KataClient(repo).is_epic("ab12") is True


def test_is_epic_closed_child(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [{
        "short_id": "ab12", "title": "epic", "body": "b",
        "links": [{"type": "parent", "from": {"short_id": "kid1", "status": "closed"}, "to": {"short_id": "ab12", "status": "open"}}],
    }])
    assert KataClient(repo).is_epic("ab12") is False


def test_is_epic_link_for_other_ref(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [{
        "short_id": "ab12", "title": "epic", "body": "b",
        "links": [{"type": "parent", "from": {"short_id": "kid1", "status": "open"}, "to": {"short_id": "zz99", "status": "open"}}],
    }])
    assert KataClient(repo).is_epic("ab12") is False


@pytest.mark.skipif(not os.environ.get("KATA_DISPATCH_LIVE"), reason="set KATA_DISPATCH_LIVE=1 to race real kata")
def test_live_kata_race_eight_actors(tmp_path):
    """Races the real daemon. Creates a probe issue in the cwd project and purges it after."""
    repo = Path(os.environ.get("KATA_DISPATCH_LIVE_REPO", os.path.expanduser("~/claudes-home")))
    out = subprocess.run(["kata", "create", "kata-dispatch live race probe (purge me)", "--json", "--as", "claude-dispatch-probe"],
                         cwd=repo, capture_output=True, text=True, check=True)
    ref = json.loads(out.stdout)["issue"]["short_id"]
    project = json.loads(out.stdout)["issue"].get("qualified_id", "").split("#")[0] or "claudes-home"
    try:
        actors = [f"claude-dispatch-live{i}-{ref}" for i in range(8)]
        procs = [subprocess.Popen(["kata", "claim", ref, "--as", a], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for a in actors]
        codes = [p.wait() for p in procs]
        assert codes.count(0) == 1 and codes.count(5) == 7, codes
        owner = json.loads(subprocess.run(["kata", "show", "--json", ref], cwd=repo, capture_output=True, text=True).stdout)["issue"].get("owner")
        assert owner == actors[codes.index(0)]
    finally:
        subprocess.run(["kata", "purge", ref, "--force", "--confirm", f"PURGE {project}#{ref}", "--reason", "kata-dispatch live race test"], cwd=repo, capture_output=True)
