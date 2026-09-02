import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from test_kata_dispatch_fakes import FAKE_CLAUDE_ESCALATE, install_fake_claude, make_repo  # noqa: E402

from kata_dispatch import state, worker  # noqa: E402

FAKE_CLAUDE_ARGS = r'''#!/usr/bin/env python3
import json, os, sys
print(json.dumps({"type": "probe", "argv": sys.argv[1:], "cwd": os.getcwd(), "env": {k: os.environ.get(k) for k in ("KATA_AUTHOR", "KATA_DISPATCH_MAIN_CHECKOUT")}, "stdin": sys.stdin.read()}))
print(json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 0.01, "is_error": False, "session_id": "s1", "result": "OUTCOME: reviewed-branch"}))
'''


def _cfg():
    return worker.Config(model="sonnet", budget_usd=3.0, use_systemd=False)


def test_spawn_creates_worktree_branch_and_record(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_claude(tmp_path, monkeypatch, FAKE_CLAUDE_ARGS)
    paths = state.Paths(repo)
    paths.ensure()
    rec, proc = worker.spawn(paths, "ab12", "claude-dispatch-r1-ab12", "r1", _cfg())
    assert proc.wait(timeout=30) == 0
    assert Path(rec.worktree) == paths.worktree("ab12") and Path(rec.worktree).is_dir()
    assert subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=rec.worktree, capture_output=True, text=True).stdout.strip() == "dispatch/ab12"
    assert state.AgentRecord.load(paths.agent("ab12")).pid == rec.pid
    probe = json.loads(Path(rec.log).read_text().splitlines()[0])
    argv = probe["argv"]
    assert argv[:2] == ["-p", worker.brief("ab12", "integration", "claude-dispatch-r1-ab12", rec.worktree, "r1", "sonnet")]
    for flag, val in (("--model", "sonnet"), ("--max-budget-usd", "3.0"), ("--permission-mode", "bypassPermissions"), ("--output-format", "stream-json")):
        assert argv[argv.index(flag) + 1] == val
    assert "--verbose" in argv and "--settings" in argv
    assert Path(probe["cwd"]) == Path(rec.worktree).resolve()
    assert probe["env"] == {"KATA_AUTHOR": "claude-dispatch-r1-ab12", "KATA_DISPATCH_MAIN_CHECKOUT": str(repo.resolve())}
    assert probe["stdin"] == ""
    settings = json.loads(Path(argv[argv.index("--settings") + 1]).read_text())
    hook = settings["hooks"]["PreToolUse"][0]
    assert hook["matcher"] == "Edit|Write|MultiEdit|NotebookEdit"
    assert hook["hooks"][0]["command"].endswith("preflight.py --hook")


def test_brief_carries_the_load_bearing_instructions():
    b = worker.brief("ab12", "integration", "claude-dispatch-r1-ab12", "/wt/ab12", "r1", "opus")
    assert b.startswith("/super-do ab12 integration")
    for must in ("do NOT merge", "do NOT run /verify-branch", "OUTCOME: reviewed-branch", "OUTCOME: escalated", "OUTCOME: no-change", "preflight.py", "kata unassign ab12", "Assisted-by: Claude:claude-opus"):
        assert must in b, must


def test_parse_result_reads_outcome_and_cost(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_claude(tmp_path, monkeypatch, FAKE_CLAUDE_ESCALATE)
    paths = state.Paths(repo)
    paths.ensure()
    rec, proc = worker.spawn(paths, "ab12", "a", "r1", _cfg())
    proc.wait(timeout=30)
    r = worker.parse_result(Path(rec.log))
    assert r == {"outcome": "escalated", "label": "needs-decision", "cost_usd": 0.1, "session_id": "fake-esc", "subtype": "success"}


def test_parse_result_without_result_line_is_unknown(tmp_path):
    log = tmp_path / "x.jsonl"
    log.write_text('{"type":"system"}\n')
    assert worker.parse_result(log)["outcome"] == "unknown"
