"""Tests for the kata defer convention.

report() is exercised against issue dicts shaped like `kata list --json` output,
in the same style as the vault's test_vitals.py. The `--due` command-path tests
replace the `kata` subprocess seam with canned listings (FakeKata).
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


# --- `--due` through the command path, with the kata boundary faked ---------
#
# `kata_defer._kata` is the single subprocess seam. FakeKata replaces it with
# canned `kata list` envelopes and records every argv, so a test can tell
# `--all` loading apart from cwd-project loading.

import json

import kata_defer

CMD_TODAY = date(2026, 11, 1)
CWD_PROJECT = "claudes-home"
INCOMPLETE_MARKERS = ("incomplete", "truncated", "partial")


class FakeDate(date):
    @classmethod
    def today(cls):
        return CMD_TODAY


def kissue(project, short_id, *, defer_until=None, priority=3, title="t", labels=(DEFER_LABEL,)):
    d = {
        "short_id": short_id,
        "title": title,
        "priority": priority,
        "status": "open",
        "labels": list(labels),
        "metadata": {},
        "project_name": project,
        "qualified_id": f"{project}#{short_id}",
    }
    if defer_until is not None:
        d["metadata"][DEFER_KEY] = defer_until
    return d


# Project names, short_ids and titles are chosen so that none is a substring of
# another, of a header word, or of an incompleteness marker.
CWD_DUE = kissue(CWD_PROJECT, "m5nd", defer_until="2026-10-01", priority=2, title="refresh cache")
CWD_PENDING = kissue(CWD_PROJECT, "q8ve", defer_until="2027-01-01", priority=2, title="later work")
CWD_UNDATED = kissue(CWD_PROJECT, "r2ux", title="lost date")
HEX_DUE_HI = kissue("hexwalker", "j23m", defer_until="2026-10-09", priority=1, title="hex route")
ORB_DUE = kissue("orbweaver", "k7qp", defer_until="2026-10-05", priority=2, title="orb mesh")
HEX_DUE_LO = kissue("hexwalker", "x4ra", defer_until="2026-09-01", priority=3, title="hex biome")
ORB_UNDATED = kissue("orbweaver", "w9tb", title="orb shader")
ORB_PENDING = kissue("orbweaver", "z6yc", defer_until="2027-03-01", priority=1, title="orb later")

CWD_ISSUES = [CWD_DUE, CWD_PENDING, CWD_UNDATED]
# Interleaved by project. report() sorts due issues by priority then date, giving
# hexwalker, claudes-home, orbweaver, hexwalker, so neither the return order nor
# the sorted order is already grouped.
ALL_ISSUES = [HEX_DUE_HI, ORB_DUE, CWD_DUE, HEX_DUE_LO, ORB_UNDATED, CWD_PENDING, ORB_PENDING, CWD_UNDATED]
FOREIGN_PROJECTS = ("hexwalker", "orbweaver")
ALL_PROJECTS = (CWD_PROJECT,) + FOREIGN_PROJECTS


def envelope(issues, *, complete=True, truncated=False):
    return {"kata_api_version": 1, "complete": complete, "truncated": truncated, "issues": issues}


class FakeKata:
    """Stands in for kata_defer._kata. Dispatches on `--all`; ignores `--label`."""

    def __init__(self, cwd_listing=None, all_listing=None):
        self.calls = []
        self.cwd_listing = cwd_listing or envelope(CWD_ISSUES)
        self.all_listing = all_listing or envelope(ALL_ISSUES)

    def __call__(self, *args):
        self.calls.append(list(args))
        if not args or args[0] != "list":
            raise AssertionError(f"unexpected kata call: {args}")
        return json.dumps(self.all_listing if "--all" in args else self.cwd_listing)


@pytest.fixture
def fake_kata(monkeypatch):
    fake = FakeKata()
    monkeypatch.setattr(kata_defer, "_kata", fake)
    monkeypatch.setattr(kata_defer, "date", FakeDate)
    return fake


def run_main(argv, capsys):
    """Run main(); an argparse rejection becomes an explicit test failure."""
    try:
        rc = kata_defer.main(argv)
    except SystemExit as e:
        err = capsys.readouterr().err
        pytest.fail(f"main({argv}) exited {e.code}: {err.strip()}")
    assert rc == 0
    return capsys.readouterr().out


def owning_project(lines, index):
    """The project named on this line, else on the nearest line above that names one."""
    for line in reversed(lines[: index + 1]):
        named = [p for p in ALL_PROJECTS if p in line]
        if named:
            assert len(named) == 1, f"line names several projects: {line!r}"
            return named[0]
    return None


def line_index(lines, short_id):
    hits = [i for i, line in enumerate(lines) if short_id in line]
    assert len(hits) == 1, f"{short_id} should be listed exactly once, found on lines {hits}"
    return hits[0]


# Criterion 2: without --all, output is exactly what 76233fd76375 printed.

PINNED_CWD_OUTPUT = (
    "DEFERRED DUE 1 (as of 2026-11-01)\n"
    "  m5nd p2 refresh cache — due 2026-10-01\n"
    "DEFERRED UNDATED 1 — labelled but no defer_until, will never resurface\n"
    "  r2ux p3 lost date\n"
)


def test_due_without_all_output_is_unchanged(fake_kata, capsys):
    out = run_main(["--due"], capsys)
    assert out == PINNED_CWD_OUTPUT
    assert all("--all" not in call for call in fake_kata.calls)


def test_due_with_project_output_is_unchanged(fake_kata, capsys):
    out = run_main(["--due", "--project", "orbweaver"], capsys)
    assert out == PINNED_CWD_OUTPUT
    assert fake_kata.calls, "no kata listing was loaded"
    for call in fake_kata.calls:
        assert "--all" not in call
        assert call[call.index("--project") + 1] == "orbweaver"


# Criterion 5: the foreign due issue appears with --all and not without it.

def test_foreign_due_issue_appears_only_with_all(fake_kata, capsys):
    without = run_main(["--due"], capsys)
    assert HEX_DUE_HI["short_id"] not in without
    assert "hexwalker" not in without

    fake_kata.calls.clear()
    with_all = run_main(["--due", "--all"], capsys)
    assert any("--all" in call for call in fake_kata.calls), "--all did not load the --all listing"
    assert HEX_DUE_HI["short_id"] in with_all
    assert "hexwalker" in with_all


# Criterion 1: due and undated issues from every project, grouped and identified.

def test_due_all_lists_due_issues_from_every_project_with_their_project(fake_kata, capsys):
    out = run_main(["--due", "--all"], capsys)
    lines = out.splitlines()
    for i in (HEX_DUE_HI, ORB_DUE, HEX_DUE_LO, CWD_DUE):
        idx = line_index(lines, i["short_id"])
        assert owning_project(lines, idx) == i["project_name"], (i["short_id"], out)


def test_due_all_lists_undated_issues_from_every_project_with_their_project(fake_kata, capsys):
    out = run_main(["--due", "--all"], capsys)
    lines = out.splitlines()
    for i in (ORB_UNDATED, CWD_UNDATED):
        idx = line_index(lines, i["short_id"])
        assert owning_project(lines, idx) == i["project_name"], (i["short_id"], out)


def test_due_all_groups_due_issues_by_project(fake_kata, capsys):
    out = run_main(["--due", "--all"], capsys)
    lines = out.splitlines()
    due = (HEX_DUE_HI, ORB_DUE, HEX_DUE_LO, CWD_DUE)
    order = sorted((line_index(lines, i["short_id"]), i["project_name"]) for i in due)
    sequence = [project for _, project in order]
    runs = [p for k, p in enumerate(sequence) if k == 0 or sequence[k - 1] != p]
    assert len(runs) == len(set(runs)), f"due issues interleave projects {sequence}:\n{out}"


def test_due_all_omits_pending_issues(fake_kata, capsys):
    out = run_main(["--due", "--all"], capsys)
    assert ORB_PENDING["short_id"] not in out
    assert CWD_PENDING["short_id"] not in out


# Criterion 3: --all with --project is a usage error.

def test_all_with_project_is_a_usage_error(fake_kata, capsys):
    run_main(["--due", "--all"], capsys)  # --all on its own must be accepted
    fake_kata.calls.clear()
    with pytest.raises(SystemExit) as exc:
        kata_defer.main(["--due", "--all", "--project", "orbweaver"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "unrecognized arguments" not in err
    assert fake_kata.calls == [], "nothing should be loaded for a rejected command line"


# Criterion 4: an incomplete or truncated --all listing is reported, not hidden.

def has_incomplete_marker(out):
    return any(m in out.lower() for m in INCOMPLETE_MARKERS)


@pytest.mark.parametrize(
    "flags",
    [{"complete": False, "truncated": False}, {"complete": True, "truncated": True}],
    ids=["complete-false", "truncated-true"],
)
def test_due_all_reports_an_incomplete_listing(fake_kata, capsys, flags):
    fake_kata.all_listing = envelope(ALL_ISSUES, **flags)
    out = run_main(["--due", "--all"], capsys)
    assert has_incomplete_marker(out), out


def test_due_all_on_a_clean_listing_has_no_incomplete_marker(fake_kata, capsys):
    out = run_main(["--due", "--all"], capsys)
    assert HEX_DUE_HI["short_id"] in out
    assert not has_incomplete_marker(out), out
