#!/usr/bin/env python3
"""Dependency-graph analyses over a kata export.

kata computes the ready set and stops. This adds the questions kata cannot
answer today: what is circularly blocked, why is this issue stuck, what does
it hold up, and where are the worst bottlenecks.

Reads `kata export` JSONL. kata is upstream third-party (kenn-io/kata), so this
lives outside it and touches nothing in the database.

  kata_graph.py cycles
  kata_graph.py why-blocked abc4
  kata_graph.py impact abc4
  kata_graph.py bottlenecks --project claudes-home

Edge semantics, verified against the export (not assumed):
  blocks: from -> to, meaning `from` must close before `to` can proceed.
          This is the ordering graph, matching what `kata ready` filters on.
  parent: from -> to, meaning `from` is a sub-task of `to`. Displayed as
          hierarchy only. kata's own `ready` does not treat parent as
          ordering, so neither do we.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

OPEN = "open"


def load(export_path=None, project=None):
    """Return (issues_by_id, blocks_edges, project_name).

    Runs `kata export` unless handed an existing JSONL file.
    """
    if export_path is None:
        tmp = Path(tempfile.mkdtemp()) / "kata-export.jsonl"
        subprocess.run(
            ["kata", "export", "--allow-running-daemon", "--output", str(tmp)],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        export_path = tmp

    issues, links, projects = {}, [], {}
    with open(export_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            kind, data = row["kind"], row["data"]
            if kind == "issue":
                if not data.get("deleted_at"):
                    issues[data["id"]] = data
            elif kind == "link":
                links.append(data)
            elif kind == "project":
                projects[data["id"]] = data["name"]

    if project:
        matches = [pid for pid, name in projects.items() if name == project]
        if not matches:
            sys.exit(
                f"no project named {project!r}; known: "
                + ", ".join(sorted(projects.values()))
            )
        keep = set(matches)
        issues = {i: v for i, v in issues.items() if v["project_id"] in keep}

    blocks = [
        (e["from_issue_id"], e["to_issue_id"])
        for e in links
        if e["type"] == "blocks"
        and e["from_issue_id"] in issues
        and e["to_issue_id"] in issues
    ]
    return issues, blocks, project


def label(issues, iid, width=60):
    it = issues[iid]
    mark = " " if it["status"] == OPEN else "x"
    title = (it.get("title") or "").replace("\n", " ")
    if len(title) > width:
        title = title[: width - 1] + "…"
    return f"[{mark}] {it['short_id']}  {title}"


def resolve(issues, ref):
    hits = [i for i, v in issues.items() if v["short_id"] == ref]
    if not hits:
        sys.exit(f"no issue with short_id {ref!r} in scope")
    if len(hits) > 1:
        sys.exit(f"short_id {ref!r} is ambiguous across projects; pass --project")
    return hits[0]


def open_subgraph(issues, blocks):
    """Ordering edges among issues that are still open.

    A closed issue no longer blocks anything, so restricting to open nodes is
    what makes a reported cycle actually mean "these can never become ready".
    """
    succ, pred = defaultdict(list), defaultdict(list)
    for a, b in blocks:
        if issues[a]["status"] == OPEN and issues[b]["status"] == OPEN:
            succ[a].append(b)
            pred[b].append(a)
    return succ, pred


def sccs(nodes, succ):
    """Tarjan's SCC, iterative so deep graphs cannot blow the stack."""
    index, low, on_stack, stack = {}, {}, set(), []
    counter, out = 0, []

    for root in nodes:
        if root in index:
            continue
        work = [(root, iter(succ.get(root, ())))]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)

        while work:
            node, children = work[-1]
            advanced = False
            for child in children:
                if child not in index:
                    index[child] = low[child] = counter
                    counter += 1
                    stack.append(child)
                    on_stack.add(child)
                    work.append((child, iter(succ.get(child, ()))))
                    advanced = True
                    break
                if child in on_stack:
                    low[node] = min(low[node], index[child])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                group = []
                while True:
                    top = stack.pop()
                    on_stack.discard(top)
                    group.append(top)
                    if top == node:
                        break
                out.append(group)
    return out


def reach(start, adj):
    """Transitive closure from start, excluding start itself."""
    seen, queue = set(), list(adj.get(start, ()))
    while queue:
        node = queue.pop()
        if node in seen:
            continue
        seen.add(node)
        queue.extend(adj.get(node, ()))
    seen.discard(start)
    return seen


