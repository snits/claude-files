#!/usr/bin/env python3
# ~/.claude/scripts/git_surgery_guard.py
"""PreToolUse guard for Bash git commands.

Blocks (exit 2, reason on stderr):
  1. Commands that would ENTER detached HEAD (checkout <non-branch>, switch --detach).
  2. Mutating git commands while ALREADY detached (rescue procedure in message).
  3. Raw-git mutations on an stgit-managed branch (silent stack desync).

Never blocks read-only commands. On any parse/classification failure: allow —
the PostToolUse desync detector is the safety net.
"""
import json
import shlex
import subprocess
import sys
from pathlib import Path

MUTATING = {
    "commit", "checkout", "switch", "reset", "rebase", "am",
    "merge", "cherry-pick", "revert",
}
# checkout/switch to another branch is safe on an stg branch; the stack refs stay put.
STG_UNSAFE = {"commit", "rebase", "reset", "cherry-pick", "am", "merge", "revert"}

OPERATORS = {"&&", "||", ";", ";;", "|", "&"}


def git(repo, *args):
    """Run git, return (rc, stdout). Never raises."""
    try:
        p = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, timeout=5,
        )
        return p.returncode, p.stdout.strip()
    except Exception:
        return 1, ""


def split_segments(command):
    """Tokenize with shlex, then split the token list on operator tokens.

    Tokenizing before splitting means a quoted metacharacter (e.g. a commit
    message containing "&&") stays part of its token instead of being
    mistaken for a shell operator. punctuation_chars=True makes shlex emit
    ";", "&&", "|" etc. as their own tokens even when jammed against
    adjacent commands with no whitespace (e.g. "git status;git checkout").
    Newlines are normalized to ";" first so newline-separated commands split
    the same way. None if unparseable.
    """
    command = command.replace("\n", " ; ")
    lex = shlex.shlex(command, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    lex.commenters = ""  # bare shlex.shlex defaults to '#': would truncate at unquoted #
    try:
        tokens = list(lex)
    except ValueError:
        return None
    segments = []
    current = []
    for tok in tokens:
        if tok in OPERATORS:
            if current:
                segments.append(current)
            current = []
        else:
            current.append(tok)
    if current:
        segments.append(current)
    return segments


def parse_git_invocation(tokens, cwd):
    """Return (repo_dir, subcommand, args) for a git segment, else None."""
    if not tokens or Path(tokens[0]).name != "git":
        return None
    repo = cwd
    i = 1
    while i < len(tokens):
        t = tokens[i]
        if t == "-C" and i + 1 < len(tokens):
            repo = str(Path(cwd) / tokens[i + 1])
            i += 2
        elif t == "-c" and i + 1 < len(tokens):
            i += 2
        elif t.startswith("--git-dir") or t.startswith("--work-tree") or t.startswith("-"):
            i += 1
        else:
            return repo, t, tokens[i + 1:]
    return None


def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def is_local_branch(repo, name):
    rc, _ = git(repo, "show-ref", "--verify", "-q", f"refs/heads/{name}")
    return rc == 0


def resolves_to_commit(repo, name):
    rc, _ = git(repo, "rev-parse", "--verify", "-q", f"{name}^{{commit}}")
    return rc == 0


def is_head_reachable(repo):
    """True if the current (possibly detached) HEAD is already reachable
    from some existing branch or tag. Fails toward blocking: any error
    running the check itself counts as unreachable, since the rescue
    command (git switch -c rescue/<slug>) always works regardless."""
    # for-each-ref, not `branch --contains`/`tag --contains`: the latter
    # prints a "* (HEAD detached from ...)" placeholder line even when
    # nothing is reachable, which would false-positive as reachable.
    rc, refs = git(
        repo, "for-each-ref", "--contains", "HEAD",
        "--format=%(refname)", "refs/heads", "refs/tags",
    )
    if rc != 0:
        return False
    return bool(refs)


def resolves_to_head(repo, ref):
    """True if `ref` names the same commit as current HEAD. Used to treat
    an explicit start-point that happens to equal HEAD as equivalent to no
    start-point at all — both leave the new branch's tip at current HEAD."""
    rc, head_sha = git(repo, "rev-parse", "-q", "--verify", "HEAD^{commit}")
    if rc != 0:
        return False
    rc, ref_sha = git(repo, "rev-parse", "-q", "--verify", f"{ref}^{{commit}}")
    if rc != 0:
        return False
    return bool(head_sha) and head_sha == ref_sha


def escapes_detached_head(repo, args):
    """True if this checkout/switch is a safe way out of detached HEAD.

    A branch-creating form (-b/-B/-c/-C) is unconditionally safe only when
    it has no start-point argument (or the start-point resolves to current
    HEAD) and no -t/--track: the new branch then starts at HEAD, so the
    detached chain becomes that branch's tip and nothing is orphaned.
    Pathspec checkouts ("--") are always safe too (they never move HEAD).

    Everything else — a branch-creating form WITH a start-point other than
    HEAD, --orphan, -t/--track, "-" (previous ref), or landing on an
    existing local branch — moves HEAD to a ref chosen independently of
    current HEAD, so it's only safe if the detached HEAD is already
    reachable from some other ref. Otherwise commits made while detached
    would be silently orphaned the moment HEAD moves off them. (--orphan
    looks harmless since it starts a brand-new unrelated root, but that's
    exactly the problem: nothing keeps the old detached chain reachable
    once HEAD moves.)
    """
    if checkout_would_detach(repo, args):
        return False  # lands on yet another commit, still detached
    if "--" in args:
        return True
    if "-" in args:
        # "-" (previous ref) is a single-char token that also matches the
        # startswith("-") flag filter below, so it must be caught here —
        # it picks a ref independent of current HEAD, same as any other
        # existing-branch target, and needs the reachability gate.
        return is_head_reachable(repo)
    targets = [a for a in args if not a.startswith("-")]
    if not targets:
        return True
    branch_creating = any(a in ("-b", "-B", "-c", "-C") for a in args)
    has_track = any(a in ("-t", "--track") for a in args)
    if branch_creating and not has_track:
        if len(targets) <= 1:
            return True  # no start-point: new branch starts at current HEAD
        if len(targets) == 2 and resolves_to_head(repo, targets[1]):
            return True  # start-point IS current HEAD: equivalent to none
    return is_head_reachable(repo)


def checkout_would_detach(repo, args):
    """True if `git checkout`/`switch <args>` leaves HEAD detached.

    False for anything that lands on a ref: -b/-B (checkout) or -c/-C
    (switch) create-and-move-to a new branch, --orphan/-t/--track track a
    branch, and an existing local-branch target moves HEAD to that branch.
    """
    if any(a in ("-b", "-B", "-c", "-C", "--orphan", "-t", "--track") for a in args):
        return False
    if "--detach" in args:
        return True
    if "--" in args:
        return False  # pathspec checkout, does not move HEAD
    targets = [a for a in args if not a.startswith("-")]
    if not targets:
        return False
    target = targets[0]
    if target == "-" or is_local_branch(repo, target):
        return False
    # Existing file paths are pathspec checkouts even without an explicit "--".
    if (Path(repo) / target).exists():
        return False
    return resolves_to_commit(repo, target)


def check_segment(tokens, cwd):
    parsed = parse_git_invocation(tokens, cwd)
    if parsed is None:
        return  # not a git command (stg, ls, ...): always allowed
    repo, sub, args = parsed
    if sub not in MUTATING:
        return
    if sub == "commit" and "--dry-run" in args:
        return  # doesn't mutate

    rc, _ = git(repo, "rev-parse", "--git-dir")
    if rc != 0:
        return  # not a repo; nothing to guard

    _, git_dir = git(repo, "rev-parse", "--absolute-git-dir")
    if git_dir and (Path(git_dir) / "BISECT_LOG").exists():
        return  # bisect in progress: legit detached-HEAD use

    detached = git(repo, "symbolic-ref", "-q", "HEAD")[0] != 0
    if detached:
        # Leaving detached HEAD for a ref (checkout/switch onto an existing
        # branch, or -b/-B/-c/-C creating one) is the prescribed recovery —
        # never block it. Anything else while detached still risks orphaning
        # work: other mutating subcommands, or checkout/switch to yet
        # another non-branch commit (still detached afterward), or checkout
        # onto an existing branch that would abandon unreachable commits
        # made while detached.
        recovers = sub in ("checkout", "switch") and escapes_detached_head(repo, args)
        if not recovers:
            _, sha = git(repo, "rev-parse", "--short", "HEAD")
            block(
                f"[git-surgery-guard] BLOCKED: HEAD is detached at {sha} and "
                f"'git {sub}' would risk orphaning work.\n"
                f"First attach your work to a ref:  git switch -c rescue/<slug>\n"
                f"That makes everything on this HEAD unloseable. Then continue.\n"
                f"(Diagnosis commands — status/log/diff/reflog — are not blocked.)"
            )

    if sub == "checkout" and checkout_would_detach(repo, args):
        target = next((a for a in args if not a.startswith("-")), "<sha>")
        block(
            f"[git-surgery-guard] BLOCKED: 'git checkout {target}' would enter "
            f"detached HEAD. Work built there is orphaned the moment anything "
            f"else is checked out.\n"
            f"Use a named branch instead:  git switch -c tmp/<name> {target}"
        )
    if sub == "switch" and ("--detach" in args or "-d" in args):
        block(
            "[git-surgery-guard] BLOCKED: 'git switch --detach' enters detached "
            "HEAD. Use a named branch:  git switch -c tmp/<name> <commit>"
        )

    _, branch = git(repo, "branch", "--show-current")
    if branch and sub in STG_UNSAFE:
        rc, _ = git(repo, "show-ref", "--verify", "-q", f"refs/stacks/{branch}")
        if rc == 0:
            block(
                f"[git-surgery-guard] BLOCKED: branch '{branch}' is stgit-managed "
                f"(refs/stacks/{branch} exists). Raw 'git {sub}' silently desyncs "
                f"the patch stack — stg won't notice until its next operation.\n"
                f"Use the stg equivalent (stg refresh / stg new / stg edit ...), "
                f"or if raw git is genuinely required, run 'stg repair' "
                f"immediately afterward."
            )


def main():
    try:
        payload = json.load(sys.stdin)
        command = payload.get("tool_input", {}).get("command", "")
        cwd = payload.get("cwd") or "."
    except Exception:
        sys.exit(0)
    segments = split_segments(command)
    if segments is None:
        sys.exit(0)  # unparseable: allow; the desync detector backstops
    for tokens in segments:
        try:
            check_segment(tokens, cwd)
        except SystemExit:
            raise
        except Exception:
            continue
    sys.exit(0)


if __name__ == "__main__":
    main()
