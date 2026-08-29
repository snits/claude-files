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

**2. Fetch.** `python3 ~/.claude/scripts/dream_corpus.py dump --since <cursor> -o <file>`
— a read-only JSONL dump straight from the journal's PostgreSQL store (each line:
`{p: file_path, d: date, proj, c: content}`). Note the newest entry timestamp — it
becomes the new cursor. Do NOT use `mcp__mnemosyne__show_entries_since` for bulk
fetches: a no-limit full-corpus call crashed the MCP server on 2026-08-29 (~13.5K
entries / 24MB in one response); the MCP surface is for interactive recall only.

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
is the spike's hybrid, run RLM-style against the DB via
`~/.claude/scripts/dream_corpus.py` (Jerry ruling, 2026-08-29: treat the corpus as data
you query with code; spend model calls only on rows that matter). Spike reference
implementation remains in `~/devel/mnemosyne/.scratchpad/zhqp-spike/`:
  - Arm A: `dream_corpus.py search "<query>" -k 15` — pgvector cosine directly
    (qwen3-embedding-8b via llama-swap :11435, same model and instruct prefix as
    mnemosyne's own search), seeded from the theme's ledger vocabulary. Calibrate on
    one known-relevant entry before trusting a miss.
  - Arm B: `dream_corpus.py dump` the full corpus, slice at entry boundaries
    (~650KB/slice), fan out cheap readers (haiku-tier subagents, batches under the
    20-concurrent cap), each returning candidate paths + why. Expect reader noise:
    off-theme drift and missed instances both occurred on 2026-08-29; the two arms
    cross-check each other — investigate any arm-A hit inside a slice whose reader
    reported zero.
  - Editor (session-tier, you): judge the pooled candidates, read raw rows
    (`dream_corpus.py show <path>`), write the pearl — Bentley-column register,
    provenance links (entry paths + dates) on every instance, every quote re-verified
    with `dream_corpus.py verify <path> "<fragment>"` (readers paraphrase and
    mis-path at every model tier; verify recovers the true path on a miss).

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
