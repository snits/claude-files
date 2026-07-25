#!/usr/bin/env python3
"""Carry a focus hint from the conversation into the compaction prompt.

Claude cannot invoke /compact, and a slash command is only prompt text — it has
no way to hand its own output to the compactor. The PreCompact hook is the one
channel that does: Claude Code joins each hook's stdout into the custom
instructions the summarizer receives, merged with whatever the user typed after
/compact rather than replacing it.

So a hint is staged to a file keyed by session, and the hook reads and consumes
it on the next compaction. Hints are one-shot: a hint left behind by a
compaction that never happened would otherwise steer an unrelated one.

Usage:
  compact_hint.py --set "workflow wf_abc is running; act on its notification"
  compact_hint.py --hook          read PreCompact JSON on stdin, emit the hint
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

HINTS_DIR = Path.home() / ".claude" / "compact-hints"
ORPHAN_AGE_DAYS = 7

SESSION_ID = re.compile(r"\A[A-Za-z0-9_-]{1,128}\Z")


def hint_path(hints_dir, session_id):
    """Locate a session's hint file, refusing anything that isn't a bare id."""
    if not session_id or not SESSION_ID.match(str(session_id)):
        raise ValueError(f"not a usable session id: {session_id!r}")
    return Path(hints_dir) / f"{session_id}.txt"


def set_hint(hints_dir, session_id, text):
    text = (text or "").strip()
    if not text:
        raise ValueError("refusing to stage an empty hint")
    path = hint_path(hints_dir, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")
    return path


def take_hint(hints_dir, session_id):
    """Return a session's hint and consume it. Absent or unreadable reads empty."""
    try:
        path = hint_path(hints_dir, session_id)
        text = path.read_text(encoding="utf-8").strip()
        path.unlink()
    except (OSError, ValueError):
        return ""
    return text


def sweep(hints_dir, max_age_days=ORPHAN_AGE_DAYS, now=None):
    """Drop hints from sessions that ended before ever compacting."""
    now = time.time() if now is None else now
    cutoff = now - max_age_days * 86400
    try:
        stale = [p for p in Path(hints_dir).glob("*.txt") if p.stat().st_mtime < cutoff]
    except OSError:
        return
    for path in stale:
        try:
            path.unlink()
        except OSError:
            pass


def run_hook(stdin_text, hints_dir):
    """Turn PreCompact hook input into the text to append to the instructions.

    Never raises and never returns anything on a session with no hint staged:
    an empty emission leaves the user's own /compact instructions untouched.
    """
    try:
        payload = json.loads(stdin_text)
        session_id = payload.get("session_id")
    except (ValueError, AttributeError):
        return ""
    hint = take_hint(hints_dir, session_id)
    sweep(hints_dir)
    return hint


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--set", metavar="TEXT", help="stage a hint for this session")
    group.add_argument(
        "--hook", action="store_true", help="run as the PreCompact hook (JSON on stdin)"
    )
    parser.add_argument("--hints-dir", default=HINTS_DIR)
    args = parser.parse_args(argv)

    if args.hook:
        try:
            hint = run_hook(sys.stdin.read(), args.hints_dir)
        except Exception:
            hint = ""
        if hint:
            print(hint)
        return 0

    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session_id:
        print("CLAUDE_CODE_SESSION_ID is unset — not inside a session", file=sys.stderr)
        return 1
    try:
        path = set_hint(args.hints_dir, session_id, args.set)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"hint staged for the next compaction: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
