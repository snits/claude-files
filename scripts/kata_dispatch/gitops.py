"""Thin git helpers. Every call names its cwd explicitly; nothing inherits a shell cd."""
import subprocess
from pathlib import Path


def git(args, cwd, check=True) -> subprocess.CompletedProcess:
    # stdin=DEVNULL: git subcommands that fall back to reading stdin (or a pager/editor that
    # does) must never inherit the dispatcher's, which may be an open pipe that never closes.
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=check,
                          stdin=subprocess.DEVNULL)


def rev_parse(cwd, what: str) -> str:
    return git(["rev-parse", what], cwd).stdout.strip()


def current_branch(cwd) -> str:
    return git(["rev-parse", "--abbrev-ref", "HEAD"], cwd).stdout.strip()


def is_clean(cwd) -> bool:
    return git(["status", "--porcelain"], cwd).stdout.strip() == ""


def branch_exists(repo, branch: str) -> bool:
    return git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], repo, check=False).returncode == 0


def commits_ahead(repo, base: str, branch: str) -> int:
    return int(git(["rev-list", "--count", f"{base}..{branch}"], repo).stdout.strip())


def diff_empty(repo, a: str, b: str) -> bool:
    return git(["diff", "--quiet", a, b], repo, check=False).returncode == 0


def worktree_add(repo, path: Path, branch: str, start_point: str, new_branch: bool = True):
    args = ["worktree", "add"]
    if new_branch:
        args += ["-b", branch, str(path), start_point]
    else:
        args += [str(path), branch]
    git(args, repo)


def worktree_remove(repo, path: Path, force: bool = False):
    args = ["worktree", "remove"]
    if force:
        args.append("--force")
    git(args + [str(path)], repo)
    git(["worktree", "prune"], repo)


def branch_delete_merged(repo, branch: str) -> bool:
    """-d, never -D: refuses an unmerged branch, which is the guard."""
    return git(["branch", "-d", branch], repo, check=False).returncode == 0


def last_commit(cwd, ref: str = "HEAD") -> tuple[int, str]:
    out = git(["log", "-1", "--format=%ct%x00%h (\"%s\")", ref], cwd, check=False).stdout.strip()
    if not out:
        return 0, ""
    ts, cite = out.split("\x00", 1)
    return int(ts), cite


def cite(cwd, ref: str) -> str:
    return git(["show", "-s", "--format=%h (\"%s\")", ref], cwd).stdout.strip()
