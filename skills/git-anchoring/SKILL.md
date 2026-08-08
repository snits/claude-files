---
name: git-anchoring
description: Use before any git surgery — history rewriting, commit decomposition, rebase-heavy work, or any task that moves refs around. Establishes anchor refs, on-disk state, and worktree isolation so work cannot be orphaned and any fresh context can re-orient. Also use when recovering seemingly lost commits.
---

# Git Anchoring: surgery without losing work

Work is lost in git surgery when the only pointer to it lives in an agent's
context — which does not survive compaction or confusion. These three rules make
loss structurally impossible. The detached-HEAD guard hook enforces rule 3's
HEAD half; the rest is protocol.

## Rule 1: Anchor before surgery

Before touching anything:

    git tag anchor/<task>-$(date +%Y%m%d) <original-tip>
    git branch backup/<task> <original-tip>

Anchors are READ-ONLY for the task's duration. Never rebase, delete, or move
them. Every parity/progress check compares against the anchor ref, never
against a SHA remembered in context.

## Rule 2: State on disk, not in context

Maintain `state.json` in the task's scratchpad directory, updated after EVERY
step that changes repo position:

    {
      "task": "<slug>",
      "original_branch": "main",
      "base_sha": "<sha surgery builds on>",
      "anchor_ref": "anchor/<task>-<date>",
      "work_branch": "<branch surgery happens on>",
      "worktree_path": "/abs/path",
      "cursor": 7,
      "cursor_meaning": "next patch index to process",
      "last_good": "<sha of work branch at last verified step>"
    }

A compacted or freshly-dispatched agent re-orients by reading this file — never
by recalling. If the file and the repo disagree, the repo is truth; fix the file.

## Rule 3: Named branches only, in a dedicated worktree

Surgery happens on a named work branch inside a dedicated worktree
(`superpowers:using-git-worktrees`), never in the main checkout, and HEAD is
never detached (`git switch -c tmp/<name> <sha>` replaces `git checkout <sha>`;
the guard hook blocks the latter). Commits on named branches are unloseable.

## Recovery: "lost" commits almost never are

Orphaned commits stay in the object store; they merely lack a ref. To recover:

1. `git reflog` — walk backwards for the tip of the lost chain
   (`git reflog --date=iso | grep -i <keyword>` helps).
2. `git fsck --lost-found` — lists dangling commits when the reflog trail is cold.
3. Inspect candidates: `git log --oneline --graph <sha>`.
4. Attach immediately: `git branch rescue/<slug> <sha>`. THEN investigate at leisure.

The failure mode to avoid while recovering: checking out candidate SHAs to
"look around" — that is more detached-HEAD surgery. Attach a branch first.
