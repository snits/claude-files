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
import shlex
import subprocess
import sys
from pathlib import Path

OPERATORS = {"&&", "||", ";", ";;", "|", "&"}


def git(repo, *args):
    try:
        p = subprocess.run(
            ["git", "-C", repo, *args], capture_output=True, text=True, timeout=5
        )
        return p.returncode, p.stdout.strip()
    except Exception:
        return 1, ""


def split_segments(command):
    """Twin of git_surgery_guard.split_segments — duplicated, not imported,
    so this hook never depends on the other hook's file location. Keep the
    two in sync by hand if the tokenizing logic changes."""
    command = command.replace("\n", " ; ")
    lex = shlex.shlex(command, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    lex.commenters = ""
    try:
        tokens = list(lex)
    except ValueError:
        return None
    segments = []
    current = []
    for tok in tokens:
        if tok in OPERATORS:
            if current:
                segments.append(current)
            current = []
        else:
            current.append(tok)
    if current:
        segments.append(current)
    return segments


def resolve_cd(cwd, path):
    """Resolve a `cd` argument against the current effective cwd. Mirrors
    git_surgery_guard.resolve_cd: bare `cd` goes home, `cd -` is unknown to
    a static analyzer so the caller falls back to the payload cwd."""
    if path is None:
        return str(Path.home())
    if path == "-":
        return None
    p = Path(path)
    if p.is_absolute():
        return str(p)
    return str(Path(cwd) / p)


def final_effective_cwd(command, payload_cwd):
    """Walk the command's segments applying `cd`s in order; return the cwd
    in effect for the command's tail. Falls back to payload_cwd on any
    parse failure — same conservative default as the guard."""
    segments = split_segments(command)
    if segments is None:
        return payload_cwd
    effective = payload_cwd
    for tokens in segments:
        if tokens and tokens[0] == "cd":
            path = tokens[1] if len(tokens) > 1 else None
            resolved = resolve_cd(effective, path)
            effective = resolved if resolved is not None else payload_cwd
    return effective


def check_desync(repo):
    """Return a warning message if `repo`'s stg stack is desynced from its
    branch head, else None. Silent (None) for any non-stg or non-repo dir."""
    rc, branch = git(repo, "branch", "--show-current")
    if rc != 0 or not branch:
        return None
    rc, _ = git(repo, "show-ref", "--verify", "-q", f"refs/stacks/{branch}")
    if rc != 0:
        return None  # not an stg-managed branch

    rc, raw = git(repo, "cat-file", "blob", f"refs/stacks/{branch}:stack.json")
    if rc != 0:
        return None
    try:
        stack_head = json.loads(raw)["head"]
    except Exception:
        return None
    rc, branch_head = git(repo, "rev-parse", f"refs/heads/{branch}")
    if rc != 0:
        return None

    if stack_head != branch_head:
        return (
            f"[stg-desync-detector] WARNING: the previous command desynced the "
            f"stgit stack on branch '{branch}'.\n"
            f"  stack head:  {stack_head}\n"
            f"  branch head: {branch_head}\n"
            f"Run 'stg repair' NOW, before any other stg operation. stg gives no "
            f"error for this state — later stg commands would misbehave silently."
        )
    return None


def main():
    try:
        payload = json.load(sys.stdin)
        cwd = payload.get("cwd") or "."
        command = payload.get("tool_input", {}).get("command", "")
    except Exception:
        sys.exit(0)

    effective_cwd = final_effective_cwd(command, cwd)

    dirs = [cwd] if effective_cwd == cwd else [cwd, effective_cwd]
    for d in dirs:
        msg = check_desync(d)
        if msg:
            print(msg, file=sys.stderr)
            sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
