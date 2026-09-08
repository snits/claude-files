"""Tests for the artifact-falsifiability claim gate (kata claudes-home#z3gp).

No mocks: feed strings to should_gate, and synthetic stdin/stdout to main.
"""
import io
import json

from claim_gate import GATE_TEXT, _without_heredoc_bodies, main, should_gate


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


# --- heredoc bodies are data, not commands (kata 8n8g) ---

def test_prose_heredoc_naming_the_verbs_does_not_gate():
    """Notes written through a heredoc: an apostrophe in prose is an unbalanced quote."""
    cmd = "cat >> notes.md <<'EOF'\nJerry's ruling: land it with git commit -s\nEOF"
    assert should_gate(cmd) is False


def test_heredoc_with_triple_quotes_in_body_does_not_gate():
    """An odd apostrophe in the body pushes shlex into the unbalanced-quote fallback,
    which strips quotes and frees the verbs as bare tokens."""
    cmd = "python3 - <<'EOF'\nnew = '''an agent's text'''\ns = \"git commit -m x\"\nEOF"
    assert should_gate(cmd) is False


def test_kata_close_inside_heredoc_body_does_not_gate():
    cmd = "cat > notes.md <<EOF\nthen run kata close abc4 --done\nEOF"
    assert should_gate(cmd) is False


def test_commit_message_from_heredoc_still_gates():
    """The command receiving the heredoc is the real commit; only its body is data."""
    cmd = "git commit -s -q -F - <<'EOF'\nscripts: do the thing\n\nbody\nEOF"
    assert should_gate(cmd) is True


def test_command_after_heredoc_terminator_still_gates():
    cmd = "cat > f <<EOF\nnote\nEOF\ngit commit -m y"
    assert should_gate(cmd) is True


def test_dash_heredoc_with_tab_indented_terminator_is_stripped():
    cmd = "cat > f <<-EOF\n\tgit commit -m x\n\tEOF"
    assert should_gate(cmd) is False


def test_unmatched_terminator_keeps_the_lines_and_gates():
    """A terminator that never appears means the << was probably not a heredoc.
    Keeping the lines can only cost a spare reminder; dropping them could hide a
    real commit."""
    assert should_gate("cat > f <<EOF\ngit commit -m x") is True


def test_heredoc_fed_to_a_shell_is_commands_and_gates():
    """A miss costs a false record: bash <<EOF runs its body."""
    assert should_gate("bash <<'EOF'\ngit commit -m x\nEOF") is True
    assert should_gate("ssh host <<EOF\nkata close abc4 --done\nEOF") is True


def test_heredoc_fed_to_a_shell_respects_dry_run_per_body_line():
    cmd = "bash <<'EOF'\ngit commit --dry-run -m x\nEOF"
    assert "git commit --dry-run -m x" in _without_heredoc_bodies(cmd)
    assert should_gate(cmd) is False


def test_heredoc_operator_inside_quotes_is_not_a_heredoc():
    """A quoted << must not swallow the lines that follow it."""
    assert should_gate('echo "see <<EOF in the docs"\ngit commit -m x\nEOF') is True


def test_arithmetic_left_shift_is_not_a_heredoc():
    assert should_gate("echo $((1<<2))\ngit commit -m x\n2") is True
    assert should_gate("x=$((y<<8))\nkata close abc4 --done\n8") is True


def test_heredoc_fed_to_a_shell_by_path_is_commands_and_gates():
    assert should_gate("/bin/bash <<'EOF'\ngit commit -m x\nEOF") is True
    assert should_gate("/usr/bin/env sh <<EOF\nkata close abc4 --done\nEOF") is True


def test_unbalanced_operator_line_strips_nothing():
    """When the operator line's own quotes do not balance, a << may be inside them;
    dropping text on that path would be a miss, so nothing is treated as a body."""
    assert should_gate("echo it's << EOF\ngit commit -m x\nEOF") is True


def test_two_heredocs_on_one_line_both_strip_in_order():
    cmd = "diff <(cat <<A) <(cat <<B)\ngit commit -m x\nA\nkata close abc4 --done\nB"
    assert should_gate(cmd) is False


