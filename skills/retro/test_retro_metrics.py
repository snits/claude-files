"""Tests for retro pattern metrics."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
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


def make_patterns() -> list[rm.Pattern]:
    return [
        rm.Pattern("worktree-guard-shape", re.compile("too complex to verify"), "isolated", [rm.Remedy("8j5h")]),
        rm.Pattern("sleep-block", re.compile(r"Blocked: sleep \d+"), "ran_bash", [rm.Remedy("note", dt.date(2026, 8, 1))]),
        rm.Pattern("classifier-denial", re.compile("auto mode classifier"), "any", []),
    ]


def make_session(version="2.1.259", interactive=True, isolated=False, ran_bash=False, errors=()):
    return rm.SessionMetrics(Path("/x"), version, interactive, isolated, ran_bash, list(errors))


ROW_KW = dict(window_start="2026-09-01T00:00:00Z", window_end="2026-09-07T00:00:00Z",
              computed_at="2026-09-07T00:00:01Z", registry_sha256="ab" * 32)


def test_build_row_counts_hits_and_eligible_per_version():
    sessions = [
        make_session(isolated=True, ran_bash=True, errors=[GUARD, GUARD, SLEEP]),
        make_session(isolated=True, ran_bash=True),
        make_session(version="2.1.258", ran_bash=True, errors=[SLEEP]),
        make_session(interactive=False, isolated=True, errors=[GUARD]),  # headless: ignored
    ]
    row = rm.build_row(sessions, make_patterns(), landed=lambda ref: None, **ROW_KW)
    assert row["sessions_interactive"] == 3
    guard = row["patterns"]["worktree-guard-shape"]["versions"]
    assert guard == {"2.1.259": {"hits": 2, "eligible": 2}}
    sleep = row["patterns"]["sleep-block"]["versions"]
    assert sleep == {"2.1.259": {"hits": 1, "eligible": 2}, "2.1.258": {"hits": 1, "eligible": 1}}
    assert row["patterns"]["classifier-denial"]["versions"] == {
        "2.1.259": {"hits": 0, "eligible": 2},
        "2.1.258": {"hits": 0, "eligible": 1},
    }


def test_build_row_hits_only_count_in_eligible_sessions():
    # A guard string in a session the detector does not consider isolated is a quote, not a refusal.
    sessions = [make_session(isolated=False, ran_bash=True, errors=[GUARD])]
    row = rm.build_row(sessions, make_patterns(), landed=lambda ref: None, **ROW_KW)
    assert row["patterns"]["worktree-guard-shape"]["versions"] == {}


def test_build_row_remedy_landed_prefers_kata_then_registry():
    lookups = {"8j5h": dt.date(2026, 9, 3)}
    row = rm.build_row([make_session()], make_patterns(), landed=lookups.get, **ROW_KW)
    assert row["patterns"]["worktree-guard-shape"]["remedies"] == [
        {"ref": "8j5h", "landed": "2026-09-03", "source": "kata"}
    ]
    assert row["patterns"]["sleep-block"]["remedies"] == [
        {"ref": "note", "landed": "2026-08-01", "source": "registry"}
    ]


def test_build_row_unlanded_remedy_has_no_date():
    patterns = [rm.Pattern("p", re.compile("x"), "any", [rm.Remedy("open1")])]
    row = rm.build_row([make_session()], patterns, landed=lambda ref: None, **ROW_KW)
    assert row["patterns"]["p"]["remedies"] == [{"ref": "open1", "landed": None, "source": "none"}]


def test_build_row_carries_window_and_hash():
    row = rm.build_row([], make_patterns(), landed=lambda ref: None, **ROW_KW)
    assert row["window_start"] == ROW_KW["window_start"]
    assert row["registry_sha256"] == ROW_KW["registry_sha256"]
    assert row["stale_registry"] is False
    assert json.loads(json.dumps(row)) == row


def fake_run(payload: dict | None, returncode=0):
    def run(cmd, **kw):
        out = json.dumps(payload) if payload is not None else ""
        return subprocess.CompletedProcess(cmd, returncode, stdout=out, stderr="")
    return run


def test_landed_date_reads_closed_at():
    run = fake_run({"issue": {"status": "closed", "closed_at": "2026-09-03T00:00:07.439Z"}})
    assert rm.landed_date("8j5h", run=run) == dt.date(2026, 9, 3)


def test_landed_date_open_issue_is_none():
    run = fake_run({"issue": {"status": "open", "closed_at": None}})
    assert rm.landed_date("wqvh", run=run) is None


def test_landed_date_unresolvable_ref_is_none():
    assert rm.landed_date("coach-hook", run=fake_run(None, returncode=3)) is None


def test_landed_date_passes_workspace():
    seen = {}
    def run(cmd, **kw):
        seen["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 3, stdout="", stderr="")
    rm.landed_date("x", workspace=Path("/w"), run=run)
    assert seen["cmd"] == ["kata", "show", "x", "--json", "--workspace", "/w"]


@pytest.mark.parametrize(
    "payload",
    [{"issue": None}, {"issue": "x"}, {"nope": 1}, {"issue": {"status": "closed", "closed_at": "garbage"}},
     {"issue": {"status": "closed", "closed_at": 42}}],
)
def test_landed_date_malformed_payload_is_none(payload):
    assert rm.landed_date("x", run=fake_run(payload)) is None


# --- append/rebuild ---

UTC = dt.timezone.utc


def ts(y, m, d, h=0):
    return dt.datetime(y, m, d, h, tzinfo=UTC)


def populate(projects_dir: Path, name: str, entries: list[dict], mtime: dt.datetime) -> Path:
    path = write_session(projects_dir / "proj", name, entries)
    os.utime(path, (mtime.timestamp(), mtime.timestamp()))
    return path


def test_append_first_row_uses_since(tmp_path):
    projects = tmp_path / "projects"
    populate(projects, "a.jsonl", [human("go"), tool_use("Bash"), tool_error(SLEEP)], ts(2026, 9, 3))
    reg = write_registry(tmp_path, MINIMAL_REGISTRY)
    metrics = tmp_path / "metrics.jsonl"
    row = rm.append_row(metrics_path=metrics, projects_dir=projects, registry_path=reg,
                        since=ts(2026, 9, 1), now=ts(2026, 9, 7), landed=lambda r: None)
    assert row["window_start"] == "2026-09-01T00:00:00Z"
    assert row["window_end"] == "2026-09-07T00:00:00Z"
    assert row["patterns"]["sleep-block"]["versions"] == {"2.1.259": {"hits": 1, "eligible": 1}}
    assert rm.read_rows(metrics) == [row]


def test_append_tiles_from_previous_row(tmp_path):
    projects = tmp_path / "projects"
    reg = write_registry(tmp_path, MINIMAL_REGISTRY)
    metrics = tmp_path / "metrics.jsonl"
    rm.append_row(metrics_path=metrics, projects_dir=projects, registry_path=reg,
                  since=ts(2026, 9, 1), now=ts(2026, 9, 7), landed=lambda r: None)
    populate(projects, "late.jsonl", [human("go"), tool_use("Bash"), tool_error(SLEEP)], ts(2026, 9, 8))
    row = rm.append_row(metrics_path=metrics, projects_dir=projects, registry_path=reg,
                        since=None, now=ts(2026, 9, 10), landed=lambda r: None)
    assert row["window_start"] == "2026-09-07T00:00:00Z"
    assert row["patterns"]["sleep-block"]["versions"]["2.1.259"]["hits"] == 1
    assert len(rm.read_rows(metrics)) == 2


def test_append_without_since_and_without_rows_fails(tmp_path):
    with pytest.raises(ValueError, match="--since"):
        rm.append_row(metrics_path=tmp_path / "m.jsonl", projects_dir=tmp_path, registry_path=write_registry(tmp_path, MINIMAL_REGISTRY),
                      since=None, now=ts(2026, 9, 10), landed=lambda r: None)


def test_sessions_after_window_end_are_excluded(tmp_path):
    projects = tmp_path / "projects"
    populate(projects, "future.jsonl", [human("go"), tool_use("Bash"), tool_error(SLEEP)], ts(2026, 9, 9))
    reg = write_registry(tmp_path, MINIMAL_REGISTRY)
    row = rm.append_row(metrics_path=tmp_path / "m.jsonl", projects_dir=projects, registry_path=reg,
                        since=ts(2026, 9, 1), now=ts(2026, 9, 7), landed=lambda r: None)
    assert row["sessions_interactive"] == 0


def test_rebuild_recomputes_under_current_registry(tmp_path):
    projects = tmp_path / "projects"
    populate(projects, "a.jsonl", [human("go"), tool_use("Bash"), tool_error(SLEEP)], ts(2026, 9, 3))
    reg = write_registry(tmp_path, MINIMAL_REGISTRY)
    metrics = tmp_path / "metrics.jsonl"
    old = rm.append_row(metrics_path=metrics, projects_dir=projects, registry_path=reg,
                        since=ts(2026, 9, 1), now=ts(2026, 9, 7), landed=lambda r: None)
    # Detector change: the regex now matches nothing.
    reg.write_text(MINIMAL_REGISTRY.replace('Blocked: sleep \\\\d+ followed by', "NEVER-MATCHES"))
    rows = rm.rebuild_rows(metrics_path=metrics, projects_dir=projects, registry_path=reg, landed=lambda r: None)
    assert rows[0]["registry_sha256"] != old["registry_sha256"]
    assert rows[0]["patterns"]["sleep-block"]["versions"] == {"2.1.259": {"hits": 0, "eligible": 1}}
    assert rows[0]["window_start"] == old["window_start"]
    assert rows[0]["stale_registry"] is False
    assert rm.read_rows(metrics) == rows


def test_rebuild_keeps_row_with_no_transcripts_and_flags_it(tmp_path):
    reg = write_registry(tmp_path, MINIMAL_REGISTRY)
    metrics = tmp_path / "metrics.jsonl"
    old = rm.append_row(metrics_path=metrics, projects_dir=tmp_path / "empty", registry_path=reg,
                        since=ts(2026, 9, 1), now=ts(2026, 9, 7), landed=lambda r: None)
    reg.write_text(MINIMAL_REGISTRY + "\n# changed\n")
    rows = rm.rebuild_rows(metrics_path=metrics, projects_dir=tmp_path / "empty", registry_path=reg, landed=lambda r: None)
    assert rows[0]["registry_sha256"] == old["registry_sha256"]
    assert rows[0]["stale_registry"] is True
    assert rows[0]["patterns"] == old["patterns"]


def make_row(end, versions, remedies=(), stale=False):
    return {
        "window_start": "2026-01-01T00:00:00Z", "window_end": f"{end}T00:00:00Z",
        "computed_at": f"{end}T00:00:01Z", "registry_sha256": "x" * 64, "stale_registry": stale,
        "sessions_interactive": 10,
        "patterns": {"worktree-guard-shape": {"versions": versions, "remedies": list(remedies)}},
    }


def test_trend_totals_and_rate():
    rows = [make_row("2026-09-02", {"2.1.235": {"hits": 326, "eligible": 140}})]
    out = rm.render_trend(rows)
    assert "## worktree-guard-shape" in out
    assert re.search(r"2026-09-02\s+326\s+140\s+2\.33", out)
    assert "2.1.235" not in out  # single version: no sub-row


def test_trend_version_subrows_when_mixed():
    rows = [make_row("2026-09-07", {"2.1.258": {"hits": 3, "eligible": 2}, "2.1.259": {"hits": 14, "eligible": 3}})]
    out = rm.render_trend(rows)
    assert re.search(r"2026-09-07\s+17\s+5\s+3\.40", out)
    assert re.search(r"^\s+2\.1\.258\s+3\s+2\s+1\.50", out, re.M)
    assert re.search(r"^\s+2\.1\.259\s+14\s+3\s+4\.67", out, re.M)


def test_trend_marks_first_window_after_landed():
    remedies = [{"ref": "8j5h", "landed": "2026-09-03", "source": "kata"}]
    rows = [
        make_row("2026-09-02", {"v": {"hits": 1, "eligible": 1}}, remedies),
        make_row("2026-09-07", {"v": {"hits": 1, "eligible": 1}}, remedies),
        make_row("2026-09-14", {"v": {"hits": 1, "eligible": 1}}, remedies),
    ]
    lines = rm.render_trend(rows).splitlines()
    marked = [l for l in lines if "◄ 8j5h landed 2026-09-03" in l]
    assert len(marked) == 1 and marked[0].startswith("2026-09-07")


def test_trend_zero_eligible_prints_dash():
    out = rm.render_trend([make_row("2026-09-02", {"v": {"hits": 0, "eligible": 0}})])
    assert re.search(r"2026-09-02\s+0\s+0\s+-", out)


def test_trend_flags_stale_rows():
    out = rm.render_trend([make_row("2026-09-02", {"v": {"hits": 1, "eligible": 1}}, stale=True)])
    assert re.search(r"^!2026-09-02", out, re.M)
    assert "computed under an older registry" in out


def test_trend_unlanded_remedy_has_no_marker():
    remedies = [{"ref": "open1", "landed": None, "source": "none"}]
    out = rm.render_trend([make_row("2026-09-02", {"v": {"hits": 1, "eligible": 1}}, remedies)])
    assert "◄" not in out
