"""Shared fixtures for kata_dispatch tests: a temp git repo, a fake `kata`, a fake `claude`.

The fakes are real executables placed first on PATH so the code under test runs its
normal subprocess path. The fake kata keeps issue state in KATA_FAKE_DIR as one JSON
file per issue and guards `claim` with an O_EXCL owner file, so a concurrent claim race
against it is a real race, not a mocked one.
"""
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FAKE_KATA = r'''#!/usr/bin/env python3
import json, os, sys
D = os.environ["KATA_FAKE_DIR"]
LOG = os.path.join(D, "calls.log")
def actor():
    if "--as" in sys.argv: return sys.argv[sys.argv.index("--as") + 1]
    return os.environ.get("KATA_AUTHOR", "claude")
def load(ref):
    p = os.path.join(D, ref + ".json")
    return json.load(open(p)) if os.path.exists(p) else None
def save(ref, d): json.dump(d, open(os.path.join(D, ref + ".json"), "w"))
with open(LOG, "a") as f: f.write(json.dumps(sys.argv[1:]) + "\n")
cmd = sys.argv[1]
def positionals(args):
    out, skip = [], False
    for a in args:
        if skip: skip = False; continue
        if a in ("--as", "--body", "--comment", "--workspace"): skip = True; continue
        if a.startswith("--"): continue
        out.append(a)
    return out
pos = positionals(sys.argv[2:])
if cmd == "health":
    print("OK"); sys.exit(0)
if cmd == "ready":
    issues = []
    for n in sorted(os.listdir(D)):
        if n.endswith(".json"):
            i = json.load(open(os.path.join(D, n)))
            if i.get("status", "open") == "open": issues.append(i)
    print(json.dumps({"issues": issues})); sys.exit(0)
ref = pos[1] if cmd == "label" else pos[0]
i = load(ref)
if i is None:
    print("ERR not_found", file=sys.stderr); sys.exit(4)
if cmd == "show":
    labels = [{"label": l} for l in i.get("labels", [])] or None
    print(json.dumps({"issue": i, "labels": labels, "links": i.get("links", []), "comments": []})); sys.exit(0)
if cmd == "claim":
    a = actor()
    lock = os.path.join(D, ref + ".owner")
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, a.encode()); os.close(fd)
    except FileExistsError:
        cur = open(lock).read()
        if cur == a: print("OK claim changed=false"); sys.exit(0)
        print("ERR claim conflict: issue is already claimed by " + cur, file=sys.stderr); sys.exit(5)
    i["owner"] = a; save(ref, i); print("OK claim " + ref); sys.exit(0)
if cmd == "unassign":
    lock = os.path.join(D, ref + ".owner")
    if os.path.exists(lock): os.unlink(lock)
    i.pop("owner", None); save(ref, i); print("OK unassign"); sys.exit(0)
if cmd == "comment":
    i.setdefault("comments", []).append(sys.argv[sys.argv.index("--body") + 1]); save(ref, i); print("OK"); sys.exit(0)
if cmd == "label":
    i.setdefault("labels", []).append(pos[2]); save(ref, i); print("OK"); sys.exit(0)
print("ERR unknown " + cmd, file=sys.stderr); sys.exit(2)
'''

FAKE_CLAUDE_COMMIT = r'''#!/usr/bin/env python3
"""Fake worker: commits one file in cwd and prints a stream-json result."""
import json, os, subprocess, sys
ref = os.environ.get("FAKE_REF", "x")
open("worker-output.txt", "w").write("done " + ref)
subprocess.run(["git", "add", "worker-output.txt"], check=True)
subprocess.run(["git", "commit", "-q", "-s", "-m", "feat: fake work for " + ref], check=True)
print(json.dumps({"type": "system", "subtype": "init", "session_id": "fake-" + ref}))
print(json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 0.5, "is_error": False,
                  "session_id": "fake-" + ref, "result": "OUTCOME: reviewed-branch\nall good"}))
'''

FAKE_CLAUDE_ESCALATE = r'''#!/usr/bin/env python3
import json
print(json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 0.1, "is_error": False,
                  "session_id": "fake-esc", "result": "OUTCOME: escalated needs-decision\ntwo defensible options"}))
'''

FAKE_CLAUDE_COMMIT_THEN_ESCALATE = r'''#!/usr/bin/env python3
"""Fake worker: commits partial work, then escalates anyway. The branch is NOT reviewed."""
import json, os, subprocess
ref = os.environ.get("FAKE_REF", "x")
open("worker-output.txt", "w").write("partial " + ref)
subprocess.run(["git", "add", "worker-output.txt"], check=True)
subprocess.run(["git", "commit", "-q", "-s", "-m", "wip: partial work for " + ref], check=True)
print(json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 0.3, "is_error": False,
                  "session_id": "fake-" + ref, "result": "OUTCOME: escalated needs-decision\ntwo defensible options"}))
'''

