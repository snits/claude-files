"""Predict the repo-relative files an issue will touch, from its text plus a grep.

Conservative by design: no evidence, or too much, becomes WILDCARD, which overlaps
everything and so runs alone. A false 'disjoint' costs a merge conflict at landing; a
false 'overlap' costs only queue time.
"""
import re
import subprocess
from pathlib import Path

WILDCARD = frozenset({"*"})

_EXT = r"py|go|rs|ts|tsx|js|md|sh|toml|json|yaml|yml|txt|ap|c|h|cfg|ini|lock"
PATH_RE = re.compile(rf"(?<![\w/`])((?:[\w.-]+/)+[\w.-]*|[\w-]+\.(?:{_EXT}))(?![\w/])")
TICK_RE = re.compile(r"`([^`\n]{3,60})`")
IDENT_RE = re.compile(r"^[A-Za-z_][\w:.]*$")


def _tracked(repo: Path) -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=repo, capture_output=True, text=True, check=True,
                         stdin=subprocess.DEVNULL).stdout
    return set(out.split())


def _grep_files(repo: Path, token: str, cap: int) -> list[str]:
    # The explicit "." is load-bearing: given no path, rg searches stdin, which blocks forever
    # whenever the dispatcher's stdin is an open pipe rather than a tty. DEVNULL closes the
    # same hole from the other side. A path argument makes rg prefix every hit with "./",
    # which `git ls-files` never does, so strip it before the tracked-set filter in predict().
    p = subprocess.run(["rg", "-l", "--fixed-strings", "--", token, "."], cwd=repo,
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    hits = [h[2:] if h.startswith("./") else h for h in p.stdout.split() if h]
    return hits[:cap]


def predict(repo, title: str, body: str, max_files: int = 40, max_hits_per_token: int = 20) -> frozenset[str]:
    repo = Path(repo)
    text = f"{title}\n{body or ''}"
    tracked = _tracked(repo)
    files: set[str] = set()
    for m in PATH_RE.finditer(text):
        cand = m.group(1).strip("./").rstrip("/")
        if not cand:
            continue
        if cand in tracked:
            files.add(cand)
        else:
            under = {t for t in tracked if t.startswith(cand + "/")}
            files |= under
    for m in TICK_RE.finditer(text):
        tok = m.group(1).strip()
        if "/" in tok or "." in tok and tok.split(".")[-1] in _EXT.split("|"):
            continue                      # path-like tokens were handled above
        if not IDENT_RE.match(tok) or len(tok) < 4:
            continue
        files.update(h for h in _grep_files(repo, tok, max_hits_per_token) if h in tracked)
    if not files or len(files) > max_files:
        return WILDCARD
    return frozenset(files)


def overlaps(a: frozenset, b: frozenset) -> bool:
    if a == WILDCARD or b == WILDCARD:
        return True
    return bool(a & b)
