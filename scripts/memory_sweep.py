#!/usr/bin/env python3
"""Flag auto-memories that describe code a commit deleted.

kata claudes-home#6pp3, shape (2'). A batch of memories can die at a single commit —
a language port, a feature removal, a re-vendor, a crate rename — and nothing notices.
They keep loading, read as current, and mislead. The deleting commit names the dead
paths exactly, so it is a far better signal than guessing which text tokens are paths.

Output is a REVIEW LIST for a human. This never edits a memory.

  memory_sweep.py                 sweep every resolvable project since its watermark
  memory_sweep.py --project PATH  just one
  memory_sweep.py --since '90 days ago'   ignore watermarks, use a date window
  memory_sweep.py --advance       record current HEADs as swept (after acting on output)

Two hazards this deliberately guards, both of which produced wrong numbers during
development (see 6pp3 comments):

  1. ~/.claude/projects/<name> encodes BOTH '/' and '.' as '-'. A naive dash->slash
     decode silently skips every repo with a hyphen or dot in its path -- 17 real
     projects, including the one that prompted the issue. It fails toward an empty
     result, which reads as a clean sweep. resolve() walks the filesystem instead.
  2. Matching a deleted path by BASENAME flags any memory mentioning a generic name:
     deleting 'hexgrid/README.md' flagged a memory citing an unrelated README.md.
     Match the full path or a distinctive tail; bare basenames only when distinctive.
"""
import argparse, fcntl, json, os, re, subprocess, sys
from collections import defaultdict

PROJECTS = os.path.expanduser("~/.claude/projects")
STATE = os.path.expanduser("~/.claude/memory-sweep/watermarks.json")

# Basenames too common to match on their own; require a path tail for these.
GENERIC = {
    "README.md", "CHANGELOG.md", "AGENTS.md", "CLAUDE.md", "mod.rs", "lib.rs",
    "main.rs", "error.rs", "common.rs", "types.rs", "cli.py", "utils.py",
    "config.py", "helpers.py", "conftest.py", "__init__.py", "setup.py",
    "index.js", "index.ts", "types.ts", "utils.ts", "Cargo.toml", "package.json",
    "requirements.txt", "Makefile", "test.py", "tests.py",
}


def resolve(encoded):
    """Recover a real directory from a tr '/.' '--' encoded project-dir name."""
    def walk(base, rest):
        if not rest:
            return base if os.path.isdir(base) else None
        try:
            entries = os.listdir(base)
        except OSError:
            return None
        cands = []
        for e in entries:
            if not os.path.isdir(os.path.join(base, e)):
                continue
            key = e.replace(".", "-")
            if rest == key:
                cands.append((len(key), e, ""))
            elif rest.startswith(key + "-"):
                cands.append((len(key), e, rest[len(key) + 1:]))
        for _, e, remainder in sorted(cands, reverse=True):
            got = walk(os.path.join(base, e), remainder)
            if got:
                return got
        return None
    return walk("/", encoded.lstrip("-"))


class GitUnavailable(Exception):
    """git could not answer. Distinct from 'nothing was deleted' -- conflating the two
    makes a broken check look like a clean corpus, which is the failure direction that
    matters here."""


def git(repo, *args, timeout=120):
    """stdout on success, None on failure.

    CAUTION: a successful command that prints nothing returns "", which is falsy and
    therefore indistinguishable from the None that means failure. Never test a git
    call's SUCCESS through this function -- use git_ok(). That conflation silently
    disabled the whole watermark mechanism once already.
    """
    r = subprocess.run(["git", "-C", repo, *args],
                       capture_output=True, text=True, timeout=timeout)
    return r.stdout if r.returncode == 0 else None


def git_ok(repo, *args, timeout=120):
    """True iff the command exited 0. For commands that answer via exit code alone."""
    r = subprocess.run(["git", "-C", repo, *args],
                       capture_output=True, text=True, timeout=timeout)
    return r.returncode == 0


