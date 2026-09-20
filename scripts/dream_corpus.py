#!/usr/bin/env python3
# ABOUTME: Read-only RLM-style query tool over the mnemosyne journal corpus in PostgreSQL.
# ABOUTME: Subcommands: dump (JSONL), search (pgvector cosine), grep, verify (quote check), reverify (batch), show.
#
# The journal store: localhost postgres, db mnemosyne_prod, table ai_memory.journal_entries.
# Embeddings: qwen3-embedding-8b (4096-dim) served by llama-swap at :11435; queries need the
# instruct prefix below (matches mnemosyne's embedding-config.js). This tool issues SELECTs only.
#
# Born from the 2026-08-29 dream pass: the MCP full-corpus fetch crashes the server, and hunts
# want the corpus as data (dump -> slice -> fan out readers; verify quotes by lookup, not recall).

import argparse, json, subprocess, sys, urllib.request

DB = ["psql", "-h", "localhost", "-U", "postgres", "-d", "mnemosyne_prod", "-At"]
ENV = {"PGPASSWORD": "postgres"}
EMBED_URL = "http://localhost:11435/v1/embeddings"
EMBED_MODEL = "qwen3-embedding-8b"
QUERY_PREFIX = ("Instruct: Given a personal journal search query, retrieve relevant "
                "journal entries\nQuery: ")
TABLE = "ai_memory.journal_entries"


def sql(query: str) -> str:
    import os
    r = subprocess.run(DB + ["-f", "-"], input=query, capture_output=True, text=True,
                       env={**os.environ, **ENV})
    if r.returncode != 0:
        sys.exit(f"psql error: {r.stderr.strip()}")
    return r.stdout


def time_clause(args, col="timestamp") -> str:
    c = []
    if getattr(args, "since", None):
        c.append(f"{col} >= '{args.since}'")
    if getattr(args, "until", None):
        c.append(f"{col} < '{args.until}'")
    return (" and " + " and ".join(c)) if c else ""


def row_query(where: str, extra_cols: str = "") -> str:
    return (f"select json_build_object('p', file_path, 'd', to_char(timestamp,"
            f"'YYYY-MM-DD HH24:MI'), 'proj', coalesce(project,''){extra_cols}, "
            f"'c', content)::text from {TABLE} where true {where} order by timestamp")


def cmd_dump(args):
    out = sys.stdout if args.output == "-" else open(args.output, "w")
    out.write(sql(row_query(time_clause(args))))
    if out is not sys.stdout:
        out.close()
        n = sum(1 for _ in open(args.output))
        print(f"wrote {n} entries to {args.output}")


def embed(text: str):
    body = json.dumps({"model": EMBED_MODEL, "input": QUERY_PREFIX + text}).encode()
    req = urllib.request.Request(EMBED_URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["data"][0]["embedding"]


def cmd_search(args):
    vec = "[" + ",".join(f"{x:.7f}" for x in embed(args.query)) + "]"
    q = (f"select to_char(1 - (embedding <=> '{vec}'::vector), 'FM0.000'), file_path, "
         f"to_char(timestamp,'YYYY-MM-DD'), coalesce(project,''), "
         f"left(regexp_replace(content, E'[\\n\\r]+', ' ', 'g'), 140) "
         f"from {TABLE} where embedding is not null {time_clause(args)} "
         f"order by embedding <=> '{vec}'::vector limit {args.k}")
    print(sql(q), end="")


def cmd_grep(args):
    frag = args.fragment.replace("'", "''")
    op = "ilike" if args.ignore_case else "like"
    q = (f"select file_path, to_char(timestamp,'YYYY-MM-DD'), coalesce(project,'') "
         f"from {TABLE} where content {op} '%{frag}%' {time_clause(args)} order by timestamp")
    print(sql(q), end="")


def get_entry(path: str) -> str | None:
    p = path.replace("'", "''")
    out = sql(f"select content from {TABLE} where file_path = '{p}'")
    return out if out.strip() else None


import html as _html, re as _re

_EMPH = _re.compile(r"[*_`]")
_WS = _re.compile(r"\s+")
_QUOTES = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
                         "\u2014": "-", "\u2013": "-"})


def normalize(t: str) -> str:
    """Collapse the differences that make a verbatim quote fail exact match: line wraps,
    emphasis markers, HTML entities, curly quotes/dashes. Both sides get the same treatment."""
    t = _html.unescape(t).translate(_QUOTES)
    t = _EMPH.sub("", t)
    return _WS.sub(" ", t).strip()


def neighbors(path: str) -> list[str]:
    """Entries within a day either side of the cited path's date: the sibling of the same
    timestamp under user/ vs project/ is where a wrong-path citation almost always lives."""
    m = _re.search(r"(\d{4}-\d{2}-\d{2})", path)
    if not m:
        return []
    out = sql(f"select file_path from {TABLE} where timestamp >= date '{m.group(1)}' - 1 "
              f"and timestamp < date '{m.group(1)}' + 2 and file_path <> '{path.replace(chr(39), chr(39)*2)}'")
    return [l for l in out.splitlines() if l.strip()]


