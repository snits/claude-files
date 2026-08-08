---
name: commit-decomposition
description: Use when breaking one or more oversized git commits into a series of logical commits — "decompose this commit", "break up this history", "atomic commits for this range". Lead-orchestrated - fresh subagent per patch, diff-parity gate, state file as cursor.
---

# Commit Decomposition

Rebuild a range of oversized commits as a readable series of logical commits,
with source parity guaranteed and zero risk of losing work. Mechanizes the
process that succeeded in the August 2025 Alpha Prime decomposition: the lead
never does surgery; durable state lives on disk; parity is the only in-flight
gate.

## The criterion: one logical change

A commit is one coherent, explainable step — kernel patch-series style. Read
`references/patch-series-style.md` before planning any split, and include it in
every subagent brief.

**There are no size limits.** No file counts, no line counts, no numeric
triggers. A 3,000-line mechanical rename can be one commit; a 40-line diff
mixing a bugfix with a refactor must be two. Justify boundaries by the change's
logic, never its size. (Numeric limits were tried in 2025 and produced absurd
granularity — agents optimized the metric instead of the history.) The one
standing structural rule: auto-generated content (lockfiles, build outputs)
gets its own isolated commit.

## Roles

- **Lead (you):** owns the cursor, applies gates, dispatches subagents, updates
  state. NEVER edits code or does git surgery directly — your context must
  survive a 100-patch run.
- **Per-patch subagent:** fresh context each patch; decomposes exactly one patch.

## Phase 0: Preflight (lead)

1. Require a clean tree (`git status --porcelain` empty). Stop if not.
2. Invoke the `git-anchoring` skill: anchor tag + backup branch on the original
   tip; dedicated worktree; work branch at the base commit
   (`git switch -c decompose/<slug> <base>` inside the worktree).
3. Require a linear range: `git rev-list --merges <base>..<anchor_ref>` must
   be empty. `git format-patch` silently emits nothing for merge commits,
   breaking the patch↔commit correspondence. A range with merges needs a
   different strategy — stop and consult the user.
4. Export the source of truth:
   `git format-patch <base>..<anchor_ref> -o <scratchpad>/patches/`
   (the anchor ref, not a remembered tip SHA). These files are the unloseable
   record; nothing that happens later can destroy the original commits.
