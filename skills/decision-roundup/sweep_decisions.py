#!/usr/bin/env python3
"""Cross-project sweep of blocked kata issues, read from projstat's --json feed.

Answers the question a per-project startup check structurally cannot: what is waiting in
projects Jerry has not opened lately. A per-project check surfaces `needs-decision` for the
current project only, so an issue in a quiet project is invisible indefinitely.

The project set and the issue enumeration come from `projstat --json`, which is the single
aggregated source (claudes-home#z64h). Ages do not: the feed's `age_days` is measured from
`created_at`, and what matters here is how long an issue has been *waiting*, which is when its
label went on. The two diverge wildly — fatescroll `kmgh` reads 159 days old and was labeled
`needsinfo` 15 days earlier — so the label-applied age is enriched from kata's event log for
the handful of issues the feed already named. Enriching named issues is not a second sweep.

Three feed properties this relies on, each of which fails toward "looks like nothing is there"
if a consumer flattens it:
  * `tasks: null` with `kata_binding` other than "unbound" means the project could NOT be
    asked. That is a gap, never a zero.
  * An empty `blocked` array means asked-and-holds-none, which is a different fact.
  * `deferred` items are parked, not standing. Reported separately with their `defer_until`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

# The labels projstat's roll-up carries (internal/kata/client.go rollUpLabels).
# `retitle` is deliberately absent: it is a maintenance queue, not a blocked state, and
# must never gate anything.
ROLLUP_LABELS = ("needs-decision", "needs-review", "needsinfo")

# The two labels only Jerry can clear. `needsinfo` is excluded because a triage loop clears
# it without him; folding it in would inflate a number that reads as his personal backlog.
WAITING_ON_YOU = ("needs-decision", "needs-review")


def run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def feed() -> dict:
    """The projstat roll-up. Exits rather than returning a partial view."""
    code, out, err = run(["projstat", "--json"])
    if code != 0:
        sys.exit(f"cannot read projstat feed: {(err or out).strip()}")
    try:
        return json.loads(out)
    except json.JSONDecodeError as e:
        sys.exit(f"projstat feed is not JSON: {e}")


def gap_reason(record: dict) -> str:
    """Why this project could not be asked, in the feed's own terms."""
    binding = record.get("kata_binding") or ""
    if binding == "":
        return "no kata binding established (.kata.toml unread or naming nothing)"
    if record.get("tasks_unknown"):
        return "daemon holds no such project (stale .kata.toml)"
    return "daemon did not answer"


def collect(report: dict, labels: tuple[str, ...]) -> tuple[list, list, list]:
    """Split the feed into (standing, deferred, gaps) for the given labels.

    Ages here are the feed's created-based `age_days`; `enrich_ages` replaces them where a
    label event exists.
    """
    standing: list[list] = []
    deferred: list[tuple[str, str, dict]] = []
    gaps: list[tuple[str, str]] = []

    for record in report.get("projects", []):
        name = record.get("name") or record.get("path", "?")
        tasks = record.get("tasks")
        if tasks is None:
            if (record.get("kata_binding") or "") != "unbound":
                gaps.append((name, gap_reason(record)))
            continue
        for item in tasks.get("blocked") or []:
            if not any(l in labels for l in item.get("labels") or []):
                continue
            if item.get("deferred"):
                deferred.append((item.get("defer_until") or "UNDATED", name, item))
                continue
            item["_age_basis"] = "created"
            standing.append([item.get("age_days", 0), name, item])
    return standing, deferred, gaps


def labeled_at(project: str, label: str) -> dict[str, str]:
    """Map short_id -> when `label` was last applied, from the project's event log.

    Events come back ordered by id ASC, so `--limit` takes the OLDEST rows, not the newest.
    Paging with `--after` to exhaustion is required; a bare `--limit N` would silently miss
    every recent label on any project with more than N events.
    """
    applied: dict[str, str] = {}
    after = 0
    while True:
        code, out, _ = run(
            ["kata", "events", "--project", project, "--json",
             "--limit", "1000", "--after", str(after)]
        )
        if code != 0:
            return applied  # caller falls back to the feed's created-based age
        try:
            payload = json.loads(out)
        except json.JSONDecodeError:
            return applied
        events = payload.get("events", payload if isinstance(payload, list) else [])
        if not events:
            return applied
        for e in events:
            after = max(after, e.get("event_id", after))
            if e.get("type") != "issue.labeled":
                continue
            if (e.get("payload") or {}).get("label") != label:
                continue
            short = e.get("issue_short_id")
            when = e.get("created_at")
            if short and when:
                applied[short] = when  # ASC order means the last write is the latest
        if len(events) < 1000:
            return applied


def age_days(created: str, now: dt.datetime) -> int:
    ts = dt.datetime.fromisoformat(created.replace("Z", "+00:00"))
    return (now - ts).days


def enrich_ages(standing: list, labels: tuple[str, ...], now: dt.datetime) -> None:
    """Replace created-based ages with label-applied ages, in place, where one exists.

    Only the projects that actually hold a matching item are queried — typically two or
    three, not the whole tracked set.
    """
    wanted: dict[str, set[str]] = {}
    for _, project, item in standing:
        for label in item.get("labels") or []:
            if label in labels:
                wanted.setdefault(project, set()).add(label)

    applied: dict[tuple[str, str], dict[str, str]] = {}
    for project, project_labels in wanted.items():
        for label in project_labels:
            applied[(project, label)] = labeled_at(project, label)

    for row in standing:
        _, project, item = row
        best = None
        for label in item.get("labels") or []:
            when = applied.get((project, label), {}).get(item["short_id"])
            if when and (best is None or when < best):
                best = when  # earliest label application = longest wait
        if best:
            row[0] = age_days(best, now)
            item["_age_basis"] = "labeled"


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

    Reports what is waiting on Jerry — needs-decision plus needs-review, counted once per
    item — with the split visible, and `needsinfo` deliberately absent. Ruling (Jerry,
    2026-08-16): needsinfo stays in the feed for loop visibility and off this line, because
    a persistent 26 sitting next to his 4 every morning is the report-card effect his
    2026-08-15 ruling on projstat#hgd6 rejected.

    Fires on the live count, not on elapsed days: a round-up against an empty backlog is
    noise, and a calendar interval cannot tell the difference.
    """
    decisions = sum(1 for _, _, i in standing if "needs-decision" in (i.get("labels") or []))
    reviews = sum(1 for _, _, i in standing if "needs-review" in (i.get("labels") or []))
    parts = [f"DECISIONS waiting_on_you={len(standing)} (decision {decisions}, review {reviews})"]
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
        choices=ROLLUP_LABELS,
        help="which blocked label the full report sweeps (default: needs-decision). "
             "Ignored by --brief, which always reports waiting_on_you.",
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
    labels = WAITING_ON_YOU if args.brief else (args.label,)
    report = feed()

    standing, deferred, gaps = collect(report, labels)
    # Fold before enriching: a folded item must get a label-applied age like any other.
    if args.include_deferred:
        for due, project, item in deferred:
            item["_age_basis"] = "created"
            standing.append([item.get("age_days", 0), project, item])
        deferred = []

    enrich_ages(standing, labels, now)
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
            if i.get("_age_basis") == "created":
                age = f"{age}?"  # no label event found; this is filing age, not waiting age
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
