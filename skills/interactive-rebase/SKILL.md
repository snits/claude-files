---
name: interactive-rebase
description: Use when you need to amend a non-HEAD commit in git history without an interactive editor — automates rebase via fixup, autosquash, and GIT_SEQUENCE_EDITOR=true
---

# Automated Interactive Rebase for AI Agents and Scripts

When an AI agent or automated script needs to modify a specific commit in Git history, it typically cannot interact with terminal text editors like `vim` or `nano` that `git rebase -i` spawns by default. 

To work around this, you can use a combination of Git's `--fixup`, `--autosquash`, and a temporary environment variable to perform a fully automated "interactive" rebase.

## Step-by-Step Guide

### 1. Make your changes
Make the necessary modifications to the files in your workspace and stage them using `git add`:

```bash
git add path/to/modified/file.c
```

### 2. Create a fixup commit
Create a new commit using the `--fixup` flag, pointing it to the hash of the commit you want to amend.

```bash
git commit --fixup <target-commit-hash>
```
*What this does:* This creates a standard commit, but prefixes the commit message with `fixup! ` followed by the subject line of the target commit.

### 3. Run the automated rebase
Execute the interactive rebase targeting the parent (or any older ancestor) of the commit you are modifying, using `--autosquash` and bypassing the editor.

```bash
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <target-commit-hash>^
```

*What this does:*
- `--autosquash`: Tells Git to automatically look for `fixup!` commits and rearrange the interactive rebase "todo" list so they immediately follow their target commits with the action set to `fixup`.
- `GIT_SEQUENCE_EDITOR=true`: Git normally halts and opens a text editor (like `vim`) to let you review the rebase todo list. By setting the sequence editor to the shell command `true` (which immediately exits with a `0` success code), Git behaves as if the user opened the editor, made no manual changes, saved, and closed it instantly. The rebase then proceeds automatically.

## Summary

```bash
# 1. Stage changes
git add <files>

# 2. Create fixup commit
git commit --fixup <commit-to-change>

# 3. Rebase and squash automatically
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <commit-to-change>^
```