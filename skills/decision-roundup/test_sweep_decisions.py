"""Tests for the cross-project decision sweep.

The load-bearing behaviour is the client-side `deferred` exclusion. kata honors only the
first --label/--no-label flag, so the exclusion cannot be pushed into the query; if this
filter regresses, a parked issue is reported as a stalled decision. That is exactly the
error this script was written to prevent (alexandria f16t, 2026-08-15).
"""

from __future__ import annotations

import datetime as dt

import sweep_decisions as sd


NOW = dt.datetime(2026, 8, 15, tzinfo=dt.timezone.utc)


def issue(short_id, *, title="t", created="2026-08-01T00:00:00Z", labels=None, metadata=None):
    return {
        "short_id": short_id,
        "title": title,
        "created_at": created,
        "labels": labels if labels is not None else ["needs-decision"],
        "metadata": metadata or {},
    }


def run(monkeypatch, capsys, per_project, argv=(), errors=None):
    errors = errors or {}
    monkeypatch.setattr(sd, "projects", lambda: list(per_project))

    def fake_issues_for(project, label):
        if project in errors:
            return [], errors[project]
        return per_project[project], None

    monkeypatch.setattr(sd, "issues_for", fake_issues_for)
    monkeypatch.setattr(sd.dt, "datetime", _FrozenDatetime)
    monkeypatch.setattr(sd.sys, "argv", ["sweep_decisions.py", *argv])
    sd.main()
    return capsys.readouterr().out


_REAL_DATETIME = dt.datetime


class _FrozenDatetime(_REAL_DATETIME):
    """Freezes now() only.

    fromisoformat must delegate to the class captured *before* monkeypatching:
    the patch replaces `sd.dt.datetime`, and `sd.dt` is the shared datetime
    module, so referring to `dt.datetime` in here resolves back to this class
    and recurses.
    """

    @classmethod
    def now(cls, tz=None):
        return NOW

    @classmethod
    def fromisoformat(cls, s):
        return _REAL_DATETIME.fromisoformat(s)


class TestDeferredExclusion:
    def test_deferred_issue_is_kept_out_of_the_standing_list(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            {
                "alexandria": [
                    issue("f16t", labels=["needs-decision", "deferred"],
                          metadata={"defer_until": '"2026-10-02"'}),
                    issue("qxq2"),
                ]
            },
        )
        standing, deferred = out.split("## Deferred")
        assert "qxq2" in standing
        assert "f16t" not in standing, "a deferred issue must not read as awaiting a ruling"
        assert "f16t" in deferred
        assert "2026-10-02" in deferred

    def test_standing_count_excludes_deferred(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            {"p": [issue("aaaa"), issue("bbbb", labels=["needs-decision", "deferred"])]},
        )
        assert "Awaiting a ruling (1)" in out

    def test_include_deferred_flag_folds_them_back_in(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            {"p": [issue("bbbb", labels=["needs-decision", "deferred"])]},
            argv=["--include-deferred"],
        )
        assert "Awaiting a ruling (1)" in out
        assert "## Deferred" not in out

    def test_deferred_without_a_date_is_flagged_not_silently_buried(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            {"p": [issue("bbbb", labels=["needs-decision", "deferred"])]},
        )
        assert "UNDATED" in out
        assert "nothing will bring this back" in out


class TestOrdering:
    def test_standing_sorted_oldest_first(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            {
                "p": [
                    issue("new", created="2026-08-14T00:00:00Z"),
                    issue("old", created="2026-07-01T00:00:00Z"),
                    issue("mid", created="2026-08-05T00:00:00Z"),
                ]
            },
        )
        assert out.index("`old`") < out.index("`mid`") < out.index("`new`")

    def test_age_is_reported_in_days(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, {"p": [issue("a", created="2026-08-05T00:00:00Z")]})
        assert "| 10d |" in out


class TestGapsAreNotZeroes:
    def test_unqueryable_project_is_reported_as_a_gap(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            {"good": [issue("aaaa")], "broken": []},
            errors={"broken": "project_not_initialized"},
        )
        assert "Could not query (1)" in out
        assert "broken" in out
        assert "project_not_initialized" in out
        assert "not a project with nothing in it" in out

    def test_broken_project_does_not_inflate_the_standing_count(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            {"good": [issue("aaaa")], "broken": []},
            errors={"broken": "boom"},
        )
        assert "Awaiting a ruling (1)" in out


class TestEmptyState:
    def test_no_standing_decisions_says_so_explicitly(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, {"p": []})
        assert "No standing" in out


class TestDeferUntilParsing:
    def test_strips_the_json_quoting_kata_stores(self):
        assert sd.defer_until({"metadata": {"defer_until": '"2026-10-02"'}}) == "2026-10-02"

    def test_absent_metadata_returns_none(self):
        assert sd.defer_until({"metadata": {}}) is None
        assert sd.defer_until({}) is None


class TestBriefLine:
    def test_reports_live_standing_count_not_just_elapsed_time(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            {
                "alexandria": [issue("qxq2", created="2026-07-25T00:00:00Z")],
                "pcitopo": [issue("6n1q", created="2026-08-01T00:00:00Z")],
            },
            argv=["--brief"],
        )
        assert out.startswith("DECISIONS standing=2")
        assert "oldest=21d(alexandria/qxq2)" in out
        assert "projects=2" in out
        assert "\n" in out and out.count("\n") == 1, "brief mode must emit exactly one line"

    def test_deferred_excluded_from_the_brief_count_too(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            {"p": [issue("a"), issue("b", labels=["needs-decision", "deferred"])]},
            argv=["--brief"],
        )
        assert "standing=1" in out

    def test_zero_standing_omits_the_oldest_field(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, {"p": []}, argv=["--brief"])
        assert "standing=0" in out
        assert "oldest=" not in out

    def test_unqueryable_projects_surface_in_the_brief(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            {"good": [issue("a")], "broken": []},
            errors={"broken": "project_not_initialized"},
            argv=["--brief"],
        )
        assert "unqueryable=1" in out

    def test_missing_stamp_reports_never(self, monkeypatch, capsys, tmp_path):
        monkeypatch.setattr(sd, "STAMP", str(tmp_path / "absent"))
        out = run(monkeypatch, capsys, {"p": [issue("a")]}, argv=["--brief"])
        assert "last=never" in out

    def test_stamp_age_reported_in_days(self, monkeypatch, capsys, tmp_path):
        stamp = tmp_path / "last-roundup"
        stamp.write_text("2026-08-05\n")
        monkeypatch.setattr(sd, "STAMP", str(stamp))
        out = run(monkeypatch, capsys, {"p": [issue("a")]}, argv=["--brief"])
        assert "last=2026-08-05 days_ago=10" in out

    def test_unreadable_stamp_does_not_crash_the_startup_check(self, monkeypatch, capsys, tmp_path):
        stamp = tmp_path / "last-roundup"
        stamp.write_text("not-a-date\n")
        monkeypatch.setattr(sd, "STAMP", str(stamp))
        out = run(monkeypatch, capsys, {"p": [issue("a")]}, argv=["--brief"])
        assert "days_ago=?" in out
