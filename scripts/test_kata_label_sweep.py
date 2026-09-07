"""Tests for the closed-issue label sweep.

Exercised against issue dicts shaped like `kata list --json` output — no mocks
for find_stale/render; the strip path is exercised through an injectable run
seam that records argv, in the same style as test_kata_defer.py.
"""
import pytest

from kata_label_sweep import (
    OPEN_WORK_LABELS,
    Stale,
    find_stale,
    main,
    render,
    strip_stale,
)


def issue(qualified_id, title="t", closed_at="2026-09-01T00:00:00Z"):
    d = {"qualified_id": qualified_id, "title": title}
    if closed_at is not None:
        d["closed_at"] = closed_at
    return d


def fake_list_fn(rows_by_label):
    def list_fn(label):
        return rows_by_label.get(label, [])

    return list_fn


def test_find_stale_empty():
    assert find_stale(fake_list_fn({})) == []


def test_one_issue_under_two_labels_yields_two_rows():
    rows = {
        "needs-review": [issue("proj#aaaa", title="x")],
        "needs-decision": [issue("proj#aaaa", title="x")],
    }
    stales = find_stale(fake_list_fn(rows), labels=("needs-review", "needs-decision"))
    assert len(stales) == 2
    assert {s.label for s in stales} == {"needs-review", "needs-decision"}
    assert all(s.qualified_id == "proj#aaaa" for s in stales)


def test_row_missing_closed_at_still_renders():
    rows = {"needsinfo": [issue("proj#bbbb", closed_at=None)]}
    stales = find_stale(fake_list_fn(rows), labels=("needsinfo",))
    assert len(stales) == 1
    assert stales[0].closed_at is None
    out = render(stales)
    assert "proj#bbbb" in out


def test_render_zero():
    assert render([]) == "LABEL SWEEP 0 closed issues labelled"


def test_render_two_rows_sorted_by_qualified_id_then_label():
    stales = [
        Stale(qualified_id="proj#bbbb", label="needs-review", title="second", closed_at="x"),
        Stale(qualified_id="proj#aaaa", label="needs-decision", title="first-b", closed_at="x"),
        Stale(qualified_id="proj#aaaa", label="needs-review", title="first-a", closed_at="x"),
    ]
    out = render(stales)
    assert out == (
        "LABEL SWEEP 3 closed issue(s) still labelled\n"
        "  proj#aaaa  needs-decision  first-b\n"
        "  proj#aaaa  needs-review  first-a\n"
        "  proj#bbbb  needs-review  second"
    )


class FakeProc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_strip_stale_calls_comment_before_label_rm_with_actor():
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return FakeProc(returncode=0, stdout="")

    stale = Stale(qualified_id="proj#aaaa", label="needs-review", title="t", closed_at="x")
    strip_stale(stale, workspace="~/claudes-home", run=fake_run)

    assert len(calls) == 2
    comment_call, label_call = calls
    assert comment_call[0:2] == ["kata", "comment"]
    assert comment_call[2] == "proj#aaaa"
    assert "--as" in comment_call and "claude-label-sweep" in comment_call
    assert label_call[0:3] == ["kata", "label", "rm"]
    assert label_call[3] == "proj#aaaa"
    assert label_call[4] == "needs-review"
    assert "--as" in label_call and "claude-label-sweep" in label_call


def test_label_bogus_exits_2():
    with pytest.raises(SystemExit) as exc:
        main(["--label", "bogus"])
    assert exc.value.code == 2
