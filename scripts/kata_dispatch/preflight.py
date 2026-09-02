#!/usr/bin/env python3
# ~/.claude/scripts/kata_dispatch/preflight.py
"""Refuse edits outside a dispatch worktree.

Standalone: `python3 preflight.py` exits 0 when cwd is a dispatch worktree, 2 otherwise.
Hook:       `python3 preflight.py --hook` reads a PreToolUse JSON payload on stdin and exits
            2 (blocking the tool) when the tool's file_path or cwd is not inside a dispatch
            worktree. Exit 2 is what Claude Code treats as a block; stderr goes to the model.
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def _git(args, cwd):
    p = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def check(cwd, file_path=None, main_checkout=None) -> tuple[bool, str]:
    cwd = Path(cwd).resolve()
    rc, top = _git(["rev-parse", "--show-toplevel"], cwd)
    if rc != 0:
        return False, f"{cwd} is not inside a git worktree"
    top = Path(top).resolve()
    rc, common = _git(["rev-parse", "--git-common-dir"], cwd)
    common = (cwd / common).resolve() if not Path(common).is_absolute() else Path(common).resolve()
    main = Path(main_checkout or os.environ.get("KATA_DISPATCH_MAIN_CHECKOUT") or common.parent).resolve()
    if top == main:
        return False, f"cwd {top} is the main checkout; edits belong in a dispatch worktree"
    rc, branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if not branch.startswith("dispatch/"):
        return False, f"branch {branch!r} is not a dispatch/ branch"
    if file_path:
        fp = Path(file_path)
        fp = (cwd / fp).resolve() if not fp.is_absolute() else fp.resolve()
        try:
            fp.relative_to(top)
        except ValueError:
            return False, f"{fp} is outside the worktree {top}"
    return True, "ok"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--hook" in argv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            payload = {}
        cwd = payload.get("cwd") or os.getcwd()
        fp = (payload.get("tool_input") or {}).get("file_path")
        ok, why = check(cwd, fp)
    else:
        ok, why = check(os.getcwd())
    if ok:
        return 0
    print(f"kata-dispatch preflight: {why}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
