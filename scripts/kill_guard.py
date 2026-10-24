#!/usr/bin/env python3
"""PreToolUse hook (matcher Bash): block commands that kill processes by name.

On 2026-10-10 an agent debugging a stalled command ran a name-based kill loop and killed
the user's kata daemon, six terminal TUI sessions and two MCP servers; the terminals did
not come back. Another time `pkill -f <pattern>` matched the agent's own shell. The rule
"never act outside your sandbox" already existed in standing text and did not hold under
debugging pressure, so this hook intercepts the command instead.

Blocked, when the word is in command position (so `echo pkill` and `grep pkill f` pass):
  1. pkill ...
  2. killall ...
  3. kill with a $(pgrep ...) / `pgrep ...` / $(pidof ...) argument
  4. a pipeline where pgrep/pidof feeds a later `xargs kill`
Each also when hidden in `bash -c '...'`. Safe practice: trace the PID from your own
task's process tree (`ps -o pid,ppid,cmd`), then `kill <literal-pid>`.

This is a workstation guard, not a security boundary: when unsure it lets the command
through, because a false block costs a real command and a miss costs only what the hook
would have caught.

Reuses claim_gate's shell segmentation (heredocs, quoting, `;`/`&&` chains, `bash -c`).
Rule 4 needs to know which segments were piped; _segments discards the `|`, so it runs
its own pass over the same sanitised text.

Exit 2 blocks the call and shows stderr to the model. Any internal error exits 0.
"""
import json
import os
import re
import shlex
import sys

from claim_gate import (
    SEPARATOR_TOKENS,
    _hidden_commands,
    _runs_body,
    _segments,
    _without_comments,
    _without_heredoc_bodies,
)

PREFIXES = {"sudo", "command", "env", "nohup", "time", "nice", "doas",
            "do", "then", "else", "!", "(", "{", "$"}
NAME_KILLERS = {"pkill", "killall"}
PID_LOOKUPS = {"pgrep", "pidof"}
LOOKUP_SUBSTITUTION = re.compile(r"(?:\$\s*\(|`)\s*(?:\S*/)?(?:pgrep|pidof)\b")
XARGS_FLAGS_WITH_VALUE = {"-n", "-I", "-L", "-P", "-d", "-E", "-s", "-a", "-l", "-i"}
MAX_DEPTH = 3


def _command_index(tokens: list[str]) -> int | None:
    """Index of the command being run, skipping `VAR=val` and wrapper words."""
    for i, tok in enumerate(tokens):
        if "=" in tok and not tok.startswith("-") and tok.split("=", 1)[0].isidentifier():
            continue
        if tok in PREFIXES or tok.rsplit("/", 1)[-1] in PREFIXES or tok.startswith("-"):
            continue
        return i
    return None


def _command_name(tokens: list[str]) -> str | None:
    idx = _command_index(tokens)
    return None if idx is None else tokens[idx].rsplit("/", 1)[-1]


def _kills_by_name(tokens: list[str]) -> bool:
    """Rules 1-3 for one segment's tokens."""
    name = _command_name(tokens)
    if name in NAME_KILLERS:
        return True
    if name == "kill":
        return bool(LOOKUP_SUBSTITUTION.search(" ".join(tokens[_command_index(tokens) + 1:])))
    return False


def _xargs_runs_kill(tokens: list[str]) -> bool:
    idx = _command_index(tokens)
    if idx is None or tokens[idx].rsplit("/", 1)[-1] != "xargs":
        return False
    i = idx + 1
    while i < len(tokens) and tokens[i].startswith("-"):
        i += 2 if tokens[i] in XARGS_FLAGS_WITH_VALUE else 1
    return i < len(tokens) and tokens[i].rsplit("/", 1)[-1] == "kill"


def _pipelines(command: str) -> list[list[list[str]]]:
    """Each pipeline as a list of stages (token lists), `|` kept as the stage boundary."""
    text = _without_comments(_without_heredoc_bodies(command))
    text = text.replace("\\\n", "").replace("\n", " ; ")
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        lex.commenters = ""
        tokens = list(lex)
    except ValueError:
        return []
    out: list[list[list[str]]] = []
    pipeline: list[list[str]] = [[]]
    for tok in tokens:
        if tok == "|":
            pipeline.append([])
        elif tok in SEPARATOR_TOKENS:
            out.append(pipeline)
            pipeline = [[]]
        else:
            pipeline[-1].append(tok)
    out.append(pipeline)
    return out


def _piped_lookup_to_kill(command: str, depth: int = 0) -> bool:
    """Rule 4: pgrep/pidof in one stage, `xargs kill` in a later stage of the same pipeline."""
    if depth > MAX_DEPTH:
        return False
    for pipeline in _pipelines(command):
        seen_lookup = False
        for stage in pipeline:
            if seen_lookup and _xargs_runs_kill(stage):
                return True
            if _command_name(stage) in PID_LOOKUPS:
                seen_lookup = True
            if _runs_body(stage):
                for tok in stage:
                    if len(tok.split()) > 1 and _piped_lookup_to_kill(tok, depth + 1):
                        return True
    return False


def message() -> str:
    return (
        "BLOCKED: this selects processes by name, which matches EVERY instance -- including "
        "the user's daemons, terminal sessions and MCP servers, and possibly your own shell. "
        "On 2026-10-10 a name-based kill took out the kata daemon, six TUI sessions and two "
        "MCP servers, and the terminals did not come back.\n"
        "  Trace the PID from your own task's process tree instead: ps -o pid,ppid,cmd\n"
        "  Then kill the literal PID you traced: kill <literal-pid>"
    )


def verdict(command: str, cwd: str) -> str | None:
    """The block message for a name-based kill, else None."""
    for tokens in _segments(command):
        for candidate in (tokens, *_hidden_commands(tokens)):
            if _kills_by_name(candidate):
                return message()
    if _piped_lookup_to_kill(command):
        return message()
    return None


def main(stdin=sys.stdin, stderr=sys.stderr) -> int:
    try:
        data = json.load(stdin)
        tool_input = data.get("tool_input") or {}
        command = tool_input.get("command")
        cwd = data.get("cwd") or os.getcwd()
        if not isinstance(command, str):
            return 0
        text = verdict(command, cwd)
    except Exception:
        return 0
    if text:
        print(text, file=stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