def test_dash_heredoc_with_quoted_terminator_is_stripped():
    assert should_gate("cat > f <<-'EOF'\n\tgit commit -m x\n\tEOF") is False


def test_terminator_with_trailing_whitespace_does_not_end_the_body():
    """bash requires the terminator alone on its line; 'EOF ' is still body."""
    assert should_gate("cat > f <<EOF\nEOF \ngit commit -m x\nEOF") is False


def test_left_shift_in_square_or_triple_parens_is_not_a_heredoc():
    assert should_gate("x=$[1<<2]\ngit commit -m x\n2") is True
    assert should_gate("echo $(((1<<2)))\ngit commit -m x\n2") is True


def test_let_shift_is_a_heredoc_to_bash_but_keeps_the_commit_line():
    """bash reads `let x=1<<2` as a heredoc wanting `2`; the terminator never comes,
    so the lines stay and the spare reminder is the tolerated cost."""
    assert should_gate("let x=1<<2\ngit commit -m x") is True


def test_heredoc_after_arithmetic_on_the_same_line_is_stripped():
    assert should_gate("echo $((1<<2));cat <<EOF\ngit commit -m x\nEOF") is False


def test_heredoc_fed_to_a_privileged_or_evaluating_shell_gates():
    assert should_gate("sudo -s <<'EOF'\ngit commit -m x\nEOF") is True
    assert should_gate("su - <<'EOF'\ngit commit -m x\nEOF") is True


def test_heredoc_line_inside_an_open_multiline_quote_is_not_an_operator():
    """The << is text inside a quoted argument opened on an earlier line."""
    cmd = "kata comment abc4 --body 'see:\ncat <<EOF\nRULING: use x\nEOF\n'"
    assert should_gate(cmd) is True
    cmd = "echo 'doc:\nusage: cat <<EOF\n' && git commit -am x\nEOF"
    assert should_gate(cmd) is True


def test_runner_after_the_terminator_in_a_continued_pipeline_keeps_the_body():
    assert should_gate("cat <<'EOF' |\ngit commit -m x\nEOF\nbash") is True
    assert should_gate("cat <<'EOF' |\nnote about git commit\nEOF\nwc -l") is False


def test_other_stdin_executing_programs_keep_the_body():
    assert should_gate("fish <<EOF\ngit commit -m x\nEOF") is True
    assert should_gate("parallel <<EOF\ngit commit -m x\nEOF") is True
    assert should_gate("make -f - <<'EOF'\nall:\n\tgit commit -m x\nEOF") is True


# --- kata hs5n: a `#` comment must end at its newline, not swallow what follows ---
#
# Every test below is pinned to a mutation of claim_gate.py it is known to kill; a test
# that no mutation kills asserts nothing. The first cut of these used a newline between
# the `#` and the `git commit` canary, which put the canary outside a comment's blast
# radius and made four of them pass with the code under test deleted. Same-line `&&` is
# what discriminates: keep it.


def test_comment_line_does_not_swallow_following_commit():
    assert should_gate("# commit the fix\ngit commit -m x") is True


def test_comment_line_does_not_swallow_following_kata_close():
    assert should_gate("# wrap up\nkata close ab12 --done") is True


def test_comment_line_does_not_swallow_following_kata_comment():
    assert should_gate("# note\nkata comment ab12 --body 'RULING (Jerry): x'") is True


def test_trailing_comment_does_not_swallow_the_next_line():
    assert should_gate("git status  # look first\ngit commit -m x") is True


def test_comment_inside_a_run_heredoc_body_does_not_swallow_the_body():
    assert should_gate("bash <<EOF\n# note\ngit commit -m x\nEOF") is True


def test_commented_out_commit_still_does_not_gate():
    """A commit genuinely inside a comment is not a claim being made."""
    assert should_gate("git status  # then git commit -m x") is False


def test_hash_inside_a_word_is_not_a_comment():
    assert should_gate("echo a#b && git commit -m x") is True


def test_hash_in_single_quotes_is_not_a_comment():
    assert should_gate("echo 'a # b' && git commit -m x") is True


def test_hash_in_double_quotes_is_not_a_comment():
    assert should_gate('echo "a # b" && git commit -m x') is True