5. The task scratchpad (`patches/`, `analysis/`, `state.json`) MUST live
   outside the worktree — no git operation inside the worktree (including a
   retry's `git clean -fd`) may be able to touch it.
6. Write `state.json` (git-anchoring schema; `cursor: 0`,
   `cursor_meaning: "patches completed; next patch file is %04d of cursor+1"`,
   `last_good: <base sha>`). `cursor` counts patches completed so far; the
   next patch file to process is `%04d` of `cursor+1` (`git format-patch`
   numbers patches from 0001).

## Phase 1: Per-patch loop (lead)

For each patch N — the 1-based patch-file number, N = `cursor+1` read from
`state.json` at the start of the step, never from memory:

1. **Dispatch** a fresh subagent with the brief template below. Model per the
   routing table: implementation tier; elevate when the patch looks
   judgment-heavy (tangled concerns, possible design questions).
2. **Parity gate (mechanical, non-negotiable):** after the subagent reports,
   run in the worktree — three checks, all mechanical, all must pass before
   the cursor advances:
   - **Tree parity:** `git diff <sha-from-patch-header-N> <work-branch> --stat`
     is empty. `<sha-from-patch-header-N>` comes from the first line of the
     patch file itself (`From <sha> Mon Sep 17 ...`) — read off disk per
     git-anchoring Rule 2, never recalled from context.
   - **History intact:** `git merge-base --is-ancestor <last_good> <work-branch>`
     succeeds. A subagent that squashed or amended already-approved commits
     can land the right tree while breaking this — treat it as a gate
     failure, not a pass.
   - **Worktree clean:** `git status --porcelain` is empty in the worktree.
     Uncommitted leftovers contaminate patch N+1's apply.

   - All three pass → record: update `state.json` (`cursor: N`,
     `last_good: <new tip>`); append one line to `<scratchpad>/progress.md`.
   - Any check fails → first capture the evidence for the retry brief (the
     failing `--stat` diff for a tree-parity failure; for a history-intact
     failure there is no diff — record instead that ancestry broke, i.e. the
     previous attempt amended or squashed existing commits) — do this BEFORE
     resetting, since the reset destroys it. Then `git switch <work-branch>`
     (ensure HEAD is on it), `git reset --hard <last_good>`, `git clean -fd`
     (safe here only because this runs inside the dedicated worktree and the
     scratchpad lives outside it), then re-dispatch ONCE with the captured
     evidence in the brief's retry-context section. Second failure → STOP,
     report to the user with the evidence. Never improvise past a failed gate.
3. Do not review commit-boundary quality mid-run — that is the optional
   Phase 2. Parity and progress only.

## Subagent brief template

Angle-bracket placeholders are filled in by the lead from `state.json` and the
patch file before every dispatch — never sent unresolved.

    **Role:** You are decomposing one oversized patch into logical commits.

    **Context:** Worktree <path>, work branch <branch>, currently at <last_good>.
    Patch file: <scratchpad>/patches/<NNNN-name.patch>. Original commit message
    is in the patch header.

    **Task:**
    1. Read <skill-dir>/references/patch-series-style.md first.
    2. Read the target files you will touch before editing them (harness rule).
    3. `git apply <patch-file>` (do NOT use git am).
    4. Split the working-tree changes into logical commits by selective staging
       (`git add <files>` / `git add -p`). Criterion: one coherent, explainable
       step per commit — the style reference governs. NO size-based splitting.
       Auto-generated files get an isolated commit.
    5. Each commit message: conventional prefix, subject explaining the step,
       body explaining why the boundary is where it is (when not obvious).
    6. Write <scratchpad>/analysis/patch-NNNN.md: the boundaries you chose and
       the reasoning, ~20 lines. This is a work product, not a formality.
    7. Do not touch refs matching anchor/* or backup/*. Do not push. Do not
       leave the worktree. Read `state.json` if you need the current tip, but
       NEVER write `state.json` or `progress.md` — they are lead-only
       bookkeeping, and the lead runs the gate. (A practice-run subagent
       updated them "helpfully"; the lead then had to re-derive the true
       last_good from progress.md to keep the ancestry check meaningful.)
    8. **Deviations log:** if anything forces you off this brief, take the
       conservative option and record it in the analysis file under
       `## Deviations`.

    **Done means:** working tree clean, all patch content committed, analysis
    file written. Report: number of commits created, one-line summary each.

    **Retry context (present only on re-dispatch):** the previous attempt
    failed the parity gate's <failed-check-name> check.
    - If tree parity failed: diagnose which hunks were missed or altered
      from the diff below and correct the decomposition.
      <failing-diff>
    - If history-intact failed: the previous attempt amended or squashed
      existing commits. Build strictly on top of <last_good> — never amend
      or squash a commit that already passed the gate.
    - If worktree-clean failed: the captured `git status --porcelain` output
      follows; the previous attempt left these paths uncommitted. Everything
      belonging to the patch must end up committed.
      <porcelain-output>

## Phase 2 (optional, after full parity): quality pass

Only after the final gate — `git diff <anchor_ref> <work-branch>` empty — walk
the new series for build/test health per commit (`git rebase --exec 'make ...'`
or equivalent) and message quality. Parity first, polish second: mixing these
concerns is what sank the 2025 attempts.

## Finish

Final parity check against the anchor ref, then
`superpowers:finishing-a-development-branch`. The original branch was never
touched; the anchor tag and backup branch are deleted only by the user after
they accept the result.
