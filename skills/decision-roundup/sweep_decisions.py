#!/usr/bin/env python3
"""Cross-project sweep of standing kata decisions.

Answers the question /wakey structurally cannot: which rulings are waiting in projects
Jerry has not opened lately. /wakey surfaces needs-decision per project, so an issue in a
quiet project is invisible indefinitely.

Two kata gotchas this works around, both of which fail toward "looks like nothing is there":
  * Only the FIRST --label/--no-label flag applies, so `--label needs-decision
    --no-label deferred` silently ignores the exclusion. Deferred issues are filtered
    client-side here instead.
  * A project that fails to resolve returns an error rather than an empty list. Those are
    reported as gaps, never folded into "0 standing".
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

DECISION_LABELS = ("needs-decision", "needs-review", "needsinfo", "retitle")


def run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def projects() -> list[str]:
    code, out, err = run(["kata", "projects", "list"])
    if code != 0:
        sys.exit(f"cannot enumerate kata projects: {err.strip()}")
    names = []
    for line in out.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[0].isdigit():
            names.append(parts[1].strip())
    return names


def issues_for(project: str, label: str) -> tuple[list[dict], str | None]:
    """Return (issues, error). Error is non-None when the project could not be queried."""
    code, out, err = run(
        ["kata", "list", "--project", project, "--label", label, "--json"]
    )
    if code != 0:
        detail = (err or out).strip().splitlines()
        return [], detail[0] if detail else f"exit {code}"
    try:
        return json.loads(out).get("issues", []), None
    except json.JSONDecodeError as e:
        return [], f"unparseable JSON: {e}"


def age_days(created: str, now: dt.datetime) -> int:
    ts = dt.datetime.fromisoformat(created.replace("Z", "+00:00"))
    return (now - ts).days


def defer_until(issue: dict) -> str | None:
    raw = (issue.get("metadata") or {}).get("defer_until")
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw.strip('"')
    return str(raw)


STAMP = "~/.claude/decisions/last-roundup"


def last_roundup(now: dt.datetime) -> str:
    """Age of the last round-up, in the same shape /wakey reports for retro and dream."""
    path = pathlib.Path(STAMP).expanduser()
    if not path.is_file():
        return "last=never"
    raw = path.read_text().strip()
    try:
        ran = dt.datetime.fromisoformat(raw).replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return f"last={raw or 'unreadable'} days_ago=?"
    return f"last={raw} days_ago={(now - ran).days}"


def brief_line(standing: list, gaps: list, now: dt.datetime) -> str:
    """One line for a startup check.

    Reports the live standing count, not just elapsed time. A calendar interval is the
    wrong trigger for this: a round-up is due when decisions are actually waiting, and
    running one against an empty backlog is noise.
    """
    parts = [f"DECISIONS standing={len(standing)}"]
    if standing:
        oldest_age, oldest_proj, oldest = standing[0]
        parts.append(f"oldest={oldest_age}d({oldest_proj}/{oldest['short_id']})")
        parts.append(f"projects={len({p for _, p, _ in standing})}")
    parts.append(last_roundup(now))
    if gaps:
        parts.append(f"unqueryable={len(gaps)}")
    return " ".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--label",
        default="needs-decision",
        choices=DECISION_LABELS,
        help="which standing label to sweep (default: needs-decision)",
    )
    ap.add_argument(
        "--include-deferred",
        action="store_true",
        help="fold deferred issues into the main list instead of a separate section",
    )
    ap.add_argument(
        "--brief",
        action="store_true",
        help="emit one status line for a startup check instead of the full report",
    )
    args = ap.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    standing: list[tuple[int, str, dict]] = []
    deferred: list[tuple[str, str, dict]] = []
    gaps: list[tuple[str, str]] = []

    for proj in projects():
        found, err = issues_for(proj, args.label)
        if err:
            gaps.append((proj, err))
            continue
        for issue in found:
            labels = issue.get("labels") or []
            if "deferred" in labels and not args.include_deferred:
                deferred.append((defer_until(issue) or "UNDATED", proj, issue))
                continue
            standing.append((age_days(issue["created_at"], now), proj, issue))

    standing.sort(key=lambda r: -r[0])
    deferred.sort(key=lambda r: r[0])

    if args.brief:
        print(brief_line(standing, gaps, now))
        return 0

    print(f"# Standing `{args.label}` — cross-project sweep, {now:%Y-%m-%d}")
    print()
    if standing:
        print(f"## Awaiting a ruling ({len(standing)}), oldest first")
        print()
        print("| Age | Project | Ref | Title | Other labels |")
        print("|---:|---|---|---|---|")
        for age, proj, i in standing:
            other = ",".join(l for l in (i.get("labels") or []) if l != args.label) or "—"
            title = i["title"].replace("|", "\\|")
            print(f"| {age}d | {proj} | `{i['short_id']}` | {title} | {other} |")
    else:
        print(f"No standing `{args.label}` issues in any project.")
    print()

    if deferred:
        print(f"## Deferred ({len(deferred)}) — parked, not waiting on anyone")
        print()
        for due, proj, i in deferred:
            flag = "  **UNDATED — nothing will bring this back**" if due == "UNDATED" else ""
            print(f"- `{i['short_id']}` ({proj}) until **{due}** — {i['title']}{flag}")
        print()

    if gaps:
        print(f"## Could not query ({len(gaps)}) — gaps, NOT zeroes")
        print()
        for proj, err in gaps:
            print(f"- **{proj}** — {err}")
        print()
        print("A project that fails to resolve is not a project with nothing in it.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
