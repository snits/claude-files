"""Tests for retro pattern metrics."""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import pytest

import retro_metrics as rm


def write_registry(directory: Path, text: str) -> Path:
    path = directory / "patterns.toml"
    path.write_text(text)
    return path


MINIMAL_REGISTRY = """
[[pattern]]
name = "sleep-block"
detector = "Blocked: sleep \\\\d+ followed by"
eligible = "ran_bash"
remedies = [{ ref = "abcd" }, { ref = "monitor-note", landed = "2026-08-01" }]
"""


def test_load_registry_parses_pattern(tmp_path):
    patterns = rm.load_registry(write_registry(tmp_path, MINIMAL_REGISTRY))
    assert [p.name for p in patterns] == ["sleep-block"]
    p = patterns[0]
    assert p.eligible == "ran_bash"
    assert p.detector.search("<tool_use_error>Blocked: sleep 60 followed by: true")
    assert p.remedies[0] == rm.Remedy(ref="abcd", landed=None)
    assert p.remedies[1] == rm.Remedy(ref="monitor-note", landed=dt.date(2026, 8, 1))


def test_load_registry_rejects_unknown_eligibility(tmp_path):
    bad = MINIMAL_REGISTRY.replace('eligible = "ran_bash"', 'eligible = "sometimes"')
    with pytest.raises(ValueError, match="eligible"):
        rm.load_registry(write_registry(tmp_path, bad))


def test_load_registry_rejects_duplicate_names(tmp_path):
    with pytest.raises(ValueError, match="duplicate"):
        rm.load_registry(write_registry(tmp_path, MINIMAL_REGISTRY + MINIMAL_REGISTRY))


def test_load_registry_rejects_remedy_without_ref(tmp_path):
    bad = MINIMAL_REGISTRY.replace('{ ref = "abcd" }', '{ landed = "2026-08-01" }')
    with pytest.raises(ValueError, match="ref"):
        rm.load_registry(write_registry(tmp_path, bad))


def test_registry_hash_changes_with_content(tmp_path):
    path = write_registry(tmp_path, MINIMAL_REGISTRY)
    before = rm.registry_hash(path)
    path.write_text(MINIMAL_REGISTRY.replace("sleep-block", "nap-block"))
    assert rm.registry_hash(path) != before
    assert len(before) == 64


def test_shipped_registry_loads():
    patterns = rm.load_registry(rm.REGISTRY_PATH)
    names = {p.name for p in patterns}
    assert names == {
        "worktree-guard-shape",
        "worktree-cwd-trap",
        "sleep-block",
        "eval-eq-error",
        "classifier-denial",
    }


# --- transcript builders, mirroring test_mine_transcripts.py ---

def line(entry: dict, version="2.1.259", cwd="/home/j/proj") -> dict:
    return {"version": version, "cwd": cwd, **entry}


def human(text, **kw):
    return line({"type": "user", "message": {"role": "user", "content": text}}, **kw)


def tool_use(name, **kw):
    return line(
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "tool_use", "id": "toolu_1", "name": name, "input": {}}],
            },
        },
        **kw,
    )


def tool_error(text, **kw):
    return line(
        {
            "type": "user",
            "message": {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "toolu_1", "is_error": True, "content": text}
                ],
            },
        },
        **kw,
    )


def env_snapshot(is_worktree: bool, **kw):
    return line(
        {"type": "attachment", "attachment": {"type": "environment", "snapshot": {"isWorktree": is_worktree}}},
        **kw,
    )


def write_session(directory: Path, name: str, entries: list[dict]) -> Path:
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    return path


GUARD = (
    "This session is isolated in the worktree /home/j/proj/.claude/worktrees/x, but this command "
    "names git in a form too complex to verify that it stays inside the worktree. Refusing to run it"
)
SLEEP = "<tool_use_error>Blocked: sleep 60 followed by: true. To wait for a condition, use Monitor"


def test_scan_reads_version_from_first_versioned_line(tmp_path):
    path = write_session(tmp_path, "s.jsonl", [{"type": "mode", "mode": "x"}, human("hi", version="2.1.258")])
    facts = rm.scan_metrics_session(path)
    assert facts.version == "2.1.258"


def test_scan_unknown_version_when_absent(tmp_path):
    path = write_session(tmp_path, "s.jsonl", [{"type": "user", "message": {"role": "user", "content": "hi"}}])
    assert rm.scan_metrics_session(path).version == "unknown"


def test_scan_interactive_requires_a_human_turn(tmp_path):
    headless = write_session(tmp_path, "h.jsonl", [tool_use("Bash"), tool_error(SLEEP)])
    assert rm.scan_metrics_session(headless).interactive is False
    interactive = write_session(tmp_path, "i.jsonl", [human("go"), tool_use("Bash")])
    assert rm.scan_metrics_session(interactive).interactive is True


def test_scan_harness_turns_are_not_human(tmp_path):
    path = write_session(tmp_path, "s.jsonl", [human("<system-reminder>x</system-reminder>")])
    assert rm.scan_metrics_session(path).interactive is False


def test_scan_ran_bash(tmp_path):
    with_bash = write_session(tmp_path, "b.jsonl", [human("go"), tool_use("Bash")])
    without = write_session(tmp_path, "r.jsonl", [human("go"), tool_use("Read")])
    assert rm.scan_metrics_session(with_bash).ran_bash is True
    assert rm.scan_metrics_session(without).ran_bash is False


@pytest.mark.parametrize(
    "entries",
    [
        [human("go"), env_snapshot(True)],
        [human("go"), tool_use("EnterWorktree")],
        [human("go"), tool_use("Bash", cwd="/home/j/proj/.claude/worktrees/task-1")],
        [human("go"), tool_use("Bash", cwd="/home/j/proj/.worktrees/task-1")],
    ],
)
def test_scan_isolated_signals(tmp_path, entries):
    assert rm.scan_metrics_session(write_session(tmp_path, "s.jsonl", entries)).isolated is True


def test_scan_not_isolated_by_default(tmp_path):
    path = write_session(tmp_path, "s.jsonl", [human("go"), env_snapshot(False), tool_use("Bash")])
    assert rm.scan_metrics_session(path).isolated is False


def test_scan_collects_error_texts(tmp_path):
    path = write_session(tmp_path, "s.jsonl", [human("go"), tool_use("Bash"), tool_error(GUARD), tool_error(SLEEP)])
    assert rm.scan_metrics_session(path).errors == [GUARD, SLEEP]


def test_scan_folds_subagent_transcripts_into_parent(tmp_path):
    parent = write_session(tmp_path, "abc.jsonl", [human("go"), tool_use("Agent")])
    write_session(tmp_path / "abc" / "subagents", "agent-1.jsonl", [tool_use("Bash", cwd="/x/.claude/worktrees/t"), tool_error(GUARD)])
    facts = rm.scan_metrics_session(parent)
    assert facts.interactive is True
    assert facts.isolated is True
    assert facts.ran_bash is True
    assert facts.errors == [GUARD]


def test_subagent_files_lists_only_that_sessions_dir(tmp_path):
    parent = write_session(tmp_path, "abc.jsonl", [human("go")])
    a = write_session(tmp_path / "abc" / "subagents", "agent-1.jsonl", [])
    write_session(tmp_path / "other" / "subagents", "agent-2.jsonl", [])
    assert rm.subagent_files(parent) == [a]
