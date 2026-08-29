#!/usr/bin/env python3
# ABOUTME: Read-only RLM-style query tool over the mnemosyne journal corpus in PostgreSQL.
# ABOUTME: Subcommands: dump (JSONL), search (pgvector cosine), grep, verify (quote check), show.
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


def cmd_verify(args):
    c = get_entry(args.path)
    if c is None:
        print(f"MISSING-PATH {args.path}")
        # help: where does the fragment actually live?
        class A: since = None; until = None; ignore_case = False
        A.fragment = args.fragment
        hits = sql(f"select file_path from {TABLE} where content like "
                   f"'%{args.fragment.replace(chr(39), chr(39)*2)}%' limit 5")
        if hits.strip():
            print("fragment found instead in:\n" + hits, end="")
        sys.exit(1)
    i = c.find(args.fragment)
    if i < 0:
        print(f"NOQUOTE {args.path}")
        sys.exit(1)
    lo, hi = max(0, i - args.context), i + len(args.fragment) + args.context
    print(f"OK {args.path}\n...{c[lo:hi]}...")


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
    v.set_defaults(fn=cmd_verify)

    sh = sub.add_parser("show", help="print one raw entry by file_path")
    sh.add_argument("path")
    sh.set_defaults(fn=cmd_show)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
