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
        abs_fp = fp if fp.is_absolute() else (cwd / fp)
        # Judge containment lexically first (normpath, no symlink resolution) so that a
        # symlink the dispatcher plants on purpose (e.g. a shared .scratchpad) isn't
        # rejected just because it resolves outside the worktree. `..` escapes are still
        # caught because normpath collapses them lexically.
        lexical = Path(os.path.normpath(str(abs_fp)))
        try:
            rel = lexical.relative_to(top)
        except ValueError:
            return False, f"{lexical} is outside the worktree {top}"
        if rel.parts and rel.parts[0] == ".scratchpad":
            return True, "ok"
        # Otherwise also require the symlink-resolved path to stay inside the worktree,
        # so a symlink planted inside the worktree pointing elsewhere can't escape it.
        resolved = abs_fp.resolve()
        try:
            resolved.relative_to(top)
        except ValueError:
            return False, f"{resolved} is outside the worktree {top}"
    return True, "ok"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--hook" in argv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            payload = None
        tool_input = (payload or {}).get("tool_input") or {}
        fp = tool_input.get("file_path") or tool_input.get("notebook_path")
        if payload is None or not fp:
            print("kata-dispatch preflight: hook payload has no file path; refusing", file=sys.stderr)
            return 2
        cwd = payload.get("cwd") or os.getcwd()
        ok, why = check(cwd, fp)
    else:
        ok, why = check(os.getcwd())
    if ok:
        return 0
    print(f"kata-dispatch preflight: {why}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
