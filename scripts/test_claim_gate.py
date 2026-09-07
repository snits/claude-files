"""Tests for the artifact-falsifiability claim gate (kata claudes-home#z3gp).

No mocks: feed strings to should_gate, and synthetic stdin/stdout to main.
"""
import io
import json

from claim_gate import GATE_TEXT, main, should_gate


def test_git_commit_gates():
    assert should_gate("git commit -s -m x") is True


def test_git_commit_dry_run_does_not_gate():
    assert should_gate("git commit --dry-run -m x") is False


def test_git_log_does_not_gate():
    assert should_gate("git log") is False


def test_kata_close_gates():
    assert should_gate("kata close abc4 --done") is True


def test_kata_close_dry_run_does_not_gate():
    assert should_gate("kata close abc4 --dry-run") is False


def test_kata_comment_with_delivered_gates():
    assert should_gate('kata comment abc4 --body "DELIVERED the fix"') is True


def test_kata_comment_with_verified_gates():
    assert should_gate('kata comment abc4 --body "VERIFIED against test output"') is True


def test_kata_comment_with_correction_gates():
    assert should_gate('kata comment abc4 --body "CORRECTION: it was wrong"') is True


def test_kata_comment_with_ruling_gates():
    assert should_gate('kata comment abc4 --body "RULING (Jerry): do X"') is True


def test_kata_comment_without_prefix_does_not_gate():
    assert should_gate('kata comment abc4 --body "note"') is False


def test_kata_comment_lowercase_prefix_does_not_gate():
    """Prefixes are case-sensitive -- 'delivered' is not 'DELIVERED'."""
    assert should_gate('kata comment abc4 --body "delivered the fix"') is False


def test_echoed_words_inside_a_string_still_gate():
    """Pinned per brief: false positives cost one line, misses cost a false record."""
    assert should_gate("echo git commit") is True


def test_git_dash_c_path_commit_gates():
    assert should_gate("git -C /home/j/x commit -s -m x") is True


def test_git_no_pager_commit_gates():
    assert should_gate("git --no-pager commit -m x") is True


def test_git_commit_tree_does_not_gate():
    assert should_gate("git commit-tree abc") is False


def test_dry_run_in_earlier_segment_does_not_exempt_later_gated_segment():
    assert should_gate("foo --dry-run && git commit -m x") is True


def test_dry_run_in_later_segment_does_not_exempt_earlier_gated_segment():
    assert should_gate("git commit -m x && foo --dry-run") is True


def test_dry_run_in_same_segment_still_exempts():
    assert should_gate("git commit --dry-run -m x") is False


def test_kata_closed_does_not_gate():
    assert should_gate("kata closed abc4") is False


def test_kata_close_after_semicolon_gates():
    assert should_gate("git log --oneline; kata close abc4 --done --commit abc") is True


def test_unbalanced_quote_falls_back_to_split_and_gates_without_raising():
    assert should_gate('echo "git commit') is True


def test_malformed_stdin_not_json_prints_nothing_and_returns_0():
    out = io.StringIO()
    rc = main(stdin=io.StringIO("not json"), stdout=out)
    assert rc == 0
    assert out.getvalue() == ""


def test_malformed_stdin_missing_tool_input_prints_nothing_and_returns_0():
    out = io.StringIO()
    rc = main(stdin=io.StringIO(json.dumps({"tool_name": "Bash"})), stdout=out)
    assert rc == 0
    assert out.getvalue() == ""


def test_malformed_stdin_tool_input_not_a_dict_prints_nothing_and_returns_0():
    out = io.StringIO()
    payload = json.dumps({"tool_name": "Bash", "tool_input": "not a dict"})
    rc = main(stdin=io.StringIO(payload), stdout=out)
    assert rc == 0
    assert out.getvalue() == ""


def test_malformed_stdin_command_missing_prints_nothing_and_returns_0():
    out = io.StringIO()
    payload = json.dumps({"tool_name": "Bash", "tool_input": {}})
    rc = main(stdin=io.StringIO(payload), stdout=out)
    assert rc == 0
    assert out.getvalue() == ""


def test_malformed_stdin_command_not_a_string_prints_nothing_and_returns_0():
    out = io.StringIO()
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": 123}})
    rc = main(stdin=io.StringIO(payload), stdout=out)
    assert rc == 0
    assert out.getvalue() == ""


def test_non_gating_command_prints_nothing_and_returns_0():
    out = io.StringIO()
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git status"}})
    rc = main(stdin=io.StringIO(payload), stdout=out)
    assert rc == 0
    assert out.getvalue() == ""


def test_gated_command_output_parses_with_exact_shape():
    out = io.StringIO()
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit -s -m x"}})
    rc = main(stdin=io.StringIO(payload), stdout=out)
    assert rc == 0
    parsed = json.loads(out.getvalue())
    assert parsed == {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": GATE_TEXT,
        }
    }


# --- quote-aware segmentation (re-review round 2) ---

def test_quoted_separator_between_git_and_commit_still_gates():
    assert should_gate('git -c "alias.co=checkout && push" commit -m x') is True


def test_quoted_separator_in_commit_message_still_gates():
    assert should_gate('git commit -m "a && b; c | d"') is True


def test_quoted_kata_close_inside_plain_comment_body_does_not_gate():
    assert should_gate('kata comment abc4 --body "pre ; kata close"') is False


def test_background_ampersand_separates_segments():
    assert should_gate("sleep 1 & git commit -m x") is True
    assert should_gate("git commit --dry-run -m x & true") is False


def test_newline_separates_segments():
    assert should_gate("foo --dry-run\ngit commit -m x") is True
