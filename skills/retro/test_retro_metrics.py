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
