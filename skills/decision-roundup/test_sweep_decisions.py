"""Tests for the cross-project decision sweep.

Three behaviours are load-bearing, and each fails toward "looks like nothing is there":

  * The `deferred` exclusion. A parked issue reported as a stalled decision is exactly the
    error this script was written to prevent (alexandria f16t, 2026-08-15).
  * The gap/zero distinction. projstat's feed says `tasks: null` for a project it could not
    ask and `blocked: []` for one it asked that holds nothing. Flattening those into one
    zero makes a blind run read as a quiet one.
  * Label-applied age. The feed's `age_days` counts from `created_at`; what matters is how
    long an issue has been waiting. fatescroll `kmgh` reads 159d by filing and 15d by label.
"""

from __future__ import annotations

import datetime as dt

import sweep_decisions as sd


NOW = dt.datetime(2026, 8, 15, tzinfo=dt.timezone.utc)


def item(short_id, *, title="t", age_days=10, labels=None, deferred=False, defer_until=None,
         created="2026-08-05T00:00:00Z"):
    return {
        "short_id": short_id,
        "title": title,
        "labels": labels if labels is not None else ["needs-decision"],
        "created_at": created,
        "age_days": age_days,
        "deferred": deferred,
        "defer_until": defer_until,
    }


def project(name, *, blocked=(), tasks_null=False, binding="bound", tasks_unknown=False):
    """One feed project record. tasks_null models a project that could not be asked."""
    return {
        "name": name,
        "path": f"/home/jsnitsel/devel/{name}",
        "kata_binding": binding,
        "tasks_unknown": tasks_unknown,
        "tasks": None if tasks_null else {"open": len(blocked), "blocked": list(blocked)},
    }


def run(monkeypatch, capsys, projects, argv=(), labeled=None):
    """Drive main() against a synthetic feed.

    `labeled` maps (project, label) -> {short_id: iso timestamp}, standing in for kata's
    event log. Absent entries make the sweep fall back to the feed's created-based age.
    """
    labeled = labeled or {}
    monkeypatch.setattr(sd, "feed", lambda: {"projects": list(projects)})
    monkeypatch.setattr(sd, "labeled_at", lambda p, l: labeled.get((p, l), {}))
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
            [project("alexandria", blocked=[
                item("f16t", deferred=True, defer_until="2026-10-02", age_days=116),
                item("qxq2"),
            ])],
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
            [project("p", blocked=[item("aaaa"), item("bbbb", deferred=True,
                                                      defer_until="2026-10-02")])],
        )
        assert "Awaiting a ruling (1)" in out

    def test_include_deferred_flag_folds_them_back_in(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("p", blocked=[item("bbbb", deferred=True, defer_until="2026-10-02")])],
            argv=["--include-deferred"],
        )
        assert "Awaiting a ruling (1)" in out
        assert "## Deferred" not in out

    def test_deferred_without_a_date_is_flagged_not_silently_buried(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("p", blocked=[item("bbbb", deferred=True, defer_until=None)])],
        )
        assert "UNDATED" in out
        assert "nothing will bring this back" in out


class TestLabelSelection:
    def test_only_the_requested_label_is_swept(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("p", blocked=[
                item("dec", labels=["needs-decision"]),
                item("inf", labels=["needsinfo"]),
            ])],
        )
        assert "`dec`" in out
        assert "`inf`" not in out, "needsinfo must not appear in a needs-decision sweep"

    def test_needsinfo_sweep_selects_the_other_half(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("p", blocked=[
                item("dec", labels=["needs-decision"]),
                item("inf", labels=["needsinfo"]),
            ])],
            argv=["--label", "needsinfo"],
        )
        assert "`inf`" in out
        assert "`dec`" not in out


class TestOrdering:
    def test_standing_sorted_oldest_first(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("p", blocked=[
                item("new", age_days=1),
                item("old", age_days=45),
                item("mid", age_days=10),
            ])],
        )
        assert out.index("`old`") < out.index("`mid`") < out.index("`new`")

    def test_age_is_reported_in_days(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("p", blocked=[item("a", age_days=10)])],
            labeled={("p", "needs-decision"): {"a": "2026-08-05T00:00:00Z"}},
        )
        assert "| 10d |" in out


class TestLabelAppliedAge:
    """The feed's age_days counts from filing; waiting starts when the label went on."""

    def test_label_event_overrides_the_feeds_created_based_age(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("fatescroll", blocked=[item("kmgh", age_days=159)])],
            labeled={("fatescroll", "needs-decision"): {"kmgh": "2026-07-31T00:00:00Z"}},
        )
        assert "| 15d |" in out, "must report waiting age, not filing age"
        assert "159" not in out

    def test_missing_label_event_falls_back_and_marks_the_age_uncertain(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, [project("p", blocked=[item("a", age_days=159)])])
        assert "| 159?d |" in out, "a filing-age fallback must not pass as a waiting age"

    def test_reordering_follows_the_corrected_ages(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("p", blocked=[item("stale", age_days=159), item("real", age_days=30)])],
            labeled={("p", "needs-decision"): {"stale": "2026-08-10T00:00:00Z"}},
        )
        assert out.index("`real`") < out.index("`stale`"), (
            "an issue triaged recently must not outrank a genuinely older one"
        )


