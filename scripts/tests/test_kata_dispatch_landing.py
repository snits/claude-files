import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from test_kata_dispatch_fakes import (FAKE_CLAUDE_ESCALATE, FAKE_CLAUDE_GATE_PASS, install_fake_claude,  # noqa: E402
                                      install_fake_kata, make_repo)

from kata_dispatch import claims, gate, landing, state, worker  # noqa: E402
from kata_dispatch.kata import KataClient  # noqa: E402

ISSUE = {"short_id": "ab12", "title": "t", "body": "b"}


def _setup(tmp_path, monkeypatch, script):
    repo = make_repo(tmp_path)
    install_fake_kata(tmp_path, monkeypatch, [ISSUE])
    install_fake_claude(tmp_path, monkeypatch, script)
    paths = state.Paths(repo)
    paths.ensure()
    landing.ensure_integration(paths)
    k = KataClient(repo)
    assert claims.acquire(paths, "ab12", "claude-dispatch-r1-ab12", k)
    monkeypatch.setenv("FAKE_REF", "ab12")
    rec, proc = worker.spawn(paths, "ab12", "claude-dispatch-r1-ab12", "r1", worker.Config(use_systemd=False))
    proc.wait(timeout=30)
    return repo, paths, k, rec


def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def test_committed_branch_lands_on_integration_and_cleans_up(tmp_path, monkeypatch):
    from test_kata_dispatch_fakes import FAKE_CLAUDE_COMMIT
    repo, paths, k, rec = _setup(tmp_path, monkeypatch, FAKE_CLAUDE_COMMIT)
    rec = landing.land(paths, rec, k, gate.NO_GATE)
    assert rec.state == "done" and rec.outcome == "merged"
    assert _git(["rev-list", "--count", "main..integration"], repo) == "2"   # worker commit + merge commit
    assert _git(["log", "-1", "--format=%P", "integration"], repo).count(" ") == 1, "must be a --no-ff merge commit"
    assert "Signed-off-by" in _git(["log", "-1", "--format=%B", "integration"], repo)
    assert not Path(rec.worktree).exists()
    assert _git(["branch", "--list", "dispatch/ab12"], repo) == ""
    assert not paths.lock("ab12").exists() and k.owner("ab12") is None
    assert rec.merge_commit and rec.cost_usd == 0.5


def test_empty_branch_is_recorded_as_escalated_and_cleaned(tmp_path, monkeypatch):
    repo, paths, k, rec = _setup(tmp_path, monkeypatch, FAKE_CLAUDE_ESCALATE)
    rec = landing.land(paths, rec, k, gate.NO_GATE)
    assert rec.state == "escalated" and "needs-decision" in rec.outcome
    assert not Path(rec.worktree).exists() and _git(["branch", "--list", "dispatch/ab12"], repo) == ""
    assert k.owner("ab12") is None
    assert _git(["rev-list", "--count", "main..integration"], repo) == "0"


def test_gate_block_keeps_worktree_and_labels(tmp_path, monkeypatch):
    from test_kata_dispatch_fakes import FAKE_CLAUDE_COMMIT
    repo, paths, k, rec = _setup(tmp_path, monkeypatch, FAKE_CLAUDE_COMMIT)
    blocked = lambda *a, **kw: gate.Verdict(False, "auditor tests: BLOCK", [])
    rec = landing.land(paths, rec, k, blocked)
    assert rec.state == "blocked"
    assert Path(rec.worktree).exists() and _git(["branch", "--list", "dispatch/ab12"], repo) != ""
    assert "needs-review" in k.labels("ab12") and k.owner("ab12") is None
    assert _git(["rev-list", "--count", "main..integration"], repo) == "0"


def test_rebase_conflict_keeps_worktree_and_labels(tmp_path, monkeypatch):
    from test_kata_dispatch_fakes import FAKE_CLAUDE_COMMIT
    repo, paths, k, rec = _setup(tmp_path, monkeypatch, FAKE_CLAUDE_COMMIT)
    # integration moves on the same file the worker created
    iw = paths.integration_worktree
    (iw / "worker-output.txt").write_text("conflicting\n")
    subprocess.run(["git", "add", "worker-output.txt"], cwd=iw, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "conflict"], cwd=iw, check=True)
    rec = landing.land(paths, rec, k, gate.NO_GATE)
    assert rec.state == "blocked" and "rebase" in rec.outcome
    assert Path(rec.worktree).exists() and "needs-review" in k.labels("ab12")
    rebase_dir = _git(["rev-parse", "--git-path", "rebase-merge"], rec.worktree)
    assert not (Path(rec.worktree) / rebase_dir).exists() and not Path(rebase_dir).exists(), "rebase must be aborted"


def test_real_gate_reads_artifacts_fail_closed(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    install_fake_claude(tmp_path, monkeypatch, FAKE_CLAUDE_GATE_PASS)
    v = gate.run_gate(repo, "ab12", "dispatch/ab12", "integration", "sonnet", tmp_path / "gate.jsonl")
    assert v.passed and len(v.artifacts) == 3
    monkeypatch.setenv("FAKE_GATE_VERDICT", "BLOCK")
    v = gate.run_gate(repo, "ab12", "dispatch/ab12", "integration", "sonnet", tmp_path / "gate2.jsonl")
    assert not v.passed and "BLOCK" in v.detail
    monkeypatch.setenv("FAKE_GATE_VERDICT", "PASS")
    monkeypatch.setenv("FAKE_GATE_COUNT", "2")
    v = gate.run_gate(repo, "ab12", "dispatch/ab12", "integration", "sonnet", tmp_path / "gate3.jsonl")
    assert not v.passed and "no verdict" in v.detail
