import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from test_kata_dispatch_fakes import install_fake_kata, make_repo  # noqa: E402

from kata_dispatch import integrate, landing, state  # noqa: E402


def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def _land_something(paths):
    iw = paths.integration_worktree
    (iw / "new.txt").write_text("hi\n")
    subprocess.run(["git", "add", "new.txt"], cwd=iw, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "landed"], cwd=iw, check=True)


def test_green_tests_fast_forward_main(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    _land_something(paths)
    ok, msg = integrate.integrate(paths, "test -f new.txt")
    assert ok, msg
    assert _git(["rev-parse", "main"], repo) == _git(["rev-parse", "integration"], repo)
    assert (repo / "new.txt").exists()


def test_red_tests_leave_main_alone(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    _land_something(paths)
    before = _git(["rev-parse", "main"], repo)
    ok, msg = integrate.integrate(paths, "echo BOOM; false")
    assert not ok and "BOOM" in msg
    assert _git(["rev-parse", "main"], repo) == before


def test_rebases_onto_moved_main(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    _land_something(paths)
    (repo / "main-moved.txt").write_text("m\n")
    subprocess.run(["git", "add", "main-moved.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "main moved"], cwd=repo, check=True)
    ok, msg = integrate.integrate(paths, "test -f new.txt && test -f main-moved.txt")
    assert ok, msg
    assert _git(["log", "--oneline", "main"], repo).count("\n") == 2   # init, main moved, landed


def test_refuses_while_agents_active(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    rec = state.AgentRecord(ref="a", actor="x", run_id="r", branch="dispatch/a", worktree="", log="", pid=os.getpid())
    rec.save(paths.agent("a"))
    ok, msg = integrate.integrate(paths, "true")
    assert not ok and "active" in msg
