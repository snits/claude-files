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

# Commands that run their heredoc body as shell: the body stays in as command lines.
BODY_RUNNERS = {"bash", "sh", "zsh", "dash", "ksh", "mksh", "ash", "fish", "csh", "tcsh", "ssh",
                "sudo", "su", "eval", "at", "batch", "parallel", "make"}


def _line_tokens(line: str) -> list[str] | None:
    """shlex tokens for one line, or None when its quotes are unbalanced."""
    try:
        lex = shlex.shlex(line, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        return list(lex)
    except ValueError:
        return None


def _heredoc_terminators(tokens: list[str]) -> list[tuple[str, bool]]:
    """(terminator, strips_leading_tabs) for each heredoc operator in a line's tokens.

    A `<<` inside `(( ))` arithmetic is a shift, not an operator. Punctuation runs such
    as `(((` or `));` arrive as one token, so depth is tracked by paren pairs inside it.
    """
    found: list[tuple[str, bool]] = []
    arithmetic_depth = 0
    for i, tok in enumerate(tokens):
        arithmetic_depth += tok.count("((")
        arithmetic_depth = max(0, arithmetic_depth - tok.count("))"))
        if tok != "<<" or arithmetic_depth or i + 1 >= len(tokens):
            continue
        word, dash = tokens[i + 1], False
        if word.startswith("-"):
            dash = True
            word = word[1:] or (tokens[i + 2] if i + 2 < len(tokens) else "")
        if word:
            found.append((word, dash))
    return found


def _body_end(lines: list[str], start: int, word: str, dash: bool) -> int | None:
    """Index of the line terminating a heredoc body that starts at `start`, or None."""
    for j in range(start, len(lines)):
        candidate = lines[j].lstrip("\t") if dash else lines[j]
        if candidate == word:
            return j
    return None


def _runs_body(tokens: list[str]) -> bool:
    return any(tok.rsplit("/", 1)[-1] in BODY_RUNNERS for tok in tokens)


def _without_heredoc_bodies(command: str) -> str:
    """Drop heredoc bodies: they are data handed to a program, not commands.

    Only a body whose terminator line exists is dropped; a `<<` with no matching
    terminator was probably not a heredoc, and keeping its lines costs at most a spare
    reminder where dropping them could hide a real commit. The body of a heredoc fed to
    a shell (`bash <<EOF`, `sudo -s <<EOF`, `cat <<EOF | bash`) is commands, so it is
    kept as ordinary lines. A line is an operator line only if the shell text kept so
    far, through that line, has balanced quotes: an unbalanced line, or one inside a
    quote opened earlier, may hold a quoted `<<`, and strips nothing.
    """
    lines = command.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        tokens = _line_tokens(line)
        if tokens is None or _line_tokens("\n".join(out)) is None:
            continue
        for word, dash in _heredoc_terminators(tokens):
            end = _body_end(lines, i, word, dash)
            if end is None:
                break
            runs_body = _runs_body(tokens)
            if not runs_body and tokens[-1] in ("|", "|&") and end + 1 < len(lines):
                runs_body = _runs_body(_line_tokens(lines[end + 1]) or [])
            if runs_body:
                out.extend(lines[i:end])
            i = end + 1
    return "\n".join(out)


def _without_comments(text: str) -> str:
    """Drop shell comments, so a `#` ends at its newline instead of at end of input.

    shlex applies its comment character to the whole string and `_segments` joins lines
    before tokenizing, so one comment line would otherwise swallow every command after
    it -- a miss, and a miss costs more than a spare reminder. A `#` opens a comment only
    outside quotes and after whitespace or at the start, so `a#b` stays one word. Real
    bash also opens one after a metacharacter (`true;#c`), which this does not; that and
    an unterminated quote both leave text in place, and leftover text can only cost a
    spare reminder, because `_segments` clears shlex's own commenters so nothing a strip
    misses can swallow what follows. Runs after heredoc bodies are removed: a dropped
    body may hold unbalanced quotes that would confuse the quote tracking here.
    """
    out: list[str] = []
    quote: str | None = None
    prev_is_space = True
    i = 0
    while i < len(text):
        ch = text[i]
        if quote != "'" and ch == "\\" and i + 1 < len(text):
            out.append(ch)
            out.append(text[i + 1])
            prev_is_space = False
            i += 2
            continue
        if quote is None and ch == "#" and prev_is_space:
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        if quote is None and ch in "'\"":
            quote = ch
        elif quote == ch:
            quote = None
        out.append(ch)
        prev_is_space = ch.isspace()
        i += 1
    return "".join(out)


def _segments(command: str) -> list[list[str]]:
    """Quote-aware split into shell segments (lists of tokens).

    shlex in punctuation mode keeps quoted text intact and emits `&&`, `||`, `;`, `|`
    as their own tokens, so a separator inside a quoted argument never splits a command.
    Heredoc bodies are removed first (see _without_heredoc_bodies), then comments (see
    _without_comments); shlex's own comment handling is switched off, so any `#` that
    survives is quoted or mid-word and becomes an ordinary token. Newlines are treated
    as `;`, but a backslash-newline is removed first: bash joins those lines, so rewriting
    it to `;` would split a verb from its subcommand -- a miss. Joining can only make
    verbs adjacent, never separate them, so the strip errs toward a spare reminder.
    Unbalanced quotes fall back to a whitespace split.
    """
    text = _without_comments(_without_heredoc_bodies(command))
    text = text.replace("\\\n", "").replace("\n", " ; ")
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        lex.commenters = ""
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