FAKE_CLAUDE_COMMIT_THEN_BUDGET_ERROR = r'''#!/usr/bin/env python3
"""Fake worker: commits partial work, then dies over budget with no OUTCOME line at all."""
import json, os, subprocess
ref = os.environ.get("FAKE_REF", "x")
open("worker-output.txt", "w").write("partial " + ref)
subprocess.run(["git", "add", "worker-output.txt"], check=True)
subprocess.run(["git", "commit", "-q", "-s", "-m", "wip: partial work for " + ref], check=True)
print(json.dumps({"type": "result", "subtype": "error_max_budget_usd", "total_cost_usd": 15.0,
                  "is_error": True, "session_id": "fake-" + ref, "result": ""}))
'''

FAKE_CLAUDE_COMMIT_THEN_AMBIGUOUS = r'''#!/usr/bin/env python3
"""Fake worker: commits partial work, then ends with two disagreeing OUTCOME lines. Nothing
about this is a reviewed branch -- fail-closed to unknown, not to whichever line matched first."""
import json, os, subprocess
ref = os.environ.get("FAKE_REF", "x")
open("worker-output.txt", "w").write("partial " + ref)
subprocess.run(["git", "add", "worker-output.txt"], check=True)
subprocess.run(["git", "commit", "-q", "-s", "-m", "wip: partial work for " + ref], check=True)
print(json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 0.3, "is_error": False,
                  "session_id": "fake-" + ref,
                  "result": "Per the brief I should have ended with:\n  OUTCOME: reviewed-branch\n"
                            "but I hit a blocker instead.\nOUTCOME: escalated needs-decision\n"}))
'''

# Must equal the default token hard-coded in FAKE_CLAUDE_GATE_PASS below: tests that pre-write a
# common file the fake is expected to echo depend on it.
FAKE_GATE_TOKEN = "0123456789abcdef"

FAKE_CLAUDE_GATE_PASS = r'''#!/usr/bin/env python3
"""Fake gate, shaped like a /verify-branch session in <cwd>/.scratchpad.

By default it writes the common file `<YYYYMMDD>-vb-common-<branch>.md` (line 1
`Brief-token: <16 hex>`, then a heading) and three artifacts
`<YYYYMMDD>-verify-branch-<auditor>-<branch>.md` for auditors claims, tests, scope, each
`# audit` / the common file's line 1 / a body line / `VERDICT: <X>` as its last line.

Knobs (env, all off by default):
  FAKE_GATE_VERDICT=PASS|BLOCK   verdict written on every artifact's last line (default PASS)
  FAKE_GATE_COUNT=N              write only the first N artifacts (default 3)
  FAKE_GATE_ARGV_DUMP=<path>     dump this process's argv (JSON) to <path>
  FAKE_GATE_TOKEN=<hex>          token for the common file and the artifacts' echo
                                 (default 0123456789abcdef)
  FAKE_GATE_NO_COMMON=1          write no common file (artifacts still echo FAKE_GATE_TOKEN)
  FAKE_GATE_COMMON_BRANCH=<b>    name the common file for branch <b> instead of this one
  FAKE_GATE_WRONG_TOKEN=<aud>    auditor <aud>'s artifact echoes deadbeefdeadbeef on line 2
  FAKE_GATE_TRAILING=<aud>       auditor <aud>'s artifact has one more line after its VERDICT
                                 line; its text is FAKE_GATE_TRAILING_TEXT (default: blank)
  FAKE_GATE_QUOTED_BLOCK=1       every artifact quotes a `VERDICT: BLOCK` line in its body
                                 before its final VERDICT line
  FAKE_GATE_RERUN=1              also write `<YYYYMMDD>-vb-common-<branch>-rerun.md` with token
                                 fedcba9876543210; the claims artifact echoes the first token,
                                 tests and scope echo the rerun token
  FAKE_GATE_LINE2_SUFFIX=<aud>   auditor <aud>'s line 2 is the right token line followed by
                                 FAKE_GATE_LINE2_SUFFIX_TEXT (default: one space)
  FAKE_GATE_ONE_LINE=<aud>       auditor <aud>'s artifact is the single line `VERDICT: <X>`
                                 with no trailing newline (no line 2 at all)
"""
import json, os, sys, time
env = os.environ.get
prompt = sys.argv[sys.argv.index("-p") + 1]
branch = prompt.split()[-1].replace("/", "-")
d = os.path.join(os.getcwd(), ".scratchpad"); os.makedirs(d, exist_ok=True)
day = time.strftime("%Y%m%d")
verdict = env("FAKE_GATE_VERDICT", "PASS")
n = int(env("FAKE_GATE_COUNT", "3"))
argv_dump = env("FAKE_GATE_ARGV_DUMP")
if argv_dump:
    open(argv_dump, "w").write(json.dumps(sys.argv[1:]))
token = env("FAKE_GATE_TOKEN", "0123456789abcdef")
rerun_token = "fedcba9876543210" # notsecret
common_branch = env("FAKE_GATE_COMMON_BRANCH", branch).replace("/", "-")
if not env("FAKE_GATE_NO_COMMON"):
    open(os.path.join(d, day + "-vb-common-" + common_branch + ".md"), "w").write(
        "Brief-token: " + token + "\n# common context\n")
    if env("FAKE_GATE_RERUN"):
        open(os.path.join(d, day + "-vb-common-" + common_branch + "-rerun.md"), "w").write(
            "Brief-token: " + rerun_token + "\n# common context (rerun)\n")
for a in ["claims", "tests", "scope"][:n]:
    t = token
    if env("FAKE_GATE_RERUN") and a != "claims":
        t = rerun_token
    if env("FAKE_GATE_WRONG_TOKEN") == a:
        t = "deadbeefdeadbeef"
    body = "| finding | evidence |\n"
    if env("FAKE_GATE_QUOTED_BLOCK"):
        body += "Quoted from a prior run as evidence:\nVERDICT: BLOCK\n"
    line2 = "Brief-token: " + t
    if env("FAKE_GATE_LINE2_SUFFIX") == a:
        line2 += env("FAKE_GATE_LINE2_SUFFIX_TEXT", " ")
    text = "# audit\n" + line2 + "\n" + body + "VERDICT: " + verdict + "\n"
    if env("FAKE_GATE_TRAILING") == a:
        text += env("FAKE_GATE_TRAILING_TEXT", "") + "\n"
    if env("FAKE_GATE_ONE_LINE") == a:
        text = "VERDICT: " + verdict
    open(os.path.join(d, day + "-verify-branch-" + a + "-" + branch + ".md"), "w").write(text)
print(json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 1.0, "is_error": False, "session_id": "fake-gate", "result": verdict}))
'''


