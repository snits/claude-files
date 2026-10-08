"""gate.run_gate: Brief-token check against the session's vb-common file(s), and the verdict
read from each artifact's literal last line (kata claudes-home#m83h).

All tests drive the real subprocess path through the fake `claude` in
test_kata_dispatch_fakes.FAKE_CLAUDE_GATE_PASS; its FAKE_GATE_* knobs shape the failure.
"""
import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from test_kata_dispatch_fakes import (FAKE_CLAUDE_GATE_PASS, FAKE_GATE_TOKEN,  # noqa: E402
                                      install_fake_claude, make_repo)

from kata_dispatch import gate  # noqa: E402

BRANCH = "dispatch/ab12"
BRANCH_KEY = "dispatch-ab12"


def _gate(tmp_path, monkeypatch, **env):
    repo = make_repo(tmp_path)
    install_fake_claude(tmp_path, monkeypatch, FAKE_CLAUDE_GATE_PASS)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    return repo, gate.run_gate(repo, "ab12", BRANCH, "integration", "sonnet", tmp_path / "gate.jsonl")


def test_matching_token_and_final_verdict_passes(tmp_path, monkeypatch):
    """(a) Baseline: one common file written in the session, every artifact's line 2 equals its
    line 1, every artifact's last line is VERDICT: PASS -> PASS with three artifacts. Catches an
    implementation that rejects the well-formed case (e.g. compares line 1 of the artifact, or
    counts the vb-common file as a fourth artifact)."""
    _, v = _gate(tmp_path, monkeypatch)
    assert v.passed is True, v.detail
    assert len(v.artifacts) == 3
    assert not any("vb-common" in a for a in v.artifacts)


@pytest.mark.parametrize("bad_token", [
    "0123456789ABCDEF",        # uppercase hex
    "0123456789abcdefjunk",    # junk suffix after 16 hex (regex without its closing anchor)
    "0123456789abcdef ",       # trailing space (stripping line 1 before matching)
])
def test_common_file_line1_must_be_exact_token_format(tmp_path, monkeypatch, bad_token):
    """(a) A token line is exactly `Brief-token: <16 lowercase hex>`, byte for byte. Here the
    common file's line 1 is a malformed token line and every artifact echoes it byte-for-byte, so
    a plain line-2 == line-1 comparison would pass. A malformed line 1 contributes no token, so
    the session has no usable common file -> BLOCK naming the common file. Catches accepting any
    common-file line 1 without validating the format, a TOKEN_RE missing its `$`, and stripping
    line 1 before matching (which would surface as a token mismatch instead)."""
    _, v = _gate(tmp_path, monkeypatch, FAKE_GATE_TOKEN=bad_token)
    assert v.passed is False
    assert "common file" in v.detail.lower(), v.detail


@pytest.mark.parametrize("suffix", [" ", "\t"], ids=["space", "tab"])
def test_line2_with_trailing_whitespace_is_token_mismatch(tmp_path, monkeypatch, suffix):
    """(b) The tests artifact's line 2 is the right token line plus a trailing space or tab. Line 2
    must be byte-equal to a token line, so that artifact is scored as no verdict -> BLOCK naming a
    token mismatch. Catches stripping line 2 before the comparison. (A CR is not a usable probe:
    the artifact is read with universal newlines, so a CR before the newline never reaches the
    comparison.)"""
    _, v = _gate(tmp_path, monkeypatch, FAKE_GATE_LINE2_SUFFIX="tests",
                 FAKE_GATE_LINE2_SUFFIX_TEXT=suffix)
    assert v.passed is False
    assert "token" in v.detail.lower(), v.detail


def test_single_line_artifact_fails_closed_without_raising(tmp_path, monkeypatch):
    """(b) The scope artifact is the single line `VERDICT: PASS` with no newline: it has no line 2,
    so it is a token mismatch -> run_gate returns a BLOCK rather than raising. Catches a length
    guard that cannot fire (IndexError on lines[1] escaping run_gate)."""
    _, v = _gate(tmp_path, monkeypatch, FAKE_GATE_ONE_LINE="scope")
    assert v.passed is False
    assert "token" in v.detail.lower(), v.detail


def test_wrong_token_on_one_artifact_blocks_with_token_mismatch(tmp_path, monkeypatch):
    """(b) The tests artifact's line 2 carries a different, well-formed token. That artifact is
    scored as no verdict, so the gate BLOCKs and detail names a token mismatch. Catches never
    checking line 2, and accepting any well-formed token rather than one from the common file."""
    _, v = _gate(tmp_path, monkeypatch, FAKE_GATE_WRONG_TOKEN="tests")
    assert v.passed is False
    assert "token" in v.detail.lower(), v.detail


