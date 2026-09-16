"""Tests for the destructive-restore guard.

No mocks for the git half: _dirty and verdict run against a real temporary repo, because
the whole point of the guard is the dirty/clean distinction and a mocked git could not
tell us whether we are asking git the right question.
"""
import io
import json
import subprocess

import pytest

from restore_guard import _destructive, main, verdict


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "tracked.txt").write_text("original\n")
    (tmp_path / "clean.txt").write_text("clean\n")
    sub = tmp_path / "src"
    sub.mkdir()
    (sub / "a.rs").write_text("fn a() {}\n")
    git(tmp_path, "add", "tracked.txt", "clean.txt", "src/a.rs")
    git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def dirty(repo):
    (repo / "tracked.txt").write_text("UNCOMMITTED WORK\n")


# --- the hazard: blocked only when work would actually be lost -------------------------

def test_checkout_dashdash_on_dirty_path_blocks(repo):
    dirty(repo)
    assert verdict("git checkout -- tracked.txt", str(repo)) is not None


def test_checkout_dashdash_on_clean_path_allows(repo):
    dirty(repo)
    assert verdict("git checkout -- clean.txt", str(repo)) is None


def test_checkout_dot_on_dirty_tree_blocks(repo):
    """`git checkout .` is the shape that cost ~200 lines in alexandria yq0n."""
    dirty(repo)
    assert verdict("git checkout .", str(repo)) is not None


def test_checkout_dot_on_clean_tree_allows(repo):
    assert verdict("git checkout .", str(repo)) is None


def test_git_restore_on_dirty_path_blocks(repo):
    dirty(repo)
    assert verdict("git restore tracked.txt", str(repo)) is not None


def test_restore_staged_checks_the_index_not_the_worktree(repo):
    """--staged discards staged work; an unstaged-only change is not what it destroys."""
    dirty(repo)
    assert verdict("git restore --staged tracked.txt", str(repo)) is None
    git(repo, "add", "tracked.txt")
    assert verdict("git restore --staged tracked.txt", str(repo)) is not None


def test_checkout_treeish_with_dirty_index_blocks(repo):
    """`git checkout HEAD -- f` destroys staged work too, so the index is checked."""
    dirty(repo)
    git(repo, "add", "tracked.txt")
    assert verdict("git checkout HEAD -- tracked.txt", str(repo)) is not None


def test_directory_pathspec_blocks_when_a_file_under_it_is_dirty(repo):
    (repo / "src" / "a.rs").write_text("MID-TASK WORK\n")
    assert verdict("git checkout -- src", str(repo)) is not None


# --- things that must never be blocked -------------------------------------------------

def test_branch_switch_is_not_a_pathspec(repo):
    git(repo, "branch", "feature")
    dirty(repo)
    assert verdict("git checkout feature", str(repo)) is None


def test_checkout_b_new_branch_allows(repo):
    dirty(repo)
    assert verdict("git checkout -b newbranch", str(repo)) is None


def test_git_status_allows(repo):
    dirty(repo)
    assert verdict("git status", str(repo)) is None


def test_unrelated_command_allows(repo):
    dirty(repo)
    assert verdict("echo git checkout -- tracked.txt", str(repo)) is None


def test_outside_a_git_repo_allows(tmp_path):
    assert verdict("git checkout -- anything.txt", str(tmp_path)) is None


# --- parsing reuse: the shapes claim_gate already knows how to see ----------------------

def test_hidden_in_bash_dash_c_blocks(repo):
    dirty(repo)
    assert verdict("bash -c 'git checkout -- tracked.txt'", str(repo)) is not None


def test_second_segment_of_a_compound_blocks(repo):
    dirty(repo)
    assert verdict("git status && git checkout -- tracked.txt", str(repo)) is not None


def test_inside_a_heredoc_body_is_data_not_a_command(repo):
    dirty(repo)
    assert verdict("cat <<EOF\ngit checkout -- tracked.txt\nEOF", str(repo)) is None


def test_quoted_argument_is_not_a_command(repo):
    dirty(repo)
    assert verdict('kata comment abc4 --body "do not run git checkout -- tracked.txt"',
                   str(repo)) is None


# --- pure parsing ----------------------------------------------------------------------

def test_destructive_ignores_non_git(tmp_path):
    assert _destructive(["rm", "-rf", "x"], str(tmp_path)) is None


def test_destructive_requires_paths(tmp_path):
    assert _destructive(["git", "checkout", "--"], str(tmp_path)) is None


# --- hook protocol ---------------------------------------------------------------------

def test_main_exits_2_and_writes_stderr_when_blocking(repo):
    dirty(repo)
    payload = json.dumps({"tool_input": {"command": "git checkout -- tracked.txt"},
                          "cwd": str(repo)})
    err = io.StringIO()
    assert main(stdin=io.StringIO(payload), stderr=err) == 2
    assert "BLOCKED" in err.getvalue()
    assert "git stash push" in err.getvalue()


def test_main_exits_0_when_clean(repo):
    payload = json.dumps({"tool_input": {"command": "git checkout -- tracked.txt"},
                          "cwd": str(repo)})
    err = io.StringIO()
    assert main(stdin=io.StringIO(payload), stderr=err) == 0
    assert err.getvalue() == ""


def test_main_survives_garbage_stdin():
    assert main(stdin=io.StringIO("not json"), stderr=io.StringIO()) == 0


# --- git must be the command, not merely a word (regression) ---------------------------

def test_git_as_an_argument_to_another_program_allows(repo):
    """`echo git checkout -- f` runs nothing; blocking it would be a false block."""
    dirty(repo)
    assert verdict("echo git checkout -- tracked.txt", str(repo)) is None


def test_env_assignment_prefix_still_blocks(repo):
    dirty(repo)
    assert verdict("GIT_AUTHOR_NAME=x git checkout -- tracked.txt", str(repo)) is not None


def test_absolute_git_path_still_blocks(repo):
    dirty(repo)
    assert verdict("/usr/bin/git checkout -- tracked.txt", str(repo)) is not None


def test_grep_for_the_phrase_allows(repo):
    dirty(repo)
    assert verdict("grep -rn 'git checkout --' docs/", str(repo)) is None


# --- git global options before the subcommand (regression: the live run missed these) ---

def test_git_dash_C_blocks_and_checks_that_repo(repo, tmp_path):
    """`git -C <repo> checkout -- f` must block, and must inspect <repo>, not cwd."""
    dirty(repo)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    assert verdict(f"git -C {repo} checkout -- tracked.txt", str(elsewhere)) is not None


def test_git_dash_C_on_clean_repo_allows(repo, tmp_path):
    elsewhere = tmp_path / "elsewhere2"
    elsewhere.mkdir()
    assert verdict(f"git -C {repo} checkout -- tracked.txt", str(elsewhere)) is None


def test_git_dash_c_config_before_subcommand_blocks(repo):
    dirty(repo)
    assert verdict("git -c core.pager=cat checkout -- tracked.txt", str(repo)) is not None


def test_git_work_tree_flag_before_subcommand_blocks(repo):
    dirty(repo)
    assert verdict(f"git --work-tree {repo} checkout -- tracked.txt", str(repo)) is not None


def test_git_dash_C_relative_path_blocks(repo):
    dirty(repo)
    assert verdict("git -C . checkout -- tracked.txt", str(repo)) is not None
