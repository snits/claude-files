"""Tests for the kata defer convention.

Exercised against issue dicts shaped like `kata list --json` output — no mocks,
in the same style as the vault's test_vitals.py.
"""
from datetime import date

import pytest

from kata_defer import DEFER_KEY, DEFER_LABEL, report

TODAY = date(2026, 7, 23)


def issue(short_id, *, labels=None, defer_until=None, priority=3, title="t"):
    d = {
        "short_id": short_id,
        "title": title,
        "priority": priority,
        "status": "open",
        "metadata": {},
    }
    if labels is not None:
        d["labels"] = labels
    if defer_until is not None:
        d["metadata"][DEFER_KEY] = defer_until
    return d


def test_defer_date_in_the_past_is_due():
    r = report([issue("aaaa", labels=[DEFER_LABEL], defer_until="2026-07-22")], TODAY)
    assert [i["short_id"] for i in r.due] == ["aaaa"]
    assert r.pending == [] and r.undated == []


def test_defer_date_of_today_is_due():
    r = report([issue("bbbb", labels=[DEFER_LABEL], defer_until="2026-07-23")], TODAY)
    assert [i["short_id"] for i in r.due] == ["bbbb"]


def test_defer_date_in_the_future_is_pending():
    r = report([issue("cccc", labels=[DEFER_LABEL], defer_until="2026-09-21")], TODAY)
    assert [i["short_id"] for i in r.pending] == ["cccc"]
    assert r.due == []


def test_deferred_label_without_a_date_is_reported_as_undated():
    """A label with no date would otherwise hide the issue forever."""
    r = report([issue("dddd", labels=[DEFER_LABEL])], TODAY)
    assert [i["short_id"] for i in r.undated] == ["dddd"]
    assert r.due == [] and r.pending == []


def test_unparseable_defer_date_is_reported_as_undated():
    r = report([issue("eeee", labels=[DEFER_LABEL], defer_until="soon")], TODAY)
    assert [i["short_id"] for i in r.undated] == ["eeee"]


def test_issue_without_the_defer_label_is_ignored_even_if_dated():
    r = report([issue("ffff", labels=["other"], defer_until="2026-01-01")], TODAY)
    assert r.due == [] and r.pending == [] and r.undated == []


def test_issue_with_no_labels_at_all_is_ignored():
    r = report([issue("gggg")], TODAY)
    assert r.due == [] and r.pending == [] and r.undated == []


def test_closed_issues_are_ignored():
    i = issue("hhhh", labels=[DEFER_LABEL], defer_until="2026-01-01")
    i["status"] = "closed"
    r = report([i], TODAY)
    assert r.due == []


def test_due_issues_are_ordered_by_priority_then_date():
    issues = [
        issue("low", labels=[DEFER_LABEL], defer_until="2026-01-01", priority=4),
        issue("high", labels=[DEFER_LABEL], defer_until="2026-07-01", priority=1),
        issue("mid", labels=[DEFER_LABEL], defer_until="2026-02-01", priority=1),
    ]
    r = report(issues, TODAY)
    assert [i["short_id"] for i in r.due] == ["mid", "high", "low"]


@pytest.mark.parametrize("days,expected", [(0, "2026-07-23"), (60, "2026-09-21")])
def test_defer_date_is_days_from_today(days, expected):
    from kata_defer import defer_date

    assert defer_date(TODAY, days) == expected
