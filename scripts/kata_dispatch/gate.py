"""Run /verify-branch headlessly from the primary checkout and read its artifacts, fail closed.

The skill writes `<primary>/.scratchpad/{YYYYMMDD}-verify-branch-{auditor}-{branch}.md`, each
ending in `VERDICT: PASS|BLOCK`. Three artifacts; the test-quality one is the
lead's `SKIPPED BY LEAD — NO-TESTS-IN-DIFF` record when the diff touches no tests. A missing
artifact or a missing VERDICT line is a BLOCK recorded as "no verdict", never a pass.

The verdict is read from the artifact's literal last line (as `tail -1` would), so a VERDICT line
quoted earlier in the body, or followed by any further line, does not count. The skill also writes
a common file `*vb-common*` whose line 1 is `Brief-token: <16 hex>`; every artifact must echo that
line on its line 2. An artifact whose line 2 matches no token from a common file written in this
gate session is scored as no verdict, and no usable common file at all is a BLOCK.
"""
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

AUDITORS = 3
VERDICT_RE = re.compile(r"^VERDICT:\s*(PASS|BLOCK)\s*$")
TOKEN_RE = re.compile(r"^Brief-token: [0-9a-f]{16}$")


@dataclass
class Verdict:
    passed: bool
    detail: str
    artifacts: list = field(default_factory=list)


def NO_GATE(*args, **kwargs) -> Verdict:
    return Verdict(True, "gate disabled", [])


def _artifacts_since(repo: Path, ref: str, branch: str, since: float) -> list[Path]:
    d = repo / ".scratchpad"
    if not d.is_dir():
        return []
    keys = {branch, branch.replace("/", "-")}
    out = []
    for p in d.glob("*verify-branch*.md"):
        # No slop on the mtime window: mtime resolution here is sub-millisecond (measured),
        # so no buffer is needed, and any widening would admit a prior run's overwritten
        # artifact for the same branch. Fail closed instead — a borderline timestamp reads
        # as missing, not as a stale pass.
        if p.stat().st_mtime >= since and any(k in p.name for k in keys):
            out.append(p)
    return sorted(out)


def _common_tokens_since(repo: Path, branch: str, since: float) -> set[str]:
    """Brief-token lines from the `*vb-common*` files this gate session wrote for the branch.
    Same branch-key and no-slop mtime window as _artifacts_since; a file whose line 1 is not an
    exact token line contributes nothing."""
    d = repo / ".scratchpad"
    if not d.is_dir():
        return set()
    keys = {branch, branch.replace("/", "-")}
    tokens = set()
    for p in d.glob("*vb-common*"):
        if p.stat().st_mtime >= since and any(k in p.name for k in keys):
            first = p.read_text(errors="replace").split("\n", 1)[0]
            if TOKEN_RE.match(first):
                tokens.add(first)
    return tokens


def _last_line_verdict(text: str):
    if text.endswith("\n"):
        text = text[:-1]
    m = VERDICT_RE.match(text.rsplit("\n", 1)[-1])
    return m.group(1) if m else None


# per gate session; up to three auditors run inside it (test-quality may be the lead's
# NO-TESTS-IN-DIFF skip record)
BUDGET_USD = 15.0


def run_gate(repo, ref: str, branch: str, target: str, model: str, log_path: Path,
             budget_usd: float = BUDGET_USD, timeout: int = 3600) -> Verdict:
    # budget_usd sits after log_path so landing.land's six positional args are unaffected; an
    # ungated session can outspend the whole run's worker budget on one branch. Exceeding it
    # exits non-zero, which the returncode check below already turns into a fail-closed BLOCK.
    repo = Path(repo)
    started = time.time()
    prompt = f"/verify-branch {target} kata#{ref} {branch}"
    with open(log_path, "ab") as logf:
        p = subprocess.run(["claude", "-p", prompt, "--model", model, "--max-budget-usd", str(budget_usd),
                            "--permission-mode", "bypassPermissions",
                            "--output-format", "stream-json", "--verbose", "--name", f"gate-{ref}"],
                           cwd=str(repo), stdin=subprocess.DEVNULL, stdout=logf, stderr=subprocess.STDOUT, timeout=timeout)
    arts = _artifacts_since(repo, ref, branch, started)
    tokens = _common_tokens_since(repo, branch, started)
    verdicts = {}
    bad_token = []
    for a in arts:
        text = a.read_text(errors="replace")
        lines = text.split("\n", 2)
        if len(lines) < 2 or lines[1] not in tokens:
            bad_token.append(a.name)
            verdicts[a.name] = None
        else:
            verdicts[a.name] = _last_line_verdict(text)
    missing = [n for n, v in verdicts.items() if v is None]
    if p.returncode != 0:
        return Verdict(False, f"gate session exited {p.returncode}: no verdict", [str(a) for a in arts])
    if not tokens:
        return Verdict(False, f"gate returned no verdict: no common file (vb-common) for {branch} written this session ({len(arts)}/{AUDITORS} artifacts)", [str(a) for a in arts])
    if bad_token:
        return Verdict(False, f"gate returned no verdict: line-2 token mismatch in {', '.join(bad_token)} ({len(arts)}/{AUDITORS} artifacts)", [str(a) for a in arts])
    if len(arts) < AUDITORS or missing:
        return Verdict(False, f"gate returned no verdict ({len(arts)}/{AUDITORS} artifacts, {len(missing)} without VERDICT)", [str(a) for a in arts])
    blocks = [n for n, v in verdicts.items() if v == "BLOCK"]
    if blocks:
        return Verdict(False, "BLOCK from " + ", ".join(blocks), [str(a) for a in arts])
    return Verdict(True, "PASS from all auditors", [str(a) for a in arts])
