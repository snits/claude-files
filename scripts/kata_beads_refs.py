#!/usr/bin/env python3
"""Audit, resolve, and rewrite beads-era issue references in kata issue prose.

The beads -> kata migration rewrote the link table and recorded each issue's old
id (a `beads-id:` label and an `import_mapping` row), but references written
*inside* issue prose still use beads ids. `kata show alexandria-64we` fails, so
those cross-references are dead ends when read.

    kata_beads_refs.py audit                  # scale, per project
    kata_beads_refs.py resolve alexandria-64we jgia --project alexandria
    kata_beads_refs.py rewrite --project recall           # dry run
    kata_beads_refs.py rewrite --project recall --apply

Three things are deliberately NOT references, each learned by getting it wrong:

  migration footer  Every migrated body ends with a block introduced by
                    `---\\nImported from Beads`, containing `beads_id: <own id>`
                    and friends. That is self-identifying metadata, not a link.
                    It is 3372 of the ~4400 raw matches — rewriting it corrupts
                    the provenance record. Only prose above the footer is
                    considered.
  sub-issue ids     Beads ids can carry a `.N` suffix (`alexandria-lwp.5`); 760
                    of 3039 do. A pattern that stops at the dot silently
                    resolves the sub-issue to its parent — a wrong link that
                    looks right.
  component names   `alexandria-engine`, `fatescroll-core`, `diceman-cli` match
                    the `project-word` shape but were never ids. Matching is by
                    exact membership in the known beads id set, not by shape.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

FOOTER = re.compile(r"\n---\nImported from Beads\n")


def load(export_path=None):
    if export_path is None:
        tmp = Path(tempfile.mkdtemp()) / "kata-export.jsonl"
        subprocess.run(
            ["kata", "export", "--allow-running-daemon", "--output", str(tmp)],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        export_path = tmp
    rows = defaultdict(list)
    with open(export_path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                d = json.loads(line)
                rows[d["kind"]].append(d["data"])
    return rows


def split_footer(body):
    """Return (prose, footer) — the footer keeps its leading delimiter."""
    parts = FOOTER.split(body or "", 1)
    if len(parts) == 1:
        return body or "", ""
    return parts[0], (body or "")[len(parts[0]) :]


class Corpus:
    def __init__(self, rows):
        self.projects = {p["id"]: p["name"] for p in rows["project"]}
        self.issues = {i["id"]: i for i in rows["issue"] if not i.get("deleted_at")}
        self.live_short_ids = {i["short_id"] for i in self.issues.values()}

        # import_mapping is authoritative; `beads-id:` labels independently
        # record the same fact and are used as a fallback.
        self.beads = {}
        for m in rows["import_mapping"]:
            if m.get("source") == "beads" and m.get("object_type") == "issue":
                issue = self.issues.get(m["issue_id"])
                if issue:
                    self.beads[m["external_id"]] = issue
        for lb in rows["issue_label"]:
            if lb["label"].startswith("beads-id:"):
                issue = self.issues.get(lb["issue_id"])
                if issue:
                    self.beads.setdefault(lb["label"][len("beads-id:") :], issue)

        words = set()
        dict_path = Path("/usr/share/dict/words")
        if dict_path.exists():
            with open(dict_path, encoding="utf-8", errors="ignore") as fh:
                words = {w.strip().lower() for w in fh if 3 <= len(w.strip()) <= 5}

        # Bare tokens are resolved only within their own project, and only when
        # unambiguous: not a live kata short_id, not an English word ("all"
        # alone produced 131 false matches before this filter).
        self.bare = defaultdict(dict)
        for ext, issue in self.beads.items():
            _, _, tail = ext.rpartition("-")
            if tail and tail not in self.live_short_ids and tail not in words:
                self.bare[issue["project_id"]][tail] = issue

        names = sorted(
            map(re.escape, set(self.projects.values())), key=len, reverse=True
        )
        # `(?:\.[0-9]+)*` — zero OR MORE dot groups. Beads sub-issue ids nest:
        # 2279 ids have no dot, 726 have one (`lwp.5`), 34 have two
        # (`orbweaver-rs-1ys8.18.7`). Matching only one level consumed
        # `…1ys8.18`, resolved it to the PARENT, and left a dangling `.7` —
        # a link that points at the wrong issue while looking well-formed.
        # Combined with exact-only lookup in ref_target, an unrecognised
        # variant is now left untouched rather than half-rewritten.
        self.ref_re = re.compile(
            r"\b(?:" + "|".join(names) + r")-[0-9a-z]+(?:\.[0-9]+)*\b"
        )
        self.token_re = re.compile(r"\b[0-9a-z]{3,5}\b")
        self.stats = Counter()

    def ref_target(self, ref, owner=None):
        """Resolve a qualified beads ref, or None. Self-refs return None."""
        target = self.beads.get(ref)
        if target is None:
            self.stats["not a beads id"] += 1
            return None
        if owner is not None and target["id"] == owner["id"]:
            self.stats["self-reference"] += 1
            return None
        return target

    def scan(self, rows, include_bare=True):
        """Return [(issue, where, ref, kind, target)] for genuine references."""
        found = []
        units = []
        for issue in self.issues.values():
            prose, footer = split_footer(issue.get("body"))
            self.stats["in migration footer"] += len(self.ref_re.findall(footer))
            units.append((issue, "title", issue.get("title") or ""))
            units.append((issue, "body", prose))
        for c in rows["comment"]:
            issue = self.issues.get(c.get("issue_id"))
            if issue:
                units.append((issue, "comment", c.get("body") or ""))

        for issue, where, text in units:
            if not text:
                continue
            spans = []
            for m in self.ref_re.finditer(text):
                spans.append(m.span())
                target = self.ref_target(m.group(0), issue)
                if target:
                    found.append((issue, where, m.group(0), "qualified", target))
            if not include_bare:
                continue
            index = self.bare.get(issue["project_id"], {})
            for m in self.token_re.finditer(text):
                if any(s <= m.start() < e for s, e in spans):
                    continue
                target = index.get(m.group(0))
                if target and target["id"] != issue["id"]:
                    found.append((issue, where, m.group(0), "bare", target))
        return found

    def rewrite_prose(self, text, owner):
        """Rewrite qualified refs in one prose fragment. Returns (new, n)."""
        count = 0

        def sub(m):
            nonlocal count
            target = self.ref_target(m.group(0), owner)
            if not target:
                return m.group(0)
            count += 1
            return f"{self.projects[target['project_id']]}#{target['short_id']}"

        return self.ref_re.sub(sub, text), count


def in_scope(corpus, project):
    if not project:
        return set(corpus.projects)
    keep = {pid for pid, n in corpus.projects.items() if n == project}
    if not keep:
        sys.exit(f"no project named {project!r}")
    return keep


def cmd_audit(corpus, rows, args):
    keep = in_scope(corpus, args.project)
    found = [f for f in corpus.scan(rows) if f[0]["project_id"] in keep]

    per_project = defaultdict(Counter)
    touched = defaultdict(set)
    for issue, where, ref, kind, target in found:
        name = corpus.projects[issue["project_id"]]
        per_project[name][f"{kind}:{'comment' if where == 'comment' else 'body'}"] += 1
        touched[name].add(issue["short_id"])

    if not found:
        print("no beads-era cross-references found")
    else:
        print(f"{len(found)} beads-era cross-reference(s) across "
              f"{len(per_project)} project(s), in "
              f"{sum(len(v) for v in touched.values())} issue(s).\n")
        print(f"  {'project':<18} {'qual/body':>10} {'qual/cmt':>9} "
              f"{'bare':>6}")
        print(f"  {'-'*18} {'-'*10} {'-'*9} {'-'*6}")
        for name in sorted(per_project, key=lambda n: -sum(per_project[n].values())):
            c = per_project[name]
            bare = c["bare:body"] + c["bare:comment"]
            print(f"  {name:<18} {c['qualified:body']:>10} "
                  f"{c['qualified:comment']:>9} {bare:>6}")

    print("\nexcluded, and why:")
    for k in ("in migration footer", "self-reference", "not a beads id"):
        print(f"  {corpus.stats[k]:>6}  {k}")
    print("\n  Only `qual/body` is rewritable — kata cannot edit an existing "
          "comment,\n  and the migration footer records each issue's own id "
          "(not a link).")
    return 0


def cmd_resolve(corpus, rows, args):
    keep = in_scope(corpus, args.project) if args.project else None
    rc = 0
    for ref in args.refs:
        target = corpus.beads.get(ref)
        if not target and keep:
            for pid in keep:
                target = corpus.bare.get(pid, {}).get(ref)
                if target:
                    break
        if target:
            name = corpus.projects[target["project_id"]]
            print(f"{ref:<22} -> {name}#{target['short_id']}  "
                  f"{(target['title'] or '')[:52]}")
        else:
            print(f"{ref:<22} -> UNRESOLVED"
                  f"{'' if args.project else '  (bare refs need --project)'}")
            rc = 1
    return rc


def cmd_rewrite(corpus, rows, args):
    keep = in_scope(corpus, args.project)
    plan = []
    footer_refs = 0
    for issue in corpus.issues.values():
        if issue["project_id"] not in keep:
            continue
        prose, footer = split_footer(issue.get("body"))
        footer_refs += len(corpus.ref_re.findall(footer))
        new_body, nb = corpus.rewrite_prose(prose, issue)
        new_title, nt = corpus.rewrite_prose(issue.get("title") or "", issue)
        if nb or nt:
            plan.append((issue, new_body + footer if nb else None,
                         new_title if nt else None, nb + nt))

    if not plan:
        print("nothing to rewrite in scope")
        return 0
    total = sum(p[3] for p in plan)
    print(f"{total} cross-reference(s) in {len(plan)} issue(s) — "
          f"{args.project or 'ALL projects'}")
    print(f"{footer_refs} ref(s) in migration footers left untouched; "
          "comments not editable\n")

    if not args.apply:
        for issue, body, title, n in plan[: args.samples]:
            name = corpus.projects[issue["project_id"]]
            print(f"--- {name}#{issue['short_id']}  ({n} ref)")
            old_prose, _ = split_footer(issue.get("body"))
            for m in corpus.ref_re.finditer(old_prose):
                t = corpus.beads.get(m.group(0))
                if t and t["id"] != issue["id"]:
                    print(f"      {m.group(0)}  ->  "
                          f"{corpus.projects[t['project_id']]}#{t['short_id']}")
        print("\nDRY RUN — nothing written. Re-run with --apply.")
        return 0

    ok = failed = 0
    for issue, body, title, _ in plan:
        name = corpus.projects[issue["project_id"]]
        cmd = ["kata", "edit", f"{name}#{issue['short_id']}", "--quiet"]
        if body is not None:
            cmd += ["--body", body]
        if title is not None:
            cmd += ["--title", title]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            ok += 1
        else:
            failed += 1
            print(f"  FAILED {name}#{issue['short_id']}: "
                  f"{(res.stderr or res.stdout).strip()[:110]}")
    print(f"\nrewrote {ok} issue(s); {failed} failed")
    return 1 if failed else 0


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--project", default=argparse.SUPPRESS)
    common.add_argument("--export", default=argparse.SUPPRESS)
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                     parents=[common])
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("audit", parents=[common], help="count refs per project")
    p = sub.add_parser("resolve", parents=[common], help="resolve refs")
    p.add_argument("refs", nargs="+")
    p = sub.add_parser("rewrite", parents=[common], help="rewrite body/title refs")
    p.add_argument("--apply", action="store_true", help="write (default: dry run)")
    p.add_argument("--samples", type=int, default=8)

    args = parser.parse_args()
    rows = load(getattr(args, "export", None))
    corpus = Corpus(rows)
    args.project = getattr(args, "project", None)
    return {"audit": cmd_audit, "resolve": cmd_resolve,
            "rewrite": cmd_rewrite}[args.cmd](corpus, rows, args)


if __name__ == "__main__":
    sys.exit(main())
