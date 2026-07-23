#!/usr/bin/env python3
"""Defer dates for kata issues.

kata has no native defer/snooze. This layers one on top of two primitives it does
have: the `deferred` label, which `kata ready --no-label deferred` filters on, and
a `defer_until` metadata key holding an ISO date.

Both halves are required. A label with no date hides an issue with nothing to
bring it back, so `--due` reports those separately rather than letting them sit
invisible.

Usage:
  kata_defer.py --due                 report deferred issues that have come due
  kata_defer.py --set <ref> --days 60 defer an issue, label and date together
  kata_defer.py --set <ref> --until 2026-09-21
"""
import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta

DEFER_LABEL = "deferred"
DEFER_KEY = "defer_until"


@dataclass
class DeferReport:
    due: list = field(default_factory=list)
    pending: list = field(default_factory=list)
    undated: list = field(default_factory=list)


def defer_date(today, days):
    return (today + timedelta(days=days)).isoformat()


def report(issues, today):
    """Split deferred issues into come-due, still-waiting, and missing-a-date."""
    result = DeferReport()
    for issue in issues:
        if issue.get("status") != "open":
            continue
        if DEFER_LABEL not in (issue.get("labels") or []):
            continue
        raw = (issue.get("metadata") or {}).get(DEFER_KEY)
        try:
            until = date.fromisoformat(raw)
        except (TypeError, ValueError):
            result.undated.append(issue)
            continue
        (result.due if until <= today else result.pending).append(issue)
    result.due.sort(key=lambda i: (i.get("priority", 9), (i.get("metadata") or {})[DEFER_KEY]))
    result.pending.sort(key=lambda i: ((i.get("metadata") or {})[DEFER_KEY], i.get("priority", 9)))
    return result


def _kata(*args):
    proc = subprocess.run(["kata", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"kata {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def load_issues(project=None):
    args = ["list", "--json", "--limit", "1000"]
    if project:
        args += ["--project", project]
    return json.loads(_kata(*args))["issues"]


def _describe(issue):
    return f"  {issue['short_id']} p{issue.get('priority', '?')} {issue['title']}"


def cmd_due(args, today):
    r = report(load_issues(args.project), today)
    if r.due:
        print(f"DEFERRED DUE {len(r.due)} (as of {today.isoformat()})")
        for issue in r.due:
            print(f"{_describe(issue)} — due {issue['metadata'][DEFER_KEY]}")
    else:
        print(f"DEFERRED DUE 0 of {len(r.pending)} deferred (as of {today.isoformat()})")
    if r.undated:
        print(f"DEFERRED UNDATED {len(r.undated)} — labelled but no {DEFER_KEY}, will never resurface")
        for issue in r.undated:
            print(_describe(issue))
    return 0


def cmd_set(args, today):
    until = args.until or defer_date(today, args.days)
    date.fromisoformat(until)
    for ref in args.set:
        _kata("meta", "set", ref, DEFER_KEY, until)
        _kata("label", "add", ref, DEFER_LABEL)
        print(f"deferred {ref} until {until}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--due", action="store_true", help="report deferred issues now due")
    parser.add_argument("--set", nargs="+", metavar="REF", help="defer these issues")
    parser.add_argument("--days", type=int, default=60, help="days from today (default 60)")
    parser.add_argument("--until", help="explicit ISO date, overrides --days")
    parser.add_argument("--project", help="kata project name")
    args = parser.parse_args(argv)

    today = date.today()
    if args.set:
        return cmd_set(args, today)
    if args.due:
        return cmd_due(args, today)
    parser.error("one of --due or --set is required")


if __name__ == "__main__":
    sys.exit(main())
