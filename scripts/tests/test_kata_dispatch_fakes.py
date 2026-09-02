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

FAKE_CLAUDE_GATE_PASS = r'''#!/usr/bin/env python3
"""Fake gate: writes three PASS artifacts into <cwd>/.scratchpad, named per /verify-branch."""
import json, os, sys, time
prompt = sys.argv[sys.argv.index("-p") + 1]
branch = prompt.split()[-1].replace("/", "-")
d = os.path.join(os.getcwd(), ".scratchpad"); os.makedirs(d, exist_ok=True)
verdict = os.environ.get("FAKE_GATE_VERDICT", "PASS")
n = int(os.environ.get("FAKE_GATE_COUNT", "3"))
for a in ["claims", "tests", "scope"][:n]:
    open(os.path.join(d, time.strftime("%Y%m%d") + "-verify-branch-" + a + "-" + branch + ".md"), "w").write("# audit\nVERDICT: " + verdict + "\n")
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
