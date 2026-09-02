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


def test_rebase_onto_moved_main_preserves_merge_commits(tmp_path, monkeypatch):
    """Everything land() puts on integration is a --no-ff merge commit. A plain `git rebase`
    flattens them; --rebase-merges keeps them, so `git log --merges main` still shows which
    branch each change arrived on."""
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    iw = paths.integration_worktree
    subprocess.run(["git", "checkout", "-q", "-b", "feat"], cwd=iw, check=True)
    (iw / "feat.txt").write_text("f\n")
    subprocess.run(["git", "add", "feat.txt"], cwd=iw, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat work"], cwd=iw, check=True)
    subprocess.run(["git", "checkout", "-q", "integration"], cwd=iw, check=True)
    subprocess.run(["git", "merge", "--no-ff", "-q", "-m", "Merge dispatch/feat", "feat"], cwd=iw, check=True)
    # main moves, forcing a real rebase rather than a fast-forward
    (repo / "main-moved.txt").write_text("m\n")
    subprocess.run(["git", "add", "main-moved.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "main moved"], cwd=repo, check=True)
    ok, msg = integrate.integrate(paths, "test -f feat.txt && test -f main-moved.txt")
    assert ok, msg
    assert "Merge dispatch/feat" in _git(["log", "--merges", "--format=%s", "main"], repo)


def test_refuses_while_agents_active(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    rec = state.AgentRecord(ref="a", actor="x", run_id="r", branch="dispatch/a", worktree="", log="", pid=os.getpid())
    rec.save(paths.agent("a"))
    ok, msg = integrate.integrate(paths, "true")
    assert not ok and "active" in msg


def test_dirty_main_refuses_before_mutating(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure()
    # make_repo() pre-creates "integration" for other tests' convenience; drop it here so this
    # test can prove integrate() never (re)creates it when main is dirty.
    subprocess.run(["git", "branch", "-D", "integration"], cwd=repo, check=True)
    (repo / "dirty.txt").write_text("uncommitted\n")
    ok, msg = integrate.integrate(paths, "true")
    assert not ok and msg == "main checkout is dirty"
    branches = _git(["branch", "--list", "integration"], repo)
    assert branches == ""


def test_dirty_integration_worktree_is_reset_between_runs(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    _land_something(paths)
    ok, msg = integrate.integrate(paths, "touch junk.txt; false")
    assert not ok, msg
    assert (paths.integration_worktree / "junk.txt").exists()
    ok, msg = integrate.integrate(paths, "test ! -e junk.txt")
    assert ok, msg
    assert not (paths.integration_worktree / "junk.txt").exists()


def test_integration_worktree_on_wrong_branch_reported_not_usable(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    subprocess.run(["git", "checkout", "-b", "other"], cwd=paths.integration_worktree, check=True)
    ok, msg = integrate.integrate(paths, "true")
    assert not ok
    assert "not usable" in msg


def test_integration_worktree_stray_directory_reported_not_usable(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure()
    paths.integration_worktree.mkdir(parents=True, exist_ok=True)
    ok, msg = integrate.integrate(paths, "true")
    assert not ok
    assert "not usable" in msg


def test_integration_worktree_stray_file_reported_not_usable(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure()
    paths.integration_worktree.parent.mkdir(parents=True, exist_ok=True)
    paths.integration_worktree.write_text("not a worktree\n")
    ok, msg = integrate.integrate(paths, "true")
    assert not ok
    assert "not usable" in msg


def test_rebase_conflict_leaves_main_and_worktree_clean(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch)
    paths = state.Paths(repo); paths.ensure(); landing.ensure_integration(paths)
    iw = paths.integration_worktree
    (iw / "src" / "app.py").write_text("def main():\n    return 'integration'\n")
    subprocess.run(["git", "add", "src/app.py"], cwd=iw, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "integration edit"], cwd=iw, check=True)
    (repo / "src" / "app.py").write_text("def main():\n    return 'main'\n")
    subprocess.run(["git", "add", "src/app.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "main edit"], cwd=repo, check=True)
    before = _git(["rev-parse", "main"], repo)
    ok, msg = integrate.integrate(paths, "true")
    assert not ok
    assert "conflicts" in msg
    assert _git(["rev-parse", "main"], repo) == before
    rebase_path = subprocess.run(
        ["git", "rev-parse", "--git-path", "rebase-merge"], cwd=iw, capture_output=True, text=True, check=True
    ).stdout.strip()
    assert not (iw / rebase_path).exists()
