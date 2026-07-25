"""Tests for the compaction hint channel.

Exercised against a real hints directory under tmp_path — no mocks. The hook
half is tested through `run_hook`, which takes the raw stdin text a PreCompact
hook receives and returns exactly what the script writes to stdout.
"""
import json
import time

import pytest

from compact_hint import run_hook, set_hint, sweep

SESSION = "19c6faba-0441-425d-a3ea-f34c4b68f563"
OTHER_SESSION = "00000000-1111-2222-3333-444444444444"


def hook_input(session_id=SESSION, trigger="manual", custom_instructions=None):
    return json.dumps(
        {
            "session_id": session_id,
            "hook_event_name": "PreCompact",
            "trigger": trigger,
            "custom_instructions": custom_instructions,
        }
    )


def test_hint_set_in_a_session_is_returned_to_that_session(tmp_path):
    set_hint(tmp_path, SESSION, "workflow wf_abc is still running")
    assert run_hook(hook_input(), tmp_path) == "workflow wf_abc is still running"


def test_no_hint_emits_nothing(tmp_path):
    assert run_hook(hook_input(), tmp_path) == ""


def test_typed_instructions_survive_when_no_hint_is_staged(tmp_path):
    """The harness merges hook output with what the user typed, so an empty
    emission leaves `/compact focus on X` exactly as the user wrote it."""
    assert run_hook(hook_input(custom_instructions="focus on X"), tmp_path) == ""


def test_hint_is_consumed_so_it_cannot_leak_into_a_later_compaction(tmp_path):
    set_hint(tmp_path, SESSION, "one-shot")
    assert run_hook(hook_input(), tmp_path) == "one-shot"
    assert run_hook(hook_input(), tmp_path) == ""


def test_another_sessions_hint_is_not_read(tmp_path):
    set_hint(tmp_path, OTHER_SESSION, "not yours")
    assert run_hook(hook_input(), tmp_path) == ""
    assert run_hook(hook_input(session_id=OTHER_SESSION), tmp_path) == "not yours"


def test_hint_applies_to_auto_compaction_too(tmp_path):
    set_hint(tmp_path, SESSION, "act on the notification")
    assert run_hook(hook_input(trigger="auto"), tmp_path) == "act on the notification"


def test_malformed_stdin_emits_nothing_instead_of_raising(tmp_path):
    assert run_hook("not json at all", tmp_path) == ""


def test_missing_session_id_emits_nothing(tmp_path):
    assert run_hook(json.dumps({"hook_event_name": "PreCompact"}), tmp_path) == ""


def test_missing_hints_directory_emits_nothing(tmp_path):
    assert run_hook(hook_input(), tmp_path / "never-created") == ""


def test_session_id_that_is_a_path_cannot_escape_the_hints_directory(tmp_path):
    with pytest.raises(ValueError):
        set_hint(tmp_path, "../../etc/passwd", "escape")
    assert run_hook(hook_input(session_id="../../etc/passwd"), tmp_path) == ""


def test_empty_hint_is_refused(tmp_path):
    with pytest.raises(ValueError):
        set_hint(tmp_path, SESSION, "   ")


def test_setting_a_hint_twice_replaces_rather_than_appends(tmp_path):
    set_hint(tmp_path, SESSION, "first")
    set_hint(tmp_path, SESSION, "second")
    assert run_hook(hook_input(), tmp_path) == "second"


def test_sweep_removes_orphaned_hints_but_keeps_fresh_ones(tmp_path):
    set_hint(tmp_path, SESSION, "fresh")
    set_hint(tmp_path, OTHER_SESSION, "abandoned")
    stale = tmp_path / f"{OTHER_SESSION}.txt"
    old = time.time() - 8 * 86400
    import os

    os.utime(stale, (old, old))

    sweep(tmp_path, max_age_days=7)

    assert run_hook(hook_input(session_id=OTHER_SESSION), tmp_path) == ""
    assert run_hook(hook_input(), tmp_path) == "fresh"
