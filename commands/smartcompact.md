---
name: smartcompact
description: Use when preparing to do a manual compaction of the context
---

Prepare for compaction by making the summary not matter: flush all
load-bearing state to durable storage BEFORE the context is compacted.
Modern compaction summarizes well on its own — do not write summary
instructions for it. Instead:

**1. Flush in-flight state to session-handoff.md**
Update (or create) the handoff file with anything a fresh context would need
to continue seamlessly: current task and its stage, running background work
(task IDs, workflow run IDs, output paths), branch/worktree state, decisions
made this session that aren't yet recorded elsewhere, and the next action.
Delete stale entries while there.

**2. Journal unjournaled insights**
If the session produced discoveries, failed approaches, or lessons not yet in
mnemosyne, call `process_thoughts` now. Conversation context is the only
place they exist until you do.

**3. Audit for conversation-only state**
Ask: "Is anything load-bearing ONLY in this conversation?" — an agreement
with Jerry, a path, an ID, a constraint, a half-finished plan. If yes, put it
in the handoff file, a bead comment, or memory. Beads and `bd prime` survive
compaction; chat nuance does not.

**4. Emit a focus hint only if needed**
If something unusual is in flight that auto-compaction might deprioritize
(e.g., "a background workflow wf_XXX is running; its notification must be
acted on"), give Jerry a ONE-LINE focus hint to pass to /compact. Otherwise
say plain /compact is fine — no curated summary string needed.

Then tell Jerry the flush is done and compaction is safe.
