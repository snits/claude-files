"""Tests for the git surgery guard PreToolUse hook.

Each test builds a real throwaway repo (tmp_path) and feeds the hook the same
JSON Claude Code would send. Assertions check exit code AND that block messages
carry the recovery command — the message is part of the contract.
"""
import json
import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / "git_surgery_guard.py"


def run_hook(command: str, cwd: Path):
    payload = json.dumps(
        {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd)}
    )
    return subprocess.run(
        ["python3", str(HOOK)], input=payload, capture_output=True, text=True
    )


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(r)], check=True)
    git(r, "commit", "--allow-empty", "-m", "one")
    git(r, "commit", "--allow-empty", "-m", "two")
    return r


class TestDetachedHeadEntry:
    def test_checkout_sha_blocked(self, repo):
        sha = git(repo, "rev-parse", "HEAD~1")
        res = run_hook(f"git checkout {sha}", repo)
        assert res.returncode == 2
        assert "git switch -c" in res.stderr

    def test_switch_detach_blocked(self, repo):
        res = run_hook("git switch --detach HEAD~1", repo)
        assert res.returncode == 2

    def test_checkout_branch_allowed(self, repo):
        git(repo, "branch", "feature")
        assert run_hook("git checkout feature", repo).returncode == 0

    def test_checkout_dash_b_allowed(self, repo):
        assert run_hook("git checkout -b topic HEAD~1", repo).returncode == 0

    def test_checkout_pathspec_allowed(self, repo):
        assert run_hook("git checkout HEAD~1 -- file.txt", repo).returncode == 0


class TestAlreadyDetached:
    @pytest.fixture
    def detached(self, repo):
        subprocess.run(
            ["git", "-C", str(repo), "checkout", "-q", "--detach", "HEAD~1"],
            check=True,
        )
        return repo

    def test_commit_blocked_with_rescue(self, detached):
        res = run_hook("git commit -m x", detached)
        assert res.returncode == 2
        assert "rescue/" in res.stderr

    def test_reset_blocked(self, detached):
        assert run_hook("git reset --hard HEAD~1", detached).returncode == 2

    def test_readonly_allowed(self, detached):
        assert run_hook("git log --oneline", detached).returncode == 0
        assert run_hook("git reflog", detached).returncode == 0
        assert run_hook("git status", detached).returncode == 0

    def test_bisect_carveout(self, detached):
        gd = Path(git(detached, "rev-parse", "--absolute-git-dir"))
        (gd / "BISECT_LOG").write_text("")
        assert run_hook("git checkout HEAD~1", detached).returncode == 0


class TestStgClause:
    @pytest.fixture
    def stg_repo(self, repo):
        subprocess.run(["stg", "-C", str(repo), "init"], check=True)
        return repo

    def test_raw_commit_blocked(self, stg_repo):
        res = run_hook("git commit -m x", stg_repo)
        assert res.returncode == 2
        assert "stg repair" in res.stderr

    def test_raw_rebase_blocked(self, stg_repo):
        assert run_hook("git rebase main", stg_repo).returncode == 2

    def test_stg_commands_allowed(self, stg_repo):
        assert run_hook("stg new -m msg p1", stg_repo).returncode == 0
        assert run_hook("stg refresh", stg_repo).returncode == 0

    def test_branch_switch_allowed(self, stg_repo):
        git(stg_repo, "branch", "other")
        assert run_hook("git checkout other", stg_repo).returncode == 0

    def test_non_stg_branch_unaffected(self, repo):
        assert run_hook("git commit --allow-empty -m x", repo).returncode == 0


class TestClassifierRobustness:
    def test_non_git_command_allowed(self, repo):
        assert run_hook("ls -la", repo).returncode == 0

    def test_compound_command_second_segment_blocked(self, repo):
        sha = git(repo, "rev-parse", "HEAD~1")
        res = run_hook(f"git status && git checkout {sha}", repo)
        assert res.returncode == 2

    def test_git_dash_c_repo_targeting(self, repo, tmp_path):
        sha = git(repo, "rev-parse", "HEAD~1")
        res = run_hook(f"git -C {repo} checkout {sha}", tmp_path)
        assert res.returncode == 2

    def test_unparseable_command_allowed(self, repo):
        assert run_hook("git checkout $(broken 'quote", repo).returncode == 0

    def test_outside_any_repo_allowed(self, tmp_path):
        assert run_hook("git checkout deadbeef", tmp_path).returncode == 0
