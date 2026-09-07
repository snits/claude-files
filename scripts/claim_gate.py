#!/usr/bin/env python3
"""PreToolUse hook (matcher Bash): when a command lands a durable claim (a commit, a kata
close, a kata comment carrying one of our comment prefixes), remind the model to name the
falsifiable artifact backing the claim before it runs. Never blocks -- always exits 0.

Reads the hook JSON on stdin; prints one hookSpecificOutput JSON object, or nothing.
"""
import json
import re
import shlex
import sys

COMMENT_PREFIX_RE = re.compile(r"\b(DELIVERED|VERIFIED|CORRECTION|RULING)\b")

GATE_TEXT = (
    'ARTIFACT GATE (kata z3gp): this command lands a claim in a durable record. Before it '
    'runs, name the artifact that backs the claim in its message (a test result line, a diff, '
    'a file, a measured count) and answer in one line: could that artifact look exactly like '
    'this if the claim were false? If yes, the claim does not ship until a different artifact '
    'exists. A pipeline exit code, an agent\'s "success", a green test never seen red, and a '
    'status line summarizing another artifact all fail this question.'
)


SEPARATOR_TOKENS = {"&&", "||", ";", ";;", "|", "&"}


def _segments(command: str) -> list[list[str]]:
    """Quote-aware split into shell segments (lists of tokens).

    shlex in punctuation mode keeps quoted text intact and emits `&&`, `||`, `;`, `|`
    as their own tokens, so a separator inside a quoted argument never splits a command.
    Newlines are treated as `;`. Unbalanced quotes fall back to a whitespace split.
    """
    text = command.replace("\n", " ; ")
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        tokens = [t.strip("\"'") for t in text.split()]
    out: list[list[str]] = []
    seg: list[str] = []
    for tok in tokens:
        if tok in SEPARATOR_TOKENS:
            if seg:
                out.append(seg)
                seg = []
        else:
            seg.append(tok)
    if seg:
        out.append(seg)
    return out


def _has_verb_after(tokens: list[str], first: str, second: str) -> bool:
    """True if `first` appears in tokens with `second` (exact token) at a later index."""
    try:
        idx = tokens.index(first)
    except ValueError:
        return False
    return second in tokens[idx + 1:]


def should_gate(command: str) -> bool:
    for tokens in _segments(command):
        has_dry_run = "--dry-run" in tokens
        if _has_verb_after(tokens, "git", "commit") and not has_dry_run:
            return True
        if _has_verb_after(tokens, "kata", "close") and not has_dry_run:
            return True
        if _has_verb_after(tokens, "kata", "comment") and COMMENT_PREFIX_RE.search(" ".join(tokens)):
            return True
    return False


def main(stdin=sys.stdin, stdout=sys.stdout) -> int:
    try:
        data = json.load(stdin)
    except Exception:
        return 0
    if not isinstance(data, dict):
        return 0
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0
    command = tool_input.get("command")
    if not isinstance(command, str):
        return 0
    if not should_gate(command):
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "additionalContext": GATE_TEXT}}), file=stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
