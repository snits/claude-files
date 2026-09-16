#!/usr/bin/env python3
"""PreToolUse hook (matcher Bash): block a git restore/checkout that would discard
uncommitted work, and only then.

`git checkout -- <path>` discards *every* uncommitted change in that path, not just the
one the model meant to undo. Under subagent-driven development the commit comes after
verification by design, so that is routinely the entire task diff. CLAUDE.md records five
recurrences of this since 2026-06-04 across four projects; each was journaled and each
recurred anyway, because the rule lives in standing text and nothing intercepts the
command.

The guard blocks only when the named paths actually carry uncommitted changes, so a
no-op restore and an ordinary branch switch pass untouched. That is what keeps it from
being theatre: git itself permits the destruction silently, and the block fires exactly
on the destructive case.

Reuses claim_gate's shell segmentation so heredocs, quoting, line continuations and
`bash -c '...'` smuggling are handled identically in both guards.

Exit 2 blocks the call and shows stderr to the model. Any internal error exits 0: a
guard that fails closed on its own bug would be worse than the hazard.
"""
import json
import os
import subprocess
import sys

from claim_gate import _hidden_commands, _segments

FLAGS_WITH_VALUE = {"--source", "-s", "--pathspec-from-file", "--conflict", "--ours", "--theirs"}

# git's own global options that consume the next word. `-C` also relocates the repo the
# command acts on, so the dirty check has to follow it or it inspects the wrong tree.
GIT_GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace",
                         "--exec-path", "--config-env", "--super-prefix"}


PREFIXES = {"sudo", "command", "env", "nohup", "time", "nice", "doas"}


def _git_command_index(tokens: list[str]) -> int | None:
    """Index of `git` when it is the command being run, not merely a word.

    `echo git checkout -- f` must not block: claim_gate can afford to match `git`
    anywhere because a false positive there costs one spare reminder, but a false
    positive here blocks a legitimate command. Leading `VAR=val` assignments and
    wrapper words (sudo, env, nohup...) are skipped; anything else means git is an
    argument to another program.
    """
    for i, tok in enumerate(tokens):
        name = tok.rsplit("/", 1)[-1]
        if name == "git":
            return i
        if "=" in tok and not tok.startswith("-") and tok.split("=", 1)[0].isidentifier():
            continue
        if name in PREFIXES or tok.startswith("-"):
            continue
        return None
    return None


def _git_subcommand(tokens: list[str], idx_git: int) -> tuple[int | None, str | None]:
    """(index of git's subcommand, value of -C if given).

    git's global options sit before the subcommand and several consume the next word, so
    a naive "first non-flag word" scan reads `git -C /repo checkout` as the subcommand
    `/repo`. That shape is common here -- and silently not matching means the guard waves
    the destructive command through, which is the failure direction that looks like
    success.
    """
    chdir = None
    i = idx_git + 1
    while i < len(tokens):
        tok = tokens[i]
        if tok in GIT_GLOBAL_WITH_VALUE:
            if tok == "-C" and i + 1 < len(tokens):
                chdir = tokens[i + 1]
            i += 2
            continue
        if tok.startswith("--") and "=" in tok:
            if tok.startswith("--git-dir=") or tok.startswith("--work-tree="):
                pass
            i += 1
            continue
        if tok.startswith("-"):
            i += 1
            continue
        return i, chdir
    return None, chdir


def _split_paths(tokens: list[str], verb_idx: int) -> tuple[list[str], bool, bool]:
    """(paths, has_treeish, saw_dashdash) for one checkout/restore segment.

    Everything after `--` is a pathspec. Before it, a non-flag word is a tree-ish for
    checkout (`git checkout HEAD -- f`) and a pathspec only when no `--` appeared.
    """
    rest = tokens[verb_idx + 1:]
    paths: list[str] = []
    pre: list[str] = []
    saw = False
    skip_next = False
    for tok in rest:
        if skip_next:
            skip_next = False
            continue
        if tok == "--":
            saw = True
            continue
        if saw:
            paths.append(tok)
            continue
        if tok.startswith("-"):
            if tok in FLAGS_WITH_VALUE and "=" not in tok:
                skip_next = True
            continue
        pre.append(tok)
    if saw:
        return paths, bool(pre), True
    return pre, False, False


def _destructive(tokens: list[str], cwd: str) -> tuple[list[str], bool, bool, str] | None:
    """(paths, check_worktree, check_index, repo_dir) when this segment can discard work.

    repo_dir comes back with the result because `git -C <dir>` relocates the tree the
    command acts on: checking the caller's cwd instead would ask a clean repo about a
    dirty one and wave the command through.
    """
    idx_git = _git_command_index(tokens)
    if idx_git is None:
        return None
    idx, chdir = _git_subcommand(tokens, idx_git)
    if idx is None or tokens[idx] not in ("checkout", "restore"):
        return None
    if chdir:
        cwd = chdir if os.path.isabs(chdir) else os.path.join(cwd, chdir)
    paths, has_treeish, saw_dashdash = _split_paths(tokens, idx)
    if not paths:
        return None

    if tokens[idx] == "restore":
        staged = "--staged" in tokens or "-S" in tokens
        worktree = "--worktree" in tokens or "-W" in tokens
        sourced = any(t == "--source" or t.startswith("--source=") or t == "-s" for t in tokens)
        if staged and not worktree and not sourced:
            return paths, False, True, cwd          # index from HEAD: staged work at risk
        return paths, True, staged or sourced, cwd  # worktree from index (or a source)

    # checkout: a bare pathspec must look like a real path, or it is a branch name.
    if not saw_dashdash and not all(p == "." or os.path.exists(os.path.join(cwd, p)) for p in paths):
        return None
    return paths, True, has_treeish, cwd


def _dirty(paths: list[str], cwd: str, worktree: bool, index: bool) -> bool:
    """True if any named path carries changes the command would destroy."""
    checks = []
    if worktree:
        checks.append(["git", "diff", "--quiet", "--", *paths])
    if index:
        checks.append(["git", "diff", "--quiet", "--cached", "--", *paths])
    for cmd in checks:
        try:
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=10)
        except Exception:
            return False
        if r.returncode == 1:
            return True
    return False


def message(paths: list[str]) -> str:
    shown = " ".join(paths)
    return (
        f"BLOCKED: this discards ALL uncommitted changes in {shown}, not just the one you "
        "meant to undo. Under subagent-driven development the commit comes after "
        "verification, so that is routinely the entire task diff (CLAUDE.md records five "
        "such losses across four projects).\n"
        "  Undo a deliberate break with the inverse Edit instead -- the edit is small and known.\n"
        f"  If you really want a git-level revert: git stash push {shown}\n"
        "  Then re-run this command if you still want it."
    )


def verdict(command: str, cwd: str) -> str | None:
    """The block message for a destructive command with work at stake, else None."""
    for tokens in _segments(command):
        for candidate in (tokens, *_hidden_commands(tokens)):
            hit = _destructive(candidate, cwd)
            if hit and _dirty(hit[0], hit[3], hit[1], hit[2]):
                return message(hit[0])
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
