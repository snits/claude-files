#!/usr/bin/env python3
"""Sweep closed kata issues still wearing an open-work label.

A closed issue that still carries `needs-review`, `needs-decision`, or
`needsinfo` corrupts the signal /talktomegoose, decision-roundup, and the
triage loops read: a closed issue that looks open gets re-triaged.

kata's `list --json` rows do not carry a `labels` field, so client-side
label filtering is impossible — one kata query per label instead.

Usage:
  kata_label_sweep.py                  report only (default), exit 0
  kata_label_sweep.py --strip          comment + remove the label on each row
  kata_label_sweep.py --label needsinfo   restrict to a subset of labels
"""
import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass

OPEN_WORK_LABELS = ("needs-review", "needs-decision", "needsinfo")
ACTOR = "claude-label-sweep"


@dataclass
class Stale:
    qualified_id: str
    label: str
    title: str
    closed_at: str = None


def find_stale(list_fn, labels=OPEN_WORK_LABELS):
    """One Stale row per (closed issue, open-work label) pair it still wears."""
    result = []
    for label in labels:
        for row in list_fn(label):
            result.append(Stale(row["qualified_id"], label, row["title"], row.get("closed_at")))
    result.sort(key=lambda s: (s.qualified_id, s.label))
    return result


def render(stales):
    if not stales:
        return "LABEL SWEEP 0 closed issues labelled"
    lines = [f"LABEL SWEEP {len(stales)} closed issue(s) still labelled"]
    for s in sorted(stales, key=lambda s: (s.qualified_id, s.label)):
        lines.append(f"  {s.qualified_id}  {s.label}  {s.title}")
    return "\n".join(lines)


def _run_kata(args, run):
    proc = run(["kata", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"kata {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def make_list_fn(workspace, run=subprocess.run):
    def list_fn(label):
        out = _run_kata(
            [
                "list",
                "--all",
                "--status",
                "closed",
                "--label",
                label,
                "--json",
                "--limit",
                "0",
                "--workspace",
                workspace,
            ],
            run,
        )
        return json.loads(out)["issues"]

    return list_fn


def strip_stale(stale, workspace, run=subprocess.run):
    comment = (
        f"Label {stale.label} removed by kata_label_sweep.py (kata claudes-home#0rsz): "
        "the issue is closed; an open-work label on a closed issue re-routes it to a "
        "loop that cannot act on it."
    )
    _run_kata(
        ["comment", stale.qualified_id, "--body", comment, "--as", ACTOR, "--workspace", workspace],
        run,
    )
    _run_kata(
        ["label", "rm", stale.qualified_id, stale.label, "--as", ACTOR, "--workspace", workspace],
        run,
    )
    print(f"stripped {stale.qualified_id} {stale.label}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strip", action="store_true", help="comment and remove the label on each row")
    parser.add_argument(
        "--label",
        action="append",
        dest="labels",
        choices=OPEN_WORK_LABELS,
        help="restrict to this label (repeatable); default all open-work labels",
    )
    parser.add_argument("--workspace", default=os.path.expanduser("~/claudes-home"))
    args = parser.parse_args(argv)

    labels = tuple(args.labels) if args.labels else OPEN_WORK_LABELS
    list_fn = make_list_fn(args.workspace)
    stales = find_stale(list_fn, labels)
    print(render(stales))

    if args.strip:
        for stale in stales:
            strip_stale(stale, args.workspace)

    return 0


if __name__ == "__main__":
    sys.exit(main())