class TestGapsAreNotZeroes:
    def test_unaskable_project_is_reported_as_a_gap(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("good", blocked=[item("aaaa")]),
             project("broken", tasks_null=True, binding="bound", tasks_unknown=True)],
        )
        assert "Could not query (1)" in out
        assert "broken" in out
        assert "stale .kata.toml" in out
        assert "not a project with nothing in it" in out

    def test_unaskable_project_does_not_inflate_the_standing_count(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("good", blocked=[item("aaaa")]),
             project("broken", tasks_null=True, binding="bound")],
        )
        assert "Awaiting a ruling (1)" in out

    def test_unbound_project_is_not_a_gap(self, monkeypatch, capsys):
        """pi-chudnovsky has no .kata.toml. There was nothing to ask; nothing failed."""
        out = run(
            monkeypatch,
            capsys,
            [project("pi-chudnovsky", tasks_null=True, binding="unbound")],
        )
        assert "Could not query" not in out

    def test_asked_project_holding_nothing_is_not_a_gap(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, [project("quiet", blocked=[])])
        assert "Could not query" not in out
        assert "No standing" in out

    def test_unestablished_binding_is_a_gap_with_its_own_reason(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, [project("p", tasks_null=True, binding="")])
        assert "Could not query (1)" in out
        assert "no kata binding established" in out


class TestEmptyState:
    def test_no_standing_decisions_says_so_explicitly(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, [project("p", blocked=[])])
        assert "No standing" in out


class TestBriefLine:
    """Ruling (Jerry, 2026-08-16): report waiting_on_you with the split, needsinfo excluded."""

    def test_reports_both_labels_with_the_split_visible(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("alexandria", blocked=[item("qxq2", age_days=21)]),
             project("claudes-home", blocked=[
                 item("1zva", labels=["needs-review"], age_days=18)])],
            argv=["--brief"],
        )
        assert out.startswith("DECISIONS waiting_on_you=2 (decision 1, review 1)")
        assert "oldest=21d(alexandria/qxq2)" in out
        assert "projects=2" in out
        assert "\n" in out and out.count("\n") == 1, "brief mode must emit exactly one line"

    def test_needsinfo_is_absent_from_the_startup_line(self, monkeypatch, capsys):
        """A persistent needsinfo count next to Jerry's would read as his own backlog."""
        out = run(
            monkeypatch,
            capsys,
            [project("p", blocked=[item("a")] + [
                item(f"n{n}", labels=["needsinfo"]) for n in range(26)])],
            argv=["--brief"],
        )
        assert "waiting_on_you=1" in out
        assert "=26" not in out, "the needsinfo count must not appear under any field name"
        assert "needsinfo" not in out
        assert "waiting_on_a_loop" not in out

    def test_an_item_carrying_both_labels_counts_once(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("p", blocked=[item("a", labels=["needs-decision", "needs-review"])])],
            argv=["--brief"],
        )
        assert out.startswith("DECISIONS waiting_on_you=1 (decision 1, review 1)")

    def test_deferred_excluded_from_the_brief_count_too(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("p", blocked=[item("a"), item("b", deferred=True,
                                                   defer_until="2026-10-02")])],
            argv=["--brief"],
        )
        assert "waiting_on_you=1" in out

    def test_zero_standing_omits_the_oldest_field(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, [project("p", blocked=[])], argv=["--brief"])
        assert "waiting_on_you=0" in out
        assert "oldest=" not in out

    def test_unqueryable_projects_surface_in_the_brief(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            [project("good", blocked=[item("a")]),
             project("broken", tasks_null=True, binding="bound")],
            argv=["--brief"],
        )
        assert "unqueryable=1" in out

    def test_missing_stamp_reports_never(self, monkeypatch, capsys, tmp_path):
        monkeypatch.setattr(sd, "STAMP", str(tmp_path / "absent"))
        out = run(monkeypatch, capsys, [project("p", blocked=[item("a")])], argv=["--brief"])
        assert "last=never" in out

    def test_stamp_age_reported_in_days(self, monkeypatch, capsys, tmp_path):
        stamp = tmp_path / "last-roundup"
        stamp.write_text("2026-08-05\n")
        monkeypatch.setattr(sd, "STAMP", str(stamp))
        out = run(monkeypatch, capsys, [project("p", blocked=[item("a")])], argv=["--brief"])
        assert "last=2026-08-05 days_ago=10" in out

    def test_unreadable_stamp_does_not_crash_the_startup_check(self, monkeypatch, capsys, tmp_path):
        stamp = tmp_path / "last-roundup"
        stamp.write_text("not-a-date\n")
        monkeypatch.setattr(sd, "STAMP", str(stamp))
        out = run(monkeypatch, capsys, [project("p", blocked=[item("a")])], argv=["--brief"])
        assert "days_ago=?" in out


class TestFeedFailure:
    def test_a_feed_that_cannot_be_read_exits_rather_than_reporting_zero(self, monkeypatch):
        monkeypatch.setattr(sd, "run", lambda cmd: (1, "", "projstat: no such config"))
        try:
            sd.feed()
        except SystemExit as e:
            assert "cannot read projstat feed" in str(e)
        else:
            raise AssertionError("a dead feed must not read as an empty backlog")

    def test_unparseable_feed_exits_too(self, monkeypatch):
        monkeypatch.setattr(sd, "run", lambda cmd: (0, "not json", ""))
        try:
            sd.feed()
        except SystemExit as e:
            assert "not JSON" in str(e)
        else:
            raise AssertionError("a garbled feed must not read as an empty backlog")