def test_no_common_file_blocks_naming_the_common_file(tmp_path, monkeypatch):
    """(c) The session writes no vb-common file; artifacts still carry a well-formed token on
    line 2. Nothing to compare against -> BLOCK, and detail names the missing common file.
    Catches skipping the token check when there is no common file (fail-open)."""
    _, v = _gate(tmp_path, monkeypatch, FAKE_GATE_NO_COMMON="1")
    assert v.passed is False
    assert "common file" in v.detail.lower(), v.detail


def test_common_file_for_another_branch_is_not_accepted(tmp_path, monkeypatch):
    """(a)/(c) Branch-key rule: the only common file in the window names a different branch.
    It must not supply this branch's token -> BLOCK naming the missing common file. Catches
    globbing `*vb-common*` without the branch key."""
    _, v = _gate(tmp_path, monkeypatch, FAKE_GATE_COMMON_BRANCH="dispatch/zz99")
    assert v.passed is False
    assert "common file" in v.detail.lower(), v.detail


def test_common_file_older_than_session_start_is_not_accepted(tmp_path, monkeypatch):
    """(a)/(c) Window rule: a common file for this branch carrying the very token the artifacts
    echo, but with mtime an hour before the gate session started, and the session writes no new
    one. A prior run's common file must not vouch for this run's artifacts -> BLOCK naming the
    missing common file. Catches ignoring the mtime window on the common file."""
    repo = make_repo(tmp_path)
    d = repo / ".scratchpad"
    d.mkdir()
    old = d / (time.strftime("%Y%m%d") + "-vb-common-" + BRANCH_KEY + ".md")
    old.write_text("Brief-token: " + FAKE_GATE_TOKEN + "\n# stale common context\n")
    past = time.time() - 3600
    os.utime(old, (past, past))
    install_fake_claude(tmp_path, monkeypatch, FAKE_CLAUDE_GATE_PASS)
    monkeypatch.setenv("FAKE_GATE_NO_COMMON", "1")
    v = gate.run_gate(repo, "ab12", BRANCH, "integration", "sonnet", tmp_path / "gate.jsonl")
    assert v.passed is False
    assert "common file" in v.detail.lower(), v.detail


def test_blank_line_after_verdict_is_no_verdict(tmp_path, monkeypatch):
    """(d) The scope artifact ends `VERDICT: PASS\\n\\n`: tail -1 is the empty line, so that
    artifact has no verdict -> BLOCK, detail says no verdict. Catches a grep-anywhere / findall
    read, and stripping all trailing whitespace instead of exactly one trailing newline."""
    _, v = _gate(tmp_path, monkeypatch, FAKE_GATE_TRAILING="scope")
    assert v.passed is False
    assert "no verdict" in v.detail, v.detail


def test_text_line_after_verdict_is_no_verdict(tmp_path, monkeypatch):
    """(d) The claims artifact has `VERDICT: PASS` followed by one more prose line, as a
    truncated-then-appended or chatty write would. The last line is not a verdict -> BLOCK.
    Catches a grep-anywhere / findall read that finds the earlier VERDICT line."""
    _, v = _gate(tmp_path, monkeypatch, FAKE_GATE_TRAILING="claims",
                 FAKE_GATE_TRAILING_TEXT="Done; see table above.")
    assert v.passed is False
    assert "no verdict" in v.detail, v.detail


def test_quoted_block_in_body_then_final_pass_is_pass(tmp_path, monkeypatch):
    """(d) Every artifact quotes `VERDICT: BLOCK` as evidence in its body, then ends with
    `VERDICT: PASS`. Only the last line counts -> PASS. Regression guard (green before and after):
    catches taking the first VERDICT match, or blocking on any BLOCK anywhere in the file."""
    _, v = _gate(tmp_path, monkeypatch, FAKE_GATE_QUOTED_BLOCK="1")
    assert v.passed is True, v.detail
    assert len(v.artifacts) == 3


def test_rerun_common_file_tokens_are_both_accepted(tmp_path, monkeypatch):
    """(e) A re-gate leaves `...-vb-common-<branch>.md` and `...-vb-common-<branch>-rerun.md` in
    the window with different tokens; the claims artifact echoes the first, tests and scope echo
    the rerun one. Both are accepted -> PASS. Regression guard: catches reading only the first
    (or only the last) common file found."""
    _, v = _gate(tmp_path, monkeypatch, FAKE_GATE_RERUN="1")
    assert v.passed is True, v.detail
    assert len(v.artifacts) == 3