def test_quoted_hash_in_an_argument_does_not_comment_out_what_follows():
    assert should_gate("git tag -m 'v1 #42' && git commit -m x") is True


def test_hash_after_an_escaped_space_is_still_inside_the_word():
    """`x\\ #y` is one word, so the `#` opens nothing."""
    assert should_gate("echo x\\ #y && git commit -m x") is True


def test_backslash_is_literal_inside_single_quotes():
    """`'a\\'` closes at the second quote, so the later `#` is a real comment."""
    assert should_gate("echo 'a\\' x # y && git commit -m z") is False


def test_backslash_escapes_a_quote_inside_double_quotes():
    """A backslash escapes inside `"..."`, so `\\"` does not close the quote.

    The `#` therefore stays inside the argument and opens no comment, leaving the
    `git commit` on the same line to gate. The same-line `&&` is required: a newline
    before the commit would put the canary outside a comment's blast radius, and the
    test would pass either way (see hs5n).
    """
    assert should_gate('echo "a\\" # b" && git commit -m x') is True


def test_comment_after_a_closed_quote_is_a_comment():
    assert should_gate("echo 'a' # c && git commit -m x") is False


def test_heredoc_bodies_are_dropped_before_comments_are_stripped():
    """An unbalanced quote in a dropped body must not desync the comment stripper.

    Stripping comments first would leave this `#` unstripped -- the apostrophe in the
    body opens a quote that never closes -- and the commented-out commit would gate.
    """
    assert should_gate("cat <<EOF\ndon't\nEOF\n# git commit -m x") is False


def test_multiline_quoted_argument_containing_a_hash_line():
    assert should_gate("echo 'a\n# b' && git commit -m x") is True


# --- kata 8vqx: a backslash-newline is a line continuation, not a separator ---
#
# `_segments` rewrites every newline to `;` before tokenizing. A backslash-newline
# must be removed first, the way bash joins the lines, or the rewrite drops a `;`
# between `git` and `commit` and the verb pair is never adjacent in one segment.
# Each canary keeps the verb pair split across the continuation: a wrapped command
# whose verbs are already on one line would gate either way and assert nothing.


def test_continuation_between_the_verb_and_its_subcommand_still_gates():
    assert should_gate("git \\\n  commit -m x") is True


def test_continuation_before_kata_close_still_gates():
    assert should_gate("kata \\\n  close ab12 --done --message y") is True


def test_continuation_inside_a_longer_pipeline_still_gates():
    assert should_gate("cd /tmp && git \\\n  commit -s -m x") is True


def test_a_bare_newline_still_separates_commands():
    """Only a backslash-newline joins; a plain newline must stay a separator."""
    assert should_gate("echo git\ncommit -m x") is False


def test_continuation_joins_the_words_it_touches():
    """bash makes `git\\<newline>commit` the single word `gitcommit`, not a verb pair."""
    assert should_gate("git\\\ncommit -m x") is False


# --- kata gh26: verbs hidden inside a quoted argument ---
#
# shlex keeps a quoted argument whole, which is what makes a separator inside one
# harmless. The cost is that `bash -c 'git commit -m x'` puts the verb pair inside a
# single token where _has_verb_after cannot see it. Each canary below hides the pair
# in the quoted argument only: a command whose verbs also appear unquoted would gate
# either way and assert nothing.


def test_commit_inside_a_shell_dash_c_argument_gates():
    assert should_gate("bash -c 'git commit -m x'") is True


def test_commit_inside_an_eval_argument_gates():
    assert should_gate('eval "git commit -m x"') is True


def test_kata_close_inside_a_quoted_argument_gates():
    assert should_gate("ssh host 'kata close ab12 --done --message y'") is True


def test_dry_run_inside_the_same_quoted_argument_does_not_gate():
    """The scan reads the whole hidden command, so its --dry-run still counts."""
    assert should_gate("bash -c 'git commit --dry-run -m x'") is False


def test_a_quoted_argument_without_a_verb_pair_does_not_gate():
    assert should_gate("echo 'hello world how are you'") is False


def test_a_single_word_quoted_argument_is_unaffected():
    assert should_gate("echo 'commit'") is False