def deleted_paths(repo, since=None, after_commit=None):
    """Paths deleted in the window and still absent from the tree."""
    args = ["log", "--diff-filter=D", "--name-only", "--pretty=format:"]
    if after_commit:
        # explicit range; a bare -n would apply to the FILTERED set, not the scan window
        args.append(f"{after_commit}..HEAD")
    else:
        args.append(f"--since={since}")
    out = git(repo, *args)
    if out is None:
        return None
    dead = {l.strip() for l in out.splitlines() if l.strip()}
    return {d for d in dead if not os.path.exists(os.path.join(repo, d))}


def patterns_for(path):
    """Text patterns that would identify this deleted path in prose."""
    pats = [path]
    seg = path.split("/")
    if len(seg) >= 2:
        pats.append("/".join(seg[-2:]))
    base = os.path.basename(path)
    if base not in GENERIC:
        pats.append(base)
    return list(dict.fromkeys(pats))


# Directory names too common to grep for as bare words; a memory saying "src" almost
# never means the deleted directory. Their files are still caught by path matching --
# only the rename/move signal is suppressed for these.
NOISY_DIRS = {
    "src", "lib", "bin", "app", "test", "tests", "docs", "doc", "examples", "example",
    "build", "dist", "target", "out", "tmp", "data", "assets", "static", "public",
    "scripts", "tools", "utils", "config", "internal", "pkg", "cmd", "api", "web",
}


def vanished_dirs(repo, dead):
    """Top-level dirs wholly gone -- the rename/move signal a path check alone misses.

    The hexgrid -> hexweave crate rename left three memories naming the crate and
    citing no path at all; nothing else in this sweep would have seen them.
    """
    tops = {d.split("/")[0] for d in dead if "/" in d}
    return {t for t in tops
            if not os.path.exists(os.path.join(repo, t))
            and t not in NOISY_DIRS and len(t) >= 3
            and re.fullmatch(r"[a-z][a-z0-9_-]+", t)}


def word_re(s, dirlike=False):
    """Match s as a whole token in prose.

    The lookbehind alternation admits a preceding '/' so a path cited inside a URL
    (a github blob permalink, say) still matches -- blocking that was a silent miss,
    and a miss is the failure direction that matters here. The cost is that a deleted
    'src/utils.py' also matches inside 'crates/x/src/utils.py'; that over-flags onto a
    list a human reads, which is the tolerable direction.

    The lookahead is symmetric with the strict lookbehind so 'src/utils.py' no longer
    matches inside 'src/utils.py-old' or 'src/utils.py.bak'.
    """
    tail = r"(?![\w/.-])" if not dirlike else r"(?![\w/-])"
    return re.compile(r"(?:(?<![\w/.-])|(?<=/))" + re.escape(s) + tail)


def sweep_project(repo, memdir, since=None, after_commit=None):
    dead = deleted_paths(repo, since=since, after_commit=after_commit)
    if dead is None:
        raise GitUnavailable(repo)   # never let a failed git read as a clean sweep
    if not dead:
        return {}, set()
    gone = vanished_dirs(repo, dead)
    compiled = [(d, [word_re(p) for p in patterns_for(d)]) for d in sorted(dead)]
    gone_re = [(t, word_re(t, dirlike=True)) for t in sorted(gone)]

    hits = defaultdict(set)
    for name in sorted(os.listdir(memdir)):
        if not name.endswith(".md") or name == "MEMORY.md":
            continue
        try:
            txt = open(os.path.join(memdir, name), encoding="utf-8",
                       errors="replace").read()
        except OSError:
            continue
        for path, regexes in compiled:
            if any(r.search(txt) for r in regexes):
                hits[name].add(path)
        for top, r in gone_re:
            if r.search(txt):
                hits[name].add(f"{top}/  [directory gone - renamed or moved?]")
    return hits, gone


def load_state():
    try:
        return json.load(open(STATE))
    except (OSError, ValueError):
        return {}