def check_quote(path: str, fragment: str, do_norm: bool):
    """Return (status, true_path). status in OK, OK-NORMALIZED, WRONG-PATH, NOQUOTE, MISSING-PATH."""
    c = get_entry(path)
    if c is not None:
        if fragment in c:
            return "OK", path
        if do_norm and normalize(fragment) in normalize(c):
            return "OK-NORMALIZED", path
    # recovery: exact search corpus-wide (only for fragments long enough to be distinctive --
    # a short generic fragment would "recover" to some unrelated entry), then a normalized
    # search over the cited path's date neighbors.
    hits = []
    if len(fragment) >= 25:
        frag_sql = fragment.replace("'", "''")
        hits = [l for l in sql(f"select file_path from {TABLE} where content like '%{frag_sql}%' limit 5").splitlines() if l.strip()]
    if not hits and do_norm:
        nf = normalize(fragment)
        for n in neighbors(path):
            e = get_entry(n)
            if e is not None and nf in normalize(e):
                hits.append(n)
                break
    if hits:
        return "WRONG-PATH", hits[0]
    return ("MISSING-PATH" if c is None else "NOQUOTE"), None


def cmd_verify(args):
    status, true_path = check_quote(args.path, args.fragment, args.normalize)
    if status in ("OK", "OK-NORMALIZED"):
        c = get_entry(args.path)
        hay, needle = (normalize(c), normalize(args.fragment)) if status == "OK-NORMALIZED" else (c, args.fragment)
        i = hay.find(needle)
        lo, hi = max(0, i - args.context), i + len(needle) + args.context
        print(f"{status} {args.path}\n...{hay[lo:hi]}...")
        return
    print(f"{status} {args.path}")
    if true_path:
        print(f"fragment found instead in:\n{true_path}")
    sys.exit(1)


def cmd_reverify(args):
    """Batch-check reader reports: lines shaped `<path> | <theme> | <quote> | <note>`.
    Prints a corrected TSV (status, cited path, true path, theme, quote, note) and a tally."""
    from collections import Counter
    tally = Counter()
    rows = []
    for rp in args.reports:
        n_lines = 0
        for line in open(rp, encoding="utf-8"):
            parts = [x.strip().strip("`") for x in line.rstrip("\n").split("|")]
            if len(parts) < 3 or "/" not in parts[0] or not parts[0].endswith(".md"):
                continue
            path, theme, quote = parts[0], parts[1], parts[2].strip('"')
            note = " | ".join(parts[3:]) if len(parts) > 3 else ""
            if not quote:
                continue
            status, true_path = check_quote(path, quote, True)
            tally[status] += 1
            rows.append((status, path, true_path or "", theme, quote, note, rp))
            n_lines += 1
        print(f"# {rp}: {n_lines} pairs", file=sys.stderr)
    out = sys.stdout if args.output == "-" else open(args.output, "w")
    out.write("status\tcited\ttrue\ttheme\tquote\tnote\treport\n")
    for r in rows:
        out.write("\t".join(x.replace("\t", " ") for x in r) + "\n")
    if out is not sys.stdout:
        out.close()
    print(f"# reports={len(args.reports)} pairs={len(rows)} " +
          " ".join(f"{k}={v}" for k, v in sorted(tally.items())), file=sys.stderr)


def cmd_show(args):
    c = get_entry(args.path)
    if c is None:
        sys.exit(f"MISSING-PATH {args.path}")
    print(c)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("dump", help="dump entries as JSONL {p,d,proj,c}")
    d.add_argument("-o", "--output", default="-")
    d.add_argument("--since"), d.add_argument("--until")
    d.set_defaults(fn=cmd_dump)

    s = sub.add_parser("search", help="pgvector cosine search (qwen3-embedding-8b)")
    s.add_argument("query"), s.add_argument("-k", type=int, default=15)
    s.add_argument("--since"), s.add_argument("--until")
    s.set_defaults(fn=cmd_search)

    g = sub.add_parser("grep", help="substring match over raw content")
    g.add_argument("fragment"), g.add_argument("-i", "--ignore-case", action="store_true")
    g.add_argument("--since"), g.add_argument("--until")
    g.set_defaults(fn=cmd_grep)

    v = sub.add_parser("verify", help="check a quote fragment appears verbatim at a path")
    v.add_argument("path"), v.add_argument("fragment")
    v.add_argument("--context", type=int, default=120)
    v.add_argument("--normalize", action="store_true",
                   help="also accept a match after collapsing whitespace, emphasis, entities, curly quotes")
    v.set_defaults(fn=cmd_verify)

    rv = sub.add_parser("reverify", help="batch-check reader reports (`path | theme | quote | note` lines)")
    rv.add_argument("reports", nargs="+")
    rv.add_argument("-o", "--output", default="-")
    rv.set_defaults(fn=cmd_reverify)

    sh = sub.add_parser("show", help="print one raw entry by file_path")
    sh.add_argument("path")
    sh.set_defaults(fn=cmd_show)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
