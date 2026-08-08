#!/usr/bin/env python3
# ~/.claude/scripts/stg_desync_detector.py
"""PostToolUse safety net: detect stgit stack desync after any Bash command.

The PreToolUse guard classifies command text and can be evaded by scripts or
aliases. This hook checks the *effect*: on an stg-managed branch, the stack
metadata (refs/stacks/<branch> -> stack.json "head") must match the branch head.
Mismatch => the previous command desynced the stack; tell the agent to run
'stg repair' NOW. Detect-and-instruct only — never mutates (auto-repair would
race stg's own operations and silently launder mistakes into stack state).

Verified detection method (stg 2.6.0, 2026-08-08):
  git cat-file blob refs/stacks/<branch>:stack.json  ->  {"head": "<sha>", ...}
"""
import json
import subprocess
import sys


def git(repo, *args):
    try:
        p = subprocess.run(
            ["git", "-C", repo, *args], capture_output=True, text=True, timeout=5
        )
        return p.returncode, p.stdout.strip()
    except Exception:
        return 1, ""


def main():
    try:
        payload = json.load(sys.stdin)
        cwd = payload.get("cwd") or "."
    except Exception:
        sys.exit(0)

    rc, branch = git(cwd, "branch", "--show-current")
    if rc != 0 or not branch:
        sys.exit(0)
    rc, _ = git(cwd, "show-ref", "--verify", "-q", f"refs/stacks/{branch}")
    if rc != 0:
        sys.exit(0)  # not an stg-managed branch

    rc, raw = git(cwd, "cat-file", "blob", f"refs/stacks/{branch}:stack.json")
    if rc != 0:
        sys.exit(0)
    try:
        stack_head = json.loads(raw)["head"]
    except Exception:
        sys.exit(0)
    rc, branch_head = git(cwd, "rev-parse", f"refs/heads/{branch}")
    if rc != 0:
        sys.exit(0)

    if stack_head != branch_head:
        print(
            f"[stg-desync-detector] WARNING: the previous command desynced the "
            f"stgit stack on branch '{branch}'.\n"
            f"  stack head:  {stack_head}\n"
            f"  branch head: {branch_head}\n"
            f"Run 'stg repair' NOW, before any other stg operation. stg gives no "
            f"error for this state — later stg commands would misbehave silently.",
            file=sys.stderr,
        )
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
