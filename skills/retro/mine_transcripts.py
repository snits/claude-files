#!/usr/bin/env python3
"""Extract the friction-bearing slice of Claude Code session transcripts.

A session transcript is mostly tool payloads. What a retrospective needs -- what
Jerry actually typed, and where tools failed -- is a tiny fraction of the bytes.
This prefilters so a miner agent reads kilobytes instead of megabytes.

Every emitted record carries `file:line`, which resolves with:

    sed -n '<line>p' <file>

so any claim built on a record can be checked against the raw transcript.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"

# Turns containing these markers are harness-generated, not typed by Jerry.
HARNESS_MARKERS = (
    "<system-reminder>",
    "<command-name>",
    "<command-message>",
    "<local-command-stdout>",
    "Caveat: The messages below",
)

# A message relayed from another agent session. It arrives as a user turn but is
# not a correction from Jerry, and must not be attributed to him.
TEAMMATE_MARKER = "<teammate-message"

MAX_TOOL_ERRORS_SHOWN = 15

# A turn text repeated verbatim as the opener of at least this many distinct
# sessions is a template — an agent launch prompt, a probe, a batch job — not
# something typed that many times. Ranking on raw turn counts lets one template
# outweigh a project with real back-and-forth.
TEMPLATE_REPEAT_THRESHOLD = 3


@dataclass
class SessionFacts:
    """What one transcript contributes to the retro."""

    path: Path
    project: str
    mtime: float
    bytes: int = 0
    lines: int = 0
    parse_failures: int = 0
    human_turns: list[dict] = field(default_factory=list)
    tool_errors: list[dict] = field(default_factory=list)

    @property
    def is_interactive(self) -> bool:
        """Sessions with no human turns are headless runs carrying no correction signal."""
        return bool(self.human_turns)


def _text_of(content) -> str:
    """Plain text of a message content field, ignoring tool payloads."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def _tool_error_of(content) -> str | None:
    """Error text of a failed tool result, or None if this is not one."""
    if not isinstance(content, list):
        return None
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_result":
            continue
        if not block.get("is_error"):
            continue
        body = block.get("content")
        return (body if isinstance(body, str) else _text_of(body)).strip()
    return None


def scan_session(path: Path) -> SessionFacts:
    stat = path.stat()
    facts = SessionFacts(
        path=path, project=path.parent.name, mtime=stat.st_mtime, bytes=stat.st_size
    )

    with path.open("r", errors="replace") as handle:
        for lineno, raw in enumerate(handle, start=1):
            facts.lines = lineno
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                facts.parse_failures += 1
                continue
            if not isinstance(entry, dict) or entry.get("type") != "user":
                continue
            if entry.get("isMeta"):
                continue

            content = entry.get("message", {}).get("content")

            error = _tool_error_of(content)
            if error is not None:
                facts.tool_errors.append(
                    {"line": lineno, "text": error[:400], "ts": entry.get("timestamp")}
                )
                continue

            text = _text_of(content).strip()
            if not text or any(marker in text for marker in HARNESS_MARKERS):
                continue
            facts.human_turns.append(
                {
                    "line": lineno,
                    "text": text,
                    "ts": entry.get("timestamp"),
                    "speaker": "teammate" if TEAMMATE_MARKER in text else "user",
                }
            )

    return facts


def sessions_in_window(since: float, projects_dir: Path = PROJECTS_DIR) -> list[Path]:
    """Top-level session transcripts modified since `since`.

    Deliberately not recursive: `<session>/subagents/*.jsonl` holds subagent
    transcripts, which contain no human turns and so no correction signal.
    """
    if not projects_dir.is_dir():
        return []
    found: list[Path] = []
    for project in sorted(projects_dir.iterdir()):
        if not project.is_dir():
            continue
        for path in sorted(project.glob("*.jsonl")):
            try:
                if path.stat().st_mtime >= since:
                    found.append(path)
            except OSError:
                continue
    return found


def _emit_json(interactive: list[SessionFacts], headless: list[SessionFacts], since: float):
    json.dump(
        {
            "since": since,
            "sessions": [
                {
                    "path": str(s.path),
                    "project": s.project,
                    "bytes": s.bytes,
                    "lines": s.lines,
                    "parse_failures": s.parse_failures,
                    "human_turns": s.human_turns,
                    "tool_errors": s.tool_errors,
                }
                for s in interactive
            ],
            "headless_sessions": [str(s.path) for s in headless],
        },
        sys.stdout,
        indent=2,
    )


def _normalize(text: str) -> str:
    return " ".join(text.split())


