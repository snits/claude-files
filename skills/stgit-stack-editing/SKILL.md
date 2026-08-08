---
name: stgit-stack-editing
description: Use when amending, reordering, or splitting commits in an in-progress patch series — especially fixing reviewer findings inside the offending commit instead of stacking fixup commits. Stacked Git (stg) alternative to interactive-rebase.
---

# Editing a patch stack with Stacked Git

stgit treats a branch tip as a stack of named patches. Position is explicit in
`stg series` — not in your memory — which makes it safer for agents than
rebase-based editing, PROVIDED one rule is never broken.

## The one commandment

**On an stg-managed branch (refs/stacks/<branch> exists), repo state is
modified with stg commands only.** A raw `git commit`/`rebase`/`reset`/
`cherry-pick`/`am`/`merge`/`revert` silently desyncs the stack: stg gives NO
error at the time — `stg series` keeps showing stale state — and the breakage
surfaces only when a later stg operation misbehaves. (Verified on stg 2.6.1.)

If raw git has touched the repo anyway (a script, a hook, an accident): run
`stg repair` BEFORE the next stg command. It absorbs stray commits into new
patches non-destructively. The surgery-guard hook blocks the obvious raw
mutations and the desync detector warns after sneaky ones — treat a
[stg-desync-detector] warning as a stop-everything instruction.

## Setup

    stg init                # once per branch, on the branch itself
    stg series              # the stack; '>' marks the current (topmost applied) patch
    stg series -d           # with descriptions

Importing existing commits into a stack: `stg uncommit -n <N>` converts the
last N commits into patches (newest patch on top).

## The reviewer-fix workflow (fix it IN the commit)

Reviewer found a problem in patch `add-frobnicator`, three patches down:

    stg goto add-frobnicator      # pops later patches, lands on the target
    # ... edit files to fix the finding ...
    stg refresh                    # folds working-tree changes into this patch
    stg goto <top-patch>           # reapply the rest (or: stg push -a)

If reapplying conflicts, stg stops with the conflict in the working tree:
resolve, `git add <files>` (allowed: conflict resolution is part of the stg
push operation), then `stg push -a` to continue. `stg undo` rolls back the
last stg operation if you get tangled.

Message-only edits: `stg edit <patch>` (add `-d` to edit the diff too).

## Other stack operations

    stg new -m "msg" <name>   # new empty patch on top; then edit + stg refresh
    stg pop / stg push        # move the stack boundary down / up
    stg spill                 # empty the top patch, keep changes staged in the tree
                              #   (start of a split: re-stage into stg new patches)
    stg squash -n <name> p1 p2 p3   # merge adjacent patches into one
                                     #   (bare `stg squash p1 p2` works too, but
                                     #   opens an interactive editor for the
                                     #   message — pass -n/-m to stay scriptable)
    stg float / stg sink      # reorder patches (float = to top, sink = to bottom)
    stg delete <patch>        # drop a patch entirely
    stg log                   # stg's own operation history (its reflog)

## When to prefer interactive-rebase instead

One-off amendment of a single commit on a branch that is not stack-managed:
the `interactive-rebase` skill is lighter. Reach for stgit when a series is
being actively reworked — multiple round-trips, reordering, splitting — and
the stack will live for a while.