def merge_state(updates):
    """Merge updates into the on-disk state under an exclusive lock.

    Several Claude sessions run at once on this machine. An unsynchronised
    load-modify-save lets the later writer revert watermarks it never touched, because
    each merges into a snapshot taken before the other's write. Re-read inside the lock
    so we merge onto whatever is current, not onto our own stale copy.
    """
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    lock = STATE + ".lock"
    with open(lock, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            st = load_state()
            st.update(updates)
            tmp = STATE + f".tmp.{os.getpid()}"
            with open(tmp, "w") as f:
                json.dump(st, f, indent=2, sort_keys=True)
            os.replace(tmp, STATE)
            return st
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", help="sweep only this repo path")
    ap.add_argument("--since", help="date window instead of watermarks, e.g. '90 days ago'")
    ap.add_argument("--advance", action="store_true",
                    help="record current HEADs as swept, print nothing else")
    ap.add_argument("--quiet-when-clean", action="store_true",
                    help="print nothing at all when there is nothing to report")
    args = ap.parse_args()

    state = load_state()
    targets = []
    if args.project:
        repo = os.path.abspath(os.path.expanduser(args.project))
        enc = "-" + repo.lstrip("/").replace("/", "-").replace(".", "-")
        md = os.path.join(PROJECTS, enc, "memory")
        targets.append((repo, md))
    else:
        for enc in sorted(os.listdir(PROJECTS)):
            md = os.path.join(PROJECTS, enc, "memory")
            if not os.path.isdir(md):
                continue
            repo = resolve(enc)
            if repo:
                targets.append((repo, md))

    unresolved, reports, swept = [], [], {}
    for repo, memdir in targets:
        if not os.path.isdir(memdir) or not os.path.isdir(os.path.join(repo, ".git")):
            continue
        head = (git(repo, "rev-parse", "HEAD") or "").strip()
        if not head:
            unresolved.append(repo)
            continue
        if args.advance:
            # Only bank a watermark for a repo we could actually have swept. Advancing
            # past a window that errored buries deletions nobody ever reviewed.
            if deleted_paths(repo, since="1 day ago") is None:
                unresolved.append(repo)
            else:
                swept[repo] = head
            continue
        swept[repo] = head
        mark = None if args.since else state.get(repo)
        if mark and not git_ok(repo, "cat-file", "-e", mark + "^{commit}"):
            mark = None  # watermark rewritten out of history (rebase, filter-repo)
        try:
            hits, gone = sweep_project(
                repo, memdir,
                since=args.since or ("90 days ago" if not mark else None),
                after_commit=mark)
        except GitUnavailable:
            unresolved.append(repo)
            continue
        if hits:
            reports.append((repo, memdir, hits, gone))

    if args.advance:
        merge_state(swept)
        print(f"memory-sweep: watermark advanced for {len(swept)} project(s)")
        if unresolved:
            print(f"  NOT advanced (git could not answer) for {len(unresolved)}:")
            for r in unresolved:
                print(f"    {r}")
        return 0

    def report_skipped():
        if unresolved:
            print(f"MEMORY-SWEEP: {len(unresolved)} project(s) COULD NOT BE CHECKED "
                  f"(git unavailable) -- these are gaps, not zeroes:")
            for r in unresolved:
                print(f"    {r}")

    if not reports:
        if not args.quiet_when_clean or unresolved:
            print(f"MEMORY-SWEEP: clean ({len(swept)} projects checked)")
            report_skipped()
        return 0

    total = sum(len(h) for _, _, h, _ in reports)
    print(f"MEMORY-SWEEP: {total} memories reference code that was deleted "
          f"({len(reports)} of {len(swept)} projects)")
    print("These are CANDIDATES, not verdicts -- a memory may cite a dead path "
          "deliberately, as historical evidence for a general lesson. Read before editing.\n")
    for repo, memdir, hits, gone in reports:
        print(f"  {repo}"
              + (f"   [gone: {', '.join(sorted(g + '/' for g in gone))}]" if gone else ""))
        for name in sorted(hits):
            print(f"    {name}")
            for d in sorted(hits[name])[:6]:
                print(f"        {d}")
        print()
    report_skipped()
    print("When resolved: memory_sweep.py --advance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