def template_openers(sessions: list[SessionFacts]) -> set[str]:
    """Opening turn texts that recur across sessions — templates, not typing.

    A launched agent session, a connectivity probe, and a batch job each start
    with the same prompt every time. Counted raw, one such template can be most
    of a window's "human turns" and rank its project first for mining.
    """
    openers: dict[str, set[Path]] = {}
    for s in sessions:
        if not s.human_turns:
            continue
        openers.setdefault(_normalize(s.human_turns[0]["text"]), set()).add(s.path)
    return {
        text
        for text, paths in openers.items()
        if len(paths) >= TEMPLATE_REPEAT_THRESHOLD
    }


def distinct_turn_count(sessions: list[SessionFacts], templates: set[str]) -> int:
    """Turns that are neither a known template nor a repeat of another turn.

    This is the ranking signal: how much distinct human input a project saw,
    not how many times the same string was replayed into it.
    """
    seen = {
        _normalize(t["text"])
        for s in sessions
        for t in s.human_turns
    }
    return len(seen - templates)


def _emit_markdown(
    scanned: list[SessionFacts], interactive: list[SessionFacts], headless: list[SessionFacts]
):
    raw_bytes = sum(s.bytes for s in scanned)
    turns = sum(len(s.human_turns) for s in interactive)
    errors = sum(len(s.tool_errors) for s in interactive)
    templates = template_openers(interactive)
    print(f"# Transcript mine: {len(scanned)} sessions, {raw_bytes / 1048576:.1f} MB raw")
    print(f"# {len(interactive)} interactive / {len(headless)} headless (no human turns)")
    print(f"# {turns} human turns, {errors} tool errors")
    if templates:
        print(
            f"# {len(templates)} templated opener(s) seen in "
            f"{TEMPLATE_REPEAT_THRESHOLD}+ sessions each — excluded from the "
            f"distinct counts that order projects below, still printed in full"
        )

    by_project: dict[str, list[SessionFacts]] = {}
    for s in interactive:
        by_project.setdefault(s.project, []).append(s)

    for project, group in sorted(
        by_project.items(), key=lambda kv: -distinct_turn_count(kv[1], templates)
    ):
        total = sum(len(s.human_turns) for s in group)
        distinct = distinct_turn_count(group, templates)
        print(
            f"\n## {project}  ({len(group)} sessions, {total} human turns, "
            f"{distinct} distinct)"
        )
        for s in group:
            print(f"\n### {s.path}")
            if s.parse_failures:
                print(f"_[{s.parse_failures} unparseable lines skipped]_")
            for turn in s.human_turns:
                text = _normalize(turn["text"])
                tag = " [TEAMMATE]" if turn["speaker"] == "teammate" else ""
                if text in templates:
                    tag += " [TEMPLATE]"
                print(f"- {s.path}:{turn['line']}{tag} {text[:600]}")
            for err in s.tool_errors[:MAX_TOOL_ERRORS_SHOWN]:
                print(
                    f"- {s.path}:{err['line']} [TOOL ERROR] "
                    f"{' '.join(err['text'].split())[:300]}"
                )
            hidden = len(s.tool_errors) - MAX_TOOL_ERRORS_SHOWN
            if hidden > 0:
                print(f"- _[{hidden} further tool errors not shown]_")

    if headless:
        print(f"\n## Headless sessions (no human turns, not mined): {len(headless)}")
        for s in headless:
            print(f"- {s.path}")


def _join_dashed_values(argv: list[str]) -> list[str]:
    """Rewrite `--project -home-foo` to `--project=-home-foo`.

    Project dir names begin with a dash (`-home-jsnitsel-devel-alexandria`), which
    argparse reads as the next option and rejects with "expected one argument".
    """
    out: list[str] = []
    skip = False
    for i, arg in enumerate(argv):
        if skip:
            skip = False
            continue
        if arg == "--project" and i + 1 < len(argv) and argv[i + 1].startswith("-"):
            out.append(f"--project={argv[i + 1]}")
            skip = True
        else:
            out.append(arg)
    return out


def main(argv: list[str] | None = None) -> int:
    argv = _join_dashed_values(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=float, default=7.0, help="window size in days")
    parser.add_argument("--since", type=str, default=None, help="ISO date; overrides --days")
    parser.add_argument("--projects-dir", type=Path, default=PROJECTS_DIR)
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="substring of a project dir name, e.g. 'alexandria'",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON not markdown")
    args = parser.parse_args(argv)

    if args.since:
        import datetime as _dt

        since = _dt.datetime.fromisoformat(args.since).timestamp()
    else:
        since = time.time() - args.days * 86400

    paths = sessions_in_window(since, args.projects_dir)
    if args.project:
        paths = [p for p in paths if args.project in p.parent.name]

    scanned = [scan_session(p) for p in paths]
    interactive = [s for s in scanned if s.is_interactive]
    headless = [s for s in scanned if not s.is_interactive]

    if args.json:
        _emit_json(interactive, headless, since)
    else:
        _emit_markdown(scanned, interactive, headless)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
