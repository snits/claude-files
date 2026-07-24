#!/usr/bin/env python3
"""Check that a retro report's citations say what the transcript says.

Mining agents produce plausible-looking citations that do not resolve -- right
quote against the wrong line, or a quote that appears nowhere. Both are invisible
in a clean-looking report. This resolves every `path/to/session.jsonl:LINE`
pointer and confirms the quoted text is actually at that line.

    python3 verify_citations.py <report.md>

Exit code is non-zero if any citation fails, so it can gate a retro before
candidates are presented.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# A pointer is a path ending .jsonl followed by :LINE
POINTER = re.compile(r"(?P<path>/[^\s`'\"()\[\]]*\.jsonl):(?P<line>\d+)")
# Quoted text following the pointer on the same report line
QUOTE = re.compile(r"`([^`]{4,})`|\"([^\"]{4,})\"")

# How much of the quote must appear at the cited line. Miners truncate and
# reflow, so an exact match is too strict; a prefix is enough to bind the
# citation to the line.
MATCH_PREFIX_CHARS = 40


@dataclass
class Result:
    path: str
    line: int
    quote: str | None
    status: str
    found_at: int | None = None


# Tags the prefilter adds to slice entries. Miners copy them along with the
# text, but they are annotations and appear nowhere in the raw transcript.
ANNOTATION_TAGS = re.compile(r"\[(?:TOOL ERROR|TEAMMATE)\]:?\s*")


def _strip_annotations(quote: str) -> str:
    return ANNOTATION_TAGS.sub("", quote).strip()


def _normalize(text: str) -> str:
    return " ".join(text.split()).lower()


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif block.get("type") == "tool_result":
                body = block.get("content")
                parts.append(body if isinstance(body, str) else _text_of(body))
        return "".join(parts)
    return ""


def _line_text(path: Path, lineno: int) -> str | None:
    """Readable text of one transcript line, or None if that line does not exist."""
    with path.open("r", errors="replace") as handle:
        for current, raw in enumerate(handle, start=1):
            if current != lineno:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                return raw
            return _text_of(entry.get("message", {}).get("content"))
    return None


def extract_citations(report: str, with_abbrev: bool = False) -> list[tuple]:
    """Pull (path, line, quote) triples out of a markdown report.

    With `with_abbrev`, each tuple gains a trailing bool marking pointers that
    were written shortened and so cannot be resolved by a reader.
    """
    found = []
    for report_line in report.splitlines():
        for match in POINTER.finditer(report_line):
            quote_match = QUOTE.search(report_line[match.end() :])
            quote = (quote_match.group(1) or quote_match.group(2)) if quote_match else None
            record = (match.group("path"), int(match.group("line")), quote)
            if with_abbrev:
                record += (is_abbreviated(report_line, match.start()),)
            found.append(record)
    return found


def is_abbreviated(report_line: str, pointer_start: int) -> bool:
    """True if the pointer was written shortened, e.g. `.../session.jsonl:21`."""
    return report_line[:pointer_start].endswith("..")


def verify_one(
    path_str: str, lineno: int, quote: str | None, abbreviated: bool = False
) -> Result:
    if abbreviated:
        return Result(path_str, lineno, quote, "ABBREVIATED-POINTER")

    path = Path(path_str)
    if not path.is_file():
        return Result(path_str, lineno, quote, "NO-SUCH-FILE")

    # Existence of the cited line is the harder failure, so it outranks a
    # missing quote: a pointer into empty space is wrong either way.
    text = _line_text(path, lineno)
    if text is None:
        return Result(path_str, lineno, quote, "NO-SUCH-LINE")
    if quote is None:
        return Result(path_str, lineno, quote, "UNVERIFIABLE")

    cleaned = _strip_annotations(quote)
    if len(cleaned) < 4:
        return Result(path_str, lineno, quote, "UNVERIFIABLE")

    needle = _normalize(cleaned)[:MATCH_PREFIX_CHARS]
    if needle in _normalize(text):
        return Result(path_str, lineno, quote, "OK")

    return Result(path_str, lineno, quote, "TEXT-MISMATCH", found_at=_search(path, needle))


def _search(path: Path, needle: str) -> int | None:
    """Line where the quote actually lives, if anywhere -- turns a failure into a fix."""
    with path.open("r", errors="replace") as handle:
        for current, raw in enumerate(handle, start=1):
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if needle in _normalize(_text_of(entry.get("message", {}).get("content"))):
                return current
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="retro report or miner output (markdown)")
    args = parser.parse_args(argv)

    citations = extract_citations(args.report.read_text(errors="replace"), with_abbrev=True)
    if not citations:
        print(f"FAIL: no citations found in {args.report}")
        print("A retro finding without a resolvable pointer is an impression.")
        return 1

    results = [verify_one(path, line, quote, abbrev) for path, line, quote, abbrev in citations]
    counts = Counter(r.status for r in results)

    for r in results:
        if r.status == "OK":
            continue
        detail = f" (quote actually at line {r.found_at})" if r.found_at else ""
        print(f"{r.status}: {r.path}:{r.line}{detail}")
        if r.quote:
            print(f"    cited: {' '.join(r.quote.split())[:120]}")

    summary = ", ".join(f"{n} {status}" for status, n in sorted(counts.items()))
    print(f"\n{len(results)} citations checked: {summary}")

    return 0 if set(counts) <= {"OK"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