def cmd_cycles(issues, blocks, args):
    succ, _ = open_subgraph(issues, blocks)
    nodes = [i for i, v in issues.items() if v["status"] == OPEN]
    groups = [g for g in sccs(nodes, succ) if len(g) > 1]
    groups += [[a] for a, b in blocks if a == b and issues[a]["status"] == OPEN]

    if not groups:
        print(f"no dependency cycles among {len(nodes)} open issues")
        return 0
    print(f"{len(groups)} dependency cycle(s) — every issue below is permanently")
    print("unreachable by `kata ready` until an edge is cut:\n")
    for group in sorted(groups, key=len, reverse=True):
        print(f"  cycle of {len(group)}:")
        for iid in group:
            print(f"    {label(issues, iid)}")
        print()
    return 1


def cmd_why_blocked(issues, blocks, args):
    target = resolve(issues, args.ref)
    _, pred = open_subgraph(issues, blocks)
    print(label(issues, target))
    if not pred.get(target):
        status = issues[target]["status"]
        print(
            "  not blocked — ready to work"
            if status == OPEN
            else f"  not blocked (status: {status})"
        )
        return 0

    seen = set()

    def walk(iid, depth):
        for up in sorted(pred.get(iid, ()), key=lambda n: issues[n]["short_id"]):
            pad = "  " * (depth + 1)
            if up in seen:
                print(f"{pad}└ {label(issues, up)}   (already shown above)")
                continue
            seen.add(up)
            print(f"{pad}└ blocked by {label(issues, up)}")
            walk(up, depth + 1)

    walk(target, 0)
    if target in seen:
        seen.discard(target)
        print(
            f"\n{len(seen)} open issue(s) must close first — but this issue is"
            "\nreachable from itself, so it sits in a cycle and can never become"
            "\nready. Run `cycles` to see the full component."
        )
    else:
        print(f"\n{len(seen)} open issue(s) must close first")
    return 0


def cmd_impact(issues, blocks, args):
    target = resolve(issues, args.ref)
    succ, _ = open_subgraph(issues, blocks)
    downstream = reach(target, succ)
    print(label(issues, target))
    if not downstream:
        print("  nothing open is waiting on this")
        return 0
    print(f"\n{len(downstream)} open issue(s) unblock (directly or transitively):\n")
    for iid in sorted(downstream, key=lambda n: issues[n]["short_id"]):
        direct = " *" if iid in succ.get(target, ()) else "  "
        print(f" {direct} {label(issues, iid)}")
    print("\n  * = directly blocked by it")
    return 0


def cmd_bottlenecks(issues, blocks, args):
    succ, _ = open_subgraph(issues, blocks)
    scored = [
        (len(reach(iid, succ)), iid)
        for iid, v in issues.items()
        if v["status"] == OPEN
    ]
    scored = [s for s in scored if s[0] > 0]
    if not scored:
        print("nothing open is blocking anything else")
        return 0
    scored.sort(key=lambda s: (-s[0], issues[s[1]]["short_id"]))
    print("open issues ranked by how much open work waits on them:\n")
    for count, iid in scored[: args.limit]:
        print(f"  {count:4d}  {label(issues, iid)}")
    if len(scored) > args.limit:
        print(f"\n  ...{len(scored) - args.limit} more (--limit to see them)")
    return 0


def main():
    # Shared flags are attached both to the top-level parser and to every
    # subparser, so they work on either side of the subcommand — matching kata,
    # where `kata ready --project x` and `kata --project x ready` both work.
    # SUPPRESS is load-bearing: without it, a subparser writes its own default
    # over a value already parsed before the subcommand, so `--project x cycles`
    # would silently lose the scope. SUPPRESS leaves the attribute unset when
    # the flag is absent, so whichever side supplied it wins.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--project",
        default=argparse.SUPPRESS,
        help="scope to one kata project by name",
    )
    common.add_argument(
        "--export",
        default=argparse.SUPPRESS,
        help="reuse an existing `kata export` JSONL instead of running one",
    )

    parser = argparse.ArgumentParser(
        description=__doc__.split("\n")[0], parents=[common]
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser(
        "cycles",
        parents=[common],
        help="find circular block chains (exits 1 if any)",
    )

    p = sub.add_parser("why-blocked", parents=[common], help="full blocker chain")
    p.add_argument("ref", help="short id, e.g. abc4")

    p = sub.add_parser("impact", parents=[common], help="what this holds up")
    p.add_argument("ref", help="short id, e.g. abc4")

    p = sub.add_parser(
        "bottlenecks", parents=[common], help="rank by downstream weight"
    )
    p.add_argument("--limit", type=int, default=15)

    args = parser.parse_args()
    issues, blocks, _ = load(
        getattr(args, "export", None), getattr(args, "project", None)
    )
    handler = {
        "cycles": cmd_cycles,
        "why-blocked": cmd_why_blocked,
        "impact": cmd_impact,
        "bottlenecks": cmd_bottlenecks,
    }[args.cmd]
    return handler(issues, blocks, args)


if __name__ == "__main__":
    sys.exit(main())
