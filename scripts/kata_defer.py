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
  kata_defer.py --due --all           the same across every project, grouped by project
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


def load_listing(project=None, all_projects=False):
    """Return kata's whole `list` envelope, so callers can see complete/truncated."""
    if all_projects:
        # --all has no default row cap, so no --limit. Only one --label is honoured.
        args = ["list", "--all", "--json", "--label", DEFER_LABEL]
    else:
        args = ["list", "--json", "--limit", "1000"]
        if project:
            args += ["--project", project]
    return json.loads(_kata(*args))


def load_issues(project=None):
    return load_listing(project)["issues"]


def _describe(issue):
    return f"  {issue['short_id']} p{issue.get('priority', '?')} {issue['title']}"


def _print_by_project(issues, line):
    """Print issues grouped under a project-name line, projects in name order."""
    by_project = {}
    for issue in issues:
        by_project.setdefault(issue.get("project_name", "?"), []).append(issue)
    for name in sorted(by_project):
        print(name)
        for issue in by_project[name]:
            print(line(issue))


def cmd_due_all(today):
    listing = load_listing(all_projects=True)
    r = report(listing["issues"], today)
    if listing.get("complete") is not True or listing.get("truncated") is not False:
        print(
            "WARNING: kata listing is incomplete "
            f"(complete={listing.get('complete')}, truncated={listing.get('truncated')}); "
            "deferred issues may be missing below"
        )
    if r.due:
        print(f"DEFERRED DUE {len(r.due)} (as of {today.isoformat()})")
        _print_by_project(r.due, lambda i: f"{_describe(i)} — due {i['metadata'][DEFER_KEY]}")
    else:
        print(f"DEFERRED DUE 0 of {len(r.pending)} deferred (as of {today.isoformat()})")
    if r.undated:
        print(f"DEFERRED UNDATED {len(r.undated)} — labelled but no {DEFER_KEY}, will never resurface")
        _print_by_project(r.undated, _describe)
    return 0


def cmd_due(args, today):
    if args.all:
        return cmd_due_all(today)
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
    parser.add_argument("--all", action="store_true", help="with --due, cover every project")
    args = parser.parse_args(argv)
    if args.all and args.project:
        parser.error("--all and --project are mutually exclusive")
    if args.all and (not args.due or args.set):
        parser.error("--all requires --due and cannot be combined with --set")

    today = date.today()
    if args.set:
        return cmd_set(args, today)
    if args.due:
        return cmd_due(args, today)
    parser.error("one of --due or --set is required")


if __name__ == "__main__":
    sys.exit(main())
