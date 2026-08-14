---
name: dream
description: Use when Jerry invokes /dream or when the startup DREAM due-check reports 7+ days since the last pass. Weekly editorial inquiry over the mnemosyne journal — maintains existing pearls, spots candidate themes, and emits proposals into the vault promotion gate. Read-only against the journal.
---

# Dream pass

A periodic editorial inquiry over the journal: squeeze the corpus until something like
Programming Pearls pops out. Direction settled by the one-pearl spike (mnemosyne kata zhqp,
ruling 2026-08-11); architecture recorded on kata p48f.

**Hard rules:**
- READ-ONLY against the journal. Never write entries or distillations.
- All output is PROPOSALS into `~/vault/_inbox/dream/`. Never edit `atlas/`, `MEMORY.md`,
  CLAUDE.md, memory files, or skills directly.
- Every verbatim quote is re-verified against the raw journal entry before it enters a
  proposal. The spike showed reader misattribution and paraphrase-as-quote: the pool
  selects, the raw row cites. A quote you cannot re-find verbatim is a paraphrase — mark
  it as one or drop it.

## Procedure

**1. State.** Read `~/.claude/dream/last-pass` (ISO date of last pass) and
`~/.claude/dream/cursor` (timestamp bound of last processed entry). Read
`~/.claude/dream/ledger.md` (candidate themes) and the pearl inventory (vault atlas
entries tagged `pearl`, plus any un-promoted pearl stubs in `~/vault/_inbox/dream/`).

**2. Fetch.** `mcp__mnemosyne__show_entries_since` with `since: <cursor>`,
`project_filter: "all"`, no limit. Note the newest entry timestamp — it becomes the new
cursor. If the volume is large (a long gap), fetch in date slices rather than raising a
limit, so nothing is silently dropped.

**3. Job A — maintenance.** Read every fetched entry against the existing pearls. Where
an entry is a genuine new instance of a pearl's theme (not a mention — an instance, with
its own evidence), draft an amendment proposal: which pearl, the new instance with entry
id and date, the verified quote or a marked paraphrase, and where in the pearl it lands.

**4. Job B — discovery.** Update `~/.claude/dream/ledger.md`: for each theme already
listed, append new instances (entry id, date, project, one-line description). For
recurring patterns not yet listed, add a theme section. **Ripeness rule:** instances
across 3+ projects, or 5+ instances spanning 2+ months. Mark ripe themes `status: ripe`.

**5. Pearl drafting (only when a theme is ripe, this pass or next — editor's call).**
A new pearl hunts the FULL corpus, not just the window — the spike proved the archive's
old stories are what similarity search misses and what gives a pearl its arc. Procedure
is the spike's hybrid, reference implementation in
`~/devel/mnemosyne/.scratchpad/zhqp-spike/` (dump_slices.py, compare_arms.py, manifest):
  - Arm A: cosine queries (`mcp__mnemosyne__search_journal`) seeded from the theme's
    ledger vocabulary.
  - Arm B: slice the corpus and fan out cheap readers (haiku-tier subagents), each
    returning candidate entry ids + why.
  - Editor (session-tier, you): judge the pooled candidates, read the raw rows, write
    the pearl — Bentley-column register, provenance links (entry ids + dates) on every
    instance, every quote re-verified.

**6. Culling.** If the window's reading shows a loaded surface entry (memory file,
vault entry, pearl section) superseded by newer evidence, draft a culling proposal
naming what supersedes what. Culling proposals are dream output too — arguably the most
valuable kind.

**7. Write proposals** to `~/vault/_inbox/dream/<slug>.md`, one file per proposal, using
the vault intake-stub schema (`~/vault/_system/schemas.md`):

```yaml
---
name: <slug>
type: intake
subtype: pearl
description: <~150 chars — say whether this is a new pearl, an amendment, or a culling proposal>
provenance: agent-proposed
source_url: <primary provenance path, e.g. the pearl draft or the superseding entry>
agent_id: dream
ingested: <YYYY-MM-DD>
sha256: <hash of the file named by source_url>
status: pending-promotion
---
```

`sha256` hashes the file named by `source_url`, never the stub's own body — it exists so
promotion can detect that the material drifted since the proposal was written. There is no
per-subtype interpretation: whatever path you put in `source_url`, hash that same file.
Compute it with `sha256sum` on the resolved path.

Body: the pearl text, amendment, or culling case. Amendments and cullings state their
target explicitly ("amends atlas/<...>/<slug>.md", "supersedes <path>"). Promotion is
Jerry's; a pass that produces zero proposals is a valid pass.

**8. Stamp state — last.** Only after proposals are written: today's date into
`~/.claude/dream/last-pass`, the newest fetched entry timestamp into
`~/.claude/dream/cursor`. Commit `~/.claude/dream/` and any ledger changes if `~/.claude`
is a git repo.

**9. Report.** Tell Jerry: window covered, entries read, Job A amendments, ledger deltas,
ripe themes, proposals written (paths). If a ripe theme was deferred to next pass, say so.
