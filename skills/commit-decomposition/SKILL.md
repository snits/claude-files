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
3. Export the source of truth:
   `git format-patch <base>..<original-tip> -o <scratchpad>/patches/`
   These files are the unloseable record; nothing that happens later can
   destroy the original commits.
4. Write `state.json` (git-anchoring schema; `cursor: 0`,
   `cursor_meaning: "next patch index"`, `last_good: <base sha>`).

## Phase 1: Per-patch loop (lead)

For each patch N (from `state.json`, not from memory):

1. **Dispatch** a fresh subagent with the brief template below. Model per the
   routing table: implementation tier; elevate when the patch looks
   judgment-heavy (tangled concerns, possible design questions).
2. **Parity gate (mechanical, non-negotiable):** after the subagent reports,
   run in the worktree:
   `git diff <sha-of-original-commit-N> <work-branch> --stat`
   - Empty → record: update `state.json` (`cursor: N+1`,
     `last_good: <new tip>`); append one line to `<scratchpad>/progress.md`.
   - Non-empty → `git reset --hard <last_good>`, re-dispatch ONCE with the
     failing diff included in the brief. Second failure → STOP, report to the
     user with the diff. Never improvise past a failed gate.
3. Do not review commit-boundary quality mid-run — that is the optional
   Phase 2. Parity and progress only.

## Subagent brief template

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
       leave the worktree.
    8. **Deviations log:** if anything forces you off this brief, take the
       conservative option and record it in the analysis file under
       `## Deviations`.

    **Done means:** working tree clean, all patch content committed, analysis
    file written. Report: number of commits created, one-line summary each.

## Phase 2 (optional, after full parity): quality pass

Only after the final gate — `git diff <anchor-tip> <work-branch>` empty — walk
the new series for build/test health per commit (`git rebase --exec 'make ...'`
or equivalent) and message quality. Parity first, polish second: mixing these
concerns is what sank the 2025 attempts.

## Finish

Final parity check against the anchor tip, then
`superpowers:finishing-a-development-branch`. The original branch was never
touched; the anchor tag and backup branch are deleted only by the user after
they accept the result.
