---
name: interactive-rebase
description: Use when you need to amend, split, or pause at a non-HEAD commit without an interactive editor — automates rebase via fixup/autosquash and GIT_SEQUENCE_EDITOR
---

# Automated Interactive Rebase for AI Agents and Scripts

When an AI agent or automated script needs to modify Git history, it typically cannot interact with terminal text editors like `vim` or `nano` that `git rebase -i` spawns by default.

The workaround: set `GIT_SEQUENCE_EDITOR` to a non-interactive command that produces the desired rebase todo list. Three common patterns:

- **Amend** a commit — `--fixup` + `--autosquash` + `GIT_SEQUENCE_EDITOR=true`
- **Pause** at a commit (to inspect, run a command, or split) — sed-modified todo list
- **Split** a commit into smaller commits — pause + `git reset` + re-commit

## Pattern 1: Amend a non-HEAD commit (autosquash)

### 1. Stage your changes

```bash
git add path/to/modified/file.c
```

### 2. Create a fixup commit

```bash
git commit -s --fixup <target-commit-hash>
```

This creates a commit whose message is `fixup! ` followed by the target's subject line.

### 3. Run the automated rebase

```bash
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <target-commit-hash>^
```

- `--autosquash` rearranges the todo so `fixup!` commits follow their targets with action `fixup`.
- `GIT_SEQUENCE_EDITOR=true` makes git "open" the editor with `true`, which exits 0 immediately — git proceeds as if you reviewed and saved the todo unchanged.

## Pattern 2: Pause at a specific commit (break / edit)

To stop the rebase at a chosen point and run commands manually, modify the todo list with sed instead of accepting it unchanged.

### Insert a `break` after a commit

```bash
GIT_SEQUENCE_EDITOR='sed -i "/^pick abc1234/a break"' git rebase -i abc1234^
```

The rebase applies `abc1234`, then stops at the inserted `break`. HEAD is `abc1234`. Do your work, then:

```bash
git rebase --continue
```

### Mark a commit for `edit`

```bash
GIT_SEQUENCE_EDITOR='sed -i "s/^pick abc1234/edit abc1234/"' git rebase -i abc1234^
```

Same effect as above, with one semantic difference: `edit` is for modifying the commit you just landed on (amend, split). `break` is for inserting unrelated work between commits (new commits, scripted operations).

## Pattern 3: Split a commit into multiple commits

Combine Pattern 2's `edit` with `git reset` to break a commit apart:

```bash
# 1. Pause with the target commit as HEAD
GIT_SEQUENCE_EDITOR='sed -i "s/^pick abc1234/edit abc1234/"' git rebase -i abc1234^

# 2. Uncommit, keeping the changes in the working tree (unstaged)
git reset HEAD^

# 3. Re-commit in pieces
git add path/to/first/group
git commit -s -m "first half: ..."
git add path/to/second/group
git commit -s -m "second half: ..."

# 4. Resume the rebase
git rebase --continue
```

This works cleanly for **file-boundary splits**. Hunk-level splits are harder because `git add -p` is interactive. Workarounds:

- Feed `git add -p` a heredoc of `y`/`n`/`s` answers (fragile — order-dependent on hunk numbering).
- Build patches with `git diff` + `git apply --cached <patch>` (more robust, more fiddly).

## Notes and gotchas

- The trailing `^` (e.g. `abc1234^`) means "the parent of" — rebase must start from the parent so the target commit appears in the todo list.
- `GIT_SEQUENCE_EDITOR` edits the rebase todo. `GIT_EDITOR` edits commit messages when the rebase pauses to reword. Set both non-interactively if your flow may trigger a reword.
- The sed examples assume GNU sed (Linux). BSD sed (macOS) requires a backup-extension argument to `-i` and uses different `a` syntax.
- Always confirm the target hash is on the current branch and that the working tree is clean (or stashed) before starting — a failed rebase mid-flight is harder to clean up than to prevent.

## Summary

```bash
# Amend (autosquash)
git add <files>
git commit -s --fixup <target>
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <target>^

# Pause at a commit (break)
GIT_SEQUENCE_EDITOR='sed -i "/^pick <target>/a break"' git rebase -i <target>^
# ... do work ...
git rebase --continue

# Split a commit
GIT_SEQUENCE_EDITOR='sed -i "s/^pick <target>/edit <target>/"' git rebase -i <target>^
git reset HEAD^
git add <piece1> && git commit -s -m "..."
git add <piece2> && git commit -s -m "..."
git rebase --continue
```