def _write_exe(path: Path, text: str) -> Path:
    path.write_text(text)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def make_repo(tmp_path: Path, name: str = "proj") -> Path:
    repo = tmp_path / name
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo, check=True)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("def main():\n    return 1\n")
    (repo / "src" / "util.py").write_text("def helper():\n    return 2\n")
    (repo / "README.md").write_text("# proj\n")
    (repo / ".gitignore").write_text(".scratchpad\n")
    subprocess.run(["git", "add", "src", "README.md", ".gitignore"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
    subprocess.run(["git", "branch", "integration", "main"], cwd=repo, check=True)
    return repo


def install_fake_kata(tmp_path: Path, monkeypatch, issues=None) -> Path:
    state = tmp_path / "kata-state"
    state.mkdir(exist_ok=True)
    bindir = tmp_path / "bin"
    bindir.mkdir(exist_ok=True)
    _write_exe(bindir / "kata", FAKE_KATA)
    monkeypatch.setenv("KATA_FAKE_DIR", str(state))
    monkeypatch.setenv("PATH", f"{bindir}:{os.environ['PATH']}")
    monkeypatch.delenv("KATA_AUTHOR", raising=False)
    for i in issues or []:
        (state / f"{i['short_id']}.json").write_text(json.dumps(i))
    return state


def install_fake_claude(tmp_path: Path, monkeypatch, script: str = FAKE_CLAUDE_COMMIT) -> Path:
    bindir = tmp_path / "bin"
    bindir.mkdir(exist_ok=True)
    exe = _write_exe(bindir / "claude", script)
    monkeypatch.setenv("PATH", f"{bindir}:{os.environ['PATH']}")
    return exe


def kata_calls(state: Path):
    log = state / "calls.log"
    return [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []


def test_fakes_smoke(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    assert (repo / "src" / "app.py").exists()
    state = install_fake_kata(tmp_path, monkeypatch, [{"short_id": "ab12", "title": "t", "body": "b"}])
    out = subprocess.run(["kata", "claim", "ab12", "--as", "A"], capture_output=True, text=True)
    assert out.returncode == 0
    out = subprocess.run(["kata", "claim", "ab12", "--as", "B"], capture_output=True, text=True)
    assert out.returncode == 5 and "already claimed by A" in out.stderr
    assert kata_calls(state)[0][0] == "claim"
