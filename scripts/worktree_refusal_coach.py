#!/usr/bin/env python3
"""PostToolUseFailure hook (matcher Bash): when Claude Code's worktree-isolation guard refuses a
command, name the refused shell shape and the fix. Silent for every other failure.

Reads the hook JSON on stdin; prints one hookSpecificOutput JSON object, or nothing. Never
exits non-zero -- a coaching hook must not be able to block anything.
"""
import json
import re
import sys

REFUSAL_MARKERS = ("isolated in the worktree", "Refusing to run")
PATH_RE = re.compile(r"isolated in the worktree (\S+?),")
GIT_C_RE = re.compile(r"\bgit\s+-C\s+(\S+)")
GIT_SUBST_RE = re.compile(r"\$\(\s*git\b|`\s*git\b")
EVAL_RE = re.compile(r"(?:^|[\s;&|(])eval\b")
ENV_PREFIX_SUBST_RE = re.compile(r"^\s*(?:[A-Za-z_]\w*=\S*\s+)*[A-Za-z_]\w*=\S*\$\([^()]*\)[^\s;&|]*\s+[A-Za-z]")
SEGMENT_SPLIT_RE = re.compile(r"\s*(?:&&|\|\||;|\||\n)\s*")
CD_RE = re.compile(r"^\(?\s*cd\s+(\S+)")

CWD_TRAP = ("Your shell cwd is outside the worktree. Call EnterWorktree {wt} again to reset it, "
            "then rerun the command unchanged.")
GIT_C = "git -C {arg} targets the shared checkout. Run git without -C; your shell already sits in {wt}."
CD_ELSEWHERE = "Do not cd out of the worktree before git. Run the git command from {wt}, with no cd."
GIT_SUBST = ("$(git …) inside a string is refused in an isolated worktree. Run the git command as "
             "its own Bash call and use its output in the next call.")
EVAL = "eval is refused in an isolated worktree. Write the command literally."
ENV_PREFIX = ("A $(…) inside an environment prefix is refused. Compute the value in its own Bash "
              "call, then pass the literal.")
FALLBACK = ("Refused in an isolated worktree: git -C <other>, cd <other>; git, $(git …), eval, and "
            "$(…) in an env prefix. Allowed: plain git, &&, ;, pipes, heredocs, loops. Run the "
            "command from {wt} without those shapes.")
TRAILER = " Worktree: {wt}."


def under(path: str, root: str) -> bool:
    root = root.rstrip("/")
    return path == root or path.startswith(root + "/")


def cd_elsewhere_before_git(command: str, wt: str) -> bool:
    """True when an absolute `cd <dir>` outside the worktree precedes a segment that names git."""
    left_worktree = False
    for seg in SEGMENT_SPLIT_RE.split(command):
        m = CD_RE.match(seg)
        if m:
            arg = m.group(1).strip("'\"")
            if arg.startswith("/") and not under(arg, wt):
                left_worktree = True
            continue
        if left_worktree and re.search(r"\bgit\b", seg):
            return True
    return False


def classify(command: str, error: str, wt: str) -> str:
    if "working directory resolved to the shared checkout" in error:
        return CWD_TRAP.format(wt=wt)
    m = GIT_C_RE.search(command)
    if m and not under(m.group(1).strip("'\""), wt):
        return GIT_C.format(arg=m.group(1), wt=wt)
    if "changes directory to the shared checkout" in error or cd_elsewhere_before_git(command, wt):
        return CD_ELSEWHERE.format(wt=wt)
    if GIT_SUBST_RE.search(command):
        return GIT_SUBST
    if EVAL_RE.search(command):
        return EVAL
    if ENV_PREFIX_SUBST_RE.search(command):
        return ENV_PREFIX
    return FALLBACK.format(wt=wt)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(data, dict):
        return 0
    error = data.get("error")
    command = (data.get("tool_input") or {}).get("command") if isinstance(data.get("tool_input"), dict) else None
    if not isinstance(error, str) or not isinstance(command, str):
        return 0
    if not all(marker in error for marker in REFUSAL_MARKERS):
        return 0
    m = PATH_RE.search(error)
    wt = m.group(1) if m else "your worktree"
    text = classify(command, error, wt) + TRAILER.format(wt=wt)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUseFailure",
                                             "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
