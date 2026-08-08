#!/usr/bin/env python3
# ~/.claude/scripts/git_surgery_guard.py
"""PreToolUse guard for Bash git commands.

Blocks (exit 2, reason on stderr):
  1. Commands that would ENTER detached HEAD (checkout <non-branch>, switch --detach).
  2. Mutating git commands while ALREADY detached (rescue procedure in message).
  3. Raw-git mutations on an stgit-managed branch (silent stack desync).

Never blocks read-only commands. On any parse/classification failure: allow —
the PostToolUse desync detector is the safety net.
"""
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

MUTATING = {
    "commit", "checkout", "switch", "reset", "rebase", "am",
    "apply", "merge", "cherry-pick", "revert",
}
# checkout/switch to another branch is safe on an stg branch; the stack refs stay put.
STG_UNSAFE = {"commit", "rebase", "reset", "cherry-pick", "am", "merge", "revert"}


def git(repo, *args):
    """Run git, return (rc, stdout). Never raises."""
    try:
        p = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, timeout=5,
        )
        return p.returncode, p.stdout.strip()
    except Exception:
        return 1, ""


def split_segments(command):
    """Split a shell command on ;, &&, ||, | into token lists. None if unparseable."""
    try:
        parts = re.split(r"(?<!\|)\|\|(?!\|)|&&|;|\|", command)
        return [shlex.split(p) for p in parts if p.strip()]
    except ValueError:
        return None


def parse_git_invocation(tokens, cwd):
    """Return (repo_dir, subcommand, args) for a git segment, else None."""
    if not tokens or Path(tokens[0]).name != "git":
        return None
    repo = cwd
    i = 1
    while i < len(tokens):
        t = tokens[i]
        if t == "-C" and i + 1 < len(tokens):
            repo = tokens[i + 1]
            i += 2
        elif t == "-c" and i + 1 < len(tokens):
            i += 2
        elif t.startswith("--git-dir") or t.startswith("--work-tree") or t.startswith("-"):
            i += 1
        else:
            return repo, t, tokens[i + 1:]
    return None


def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def is_local_branch(repo, name):
    rc, _ = git(repo, "show-ref", "--verify", "-q", f"refs/heads/{name}")
    return rc == 0


def resolves_to_commit(repo, name):
    rc, _ = git(repo, "rev-parse", "--verify", "-q", f"{name}^{{commit}}")
    return rc == 0


def checkout_would_detach(repo, args):
    if any(a in ("-b", "-B", "--orphan", "-t", "--track") for a in args):
        return False
    if "--detach" in args:
        return True
    if "--" in args:
        return False  # pathspec checkout, does not move HEAD
    targets = [a for a in args if not a.startswith("-")]
    if not targets:
        return False
    target = targets[0]
    if target == "-" or is_local_branch(repo, target):
        return False
    # Existing file paths are pathspec checkouts even without an explicit "--".
    if (Path(repo) / target).exists():
        return False
    return resolves_to_commit(repo, target)


def check_segment(tokens, cwd):
    parsed = parse_git_invocation(tokens, cwd)
    if parsed is None:
        return  # not a git command (stg, ls, ...): always allowed
    repo, sub, args = parsed
    rc, _ = git(repo, "rev-parse", "--git-dir")
    if rc != 0:
        return  # not a repo; nothing to guard
    if sub not in MUTATING:
        return

    _, git_dir = git(repo, "rev-parse", "--absolute-git-dir")
    if git_dir and (Path(git_dir) / "BISECT_LOG").exists():
        return  # bisect in progress: legit detached-HEAD use

    detached = git(repo, "symbolic-ref", "-q", "HEAD")[0] != 0
    if detached:
        _, sha = git(repo, "rev-parse", "--short", "HEAD")
        block(
            f"[git-surgery-guard] BLOCKED: HEAD is detached at {sha} and "
            f"'git {sub}' would risk orphaning work.\n"
            f"First attach your work to a ref:  git switch -c rescue/<slug>\n"
            f"That makes everything on this HEAD unloseable. Then continue.\n"
            f"(Diagnosis commands — status/log/diff/reflog — are not blocked.)"
        )

    if sub == "checkout" and checkout_would_detach(repo, args):
        target = next((a for a in args if not a.startswith("-")), "<sha>")
        block(
            f"[git-surgery-guard] BLOCKED: 'git checkout {target}' would enter "
            f"detached HEAD. Work built there is orphaned the moment anything "
            f"else is checked out.\n"
            f"Use a named branch instead:  git switch -c tmp/<name> {target}"
        )
    if sub == "switch" and ("--detach" in args or "-d" in args):
        block(
            "[git-surgery-guard] BLOCKED: 'git switch --detach' enters detached "
            "HEAD. Use a named branch:  git switch -c tmp/<name> <commit>"
        )

    _, branch = git(repo, "branch", "--show-current")
    if branch and sub in STG_UNSAFE:
        rc, _ = git(repo, "show-ref", "--verify", "-q", f"refs/stacks/{branch}")
        if rc == 0:
            block(
                f"[git-surgery-guard] BLOCKED: branch '{branch}' is stgit-managed "
                f"(refs/stacks/{branch} exists). Raw 'git {sub}' silently desyncs "
                f"the patch stack — stg won't notice until its next operation.\n"
                f"Use the stg equivalent (stg refresh / stg new / stg edit ...), "
                f"or if raw git is genuinely required, run 'stg repair' "
                f"immediately afterward."
            )


def main():
    try:
        payload = json.load(sys.stdin)
        command = payload.get("tool_input", {}).get("command", "")
        cwd = payload.get("cwd") or "."
    except Exception:
        sys.exit(0)
    segments = split_segments(command)
    if segments is None:
        sys.exit(0)  # unparseable: allow; the desync detector backstops
    for tokens in segments:
        try:
            check_segment(tokens, cwd)
        except SystemExit:
            raise
        except Exception:
            continue
    sys.exit(0)


if __name__ == "__main__":
    main()
