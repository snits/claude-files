---
name: manage-vault
description: loop for advancing the ~/vault intake backlog and prepping _inbox proposals for Jerry's promotion gate
---

You are working in `~/vault`. Each firing you advance **at most one** item of vault work.
Read `_system/routing.md` before acting — it is the contract, and this prompt does not
restate it.

## Preconditions — check both, in order, before anything else

1. `git -C ~/vault status --porcelain` — if non-empty, stop. Report the dirty paths and exit
   without touching anything. `promote.py` regenerates `_surface/index.html` into the working
   tree, and you would stage someone else's work into your commit.
2. `cd ~/vault && python3 _system/promote.py --backlog` — this is the ingest queue. It lists
   promoted intake material that still owes the ingest loop. **Do not use `ls intake/`**; most
   of those files are already integrated.

## Work priority

**A. Ingest backlog** (`--backlog` non-empty) — take the first item and run the ingest loop.
**B. Inbox prep** (backlog empty, `_inbox/**/*.md` non-empty) — prepare one proposal for
Jerry's gate. You never promote it.
**C. Nothing** — both empty. This is the expected case; see below.

Do exactly one item of work, then stop. Do not chain A into B in the same firing.

## A. Ingest one backlog item

1. Read the intake source in full.
2. Find its atlas home. Which branch you take depends on the source's `subtype:`.

   **`subtype: case-study`** — the home is `atlas/case-studies/<slug>.md`, same slug as the
   source, one entry per subject studied. There is never a pre-existing target, so **you may
   create this entry** — the sole exception to the ceiling below. The judgment the ceiling
   protects was already made by Jerry when he promoted the study; the target's name is
   mechanical, not chosen. Read every other entry in `atlas/case-studies/` first — the series
   is cumulative and a study's recurrence claims are checked against its siblings.

   **Anything else** — identify the *existing* atlas entry it belongs to and read that entry
   in full first. If none exists, you may **not** create one: write what you found, file it,
   and stop (see "Route ambiguity out").
3. Fold the source's contribution into the entry's body — integrate the claim, do not restate
   the source — and append its `## Sources` line. `## Sources` is append-only; never rewrite
   an existing entry there.

   For a case-study entry you are creating, this is a synthesis, not a copy: the intake file
   is the session's raw essay, the atlas entry is the curated one. Frontmatter takes the
   **Atlas case study** contract in `_system/schemas.md` — `type: case-study`,
   `provenance: inbox-promoted` (`routing.md:16` — authoring under Jerry's direction does not
   confer a `jerry-*` provenance), and `subject:` naming the system studied.
4. If the source contradicts the current body, follow the contradiction rules in `routing.md`
   (`contradictions:`, both sides dated, `contested:` where the claim itself is disputed).
5. Add the `MEMORY.md` index line by hand: `- [slug](atlas/.../slug.md) — description`.
   **`--ingest` does not write it** — `_append_memory_line` runs only on the promotion path
   (`promote.py:279`), so nothing enforces `routing.md`'s one-index-line-per-atlas-file rule
   on this hop. Skip only if the entry already existed and already has its line.
6. Record it:
   `python3 _system/promote.py --ingest intake/<subtype>/<slug>.md --into atlas/<concepts|case-studies>/<slug>.md --by jerry-directed`

   The gate refuses unless the target already exists *and* already cites the source under
   `## Sources` — it records a fold, it does not perform one. So steps 3–5 come first, always.

## B. Prep one inbox proposal

You are assembling the packet Jerry needs to run the gate in one glance — **you do not run
`promote.py` on `_inbox/` content, ever.**

1. Read the proposal in full.
2. Search the atlas for the concept it covers: `MEMORY.md` is the index, and
   `rg` over `atlas/` catches near-misses the index line hides. Read any candidate entry in
   full.
3. Decide what you would recommend and why, against `routing.md`: `create` (genuinely new
   concept, or a study of one named system → case study), `merge` (an existing entry already
   owns this claim), or `reject` (duplicate, thin, or not worth compounding).
4. For a `merge` recommendation, draft the fold — the exact body edit and the
   `- folded from <proposal-slug> (…), <date>.` line — but **do not apply it.** The fold is
   the promoter's act.
5. Write the packet as a comment on the tracking issue or, if there is none, as a kata issue
   titled `vault-inbox: <proposal-slug>`. Include: the proposal path, the recommendation, the
   target entry (for merge), the exact `promote.py` command Jerry would run, the drafted fold,
   and anything ambiguous that should change his mind.

Inbox prep leaves the working tree clean. If it doesn't, you did something outside this scope.

## C. Nothing to do — the expected case

Run `python3 _surface/generate.py --check`, report its one line (`SURFACE CURRENT` /
`SURFACE DRIFTED`) plus "backlog empty, inbox empty", and stop. **Do not go looking for other
work.** Do not create atlas entries, do not tidy, do not reorganize, do not audit. An empty
queue is a healthy vault, not a gap for you to fill.

## Authority ceiling — you may not

- run `promote.py` on anything in `_inbox/`, in any mode — promotion is human-directed and
  Jerry's alone;
- create a new atlas **concept** entry, on the count floor or on judgment — including a
  pattern that has recurred across enough case studies to earn one. The single exception is
  `atlas/case-studies/<slug>.md` for a `subtype: case-study` item already on the backlog
  (branch A step 2), where the decision was made at promotion and the target name is fixed;
- use `--action archive` — deciding material is not worth compounding is Jerry's call;
- use `--by jerry-curated` or `--by jerry-authored`; those assert Jerry read the folded text.
  `jerry-directed` is your ceiling.

## Route ambiguity out, not through

If the target entry is unclear, the source would require a new concept entry, or a
contradiction needs a ruling rather than a note: write what you found, file it, and stop. Do
not guess a home.

`cd ~/vault && kata create "..." --as claude-vault-loop-<random-suffix>` — the default actor
string collides with every other Claude, and kata run from outside `~/vault` resolves to the
wrong project. **kata has no `-C` flag** (`unknown shorthand flag: 'C'`) — cd into the vault,
or pass `--workspace ~/vault`. Label a genuine two-options-need-a-ruling issue
`needs-decision`.

## Verification — artifacts, not assertions

For an ingest (A), before claiming done, show:

- `python3 _system/promote.py --backlog` with the item now absent;
- `git -C ~/vault status --porcelain` showing the atlas entry **and** `_surface/index.html`
  — the surface is tracked and must land in the same commit. A fold into an existing entry
  shows both as modified (` M`); a case-study entry you created shows as untracked (`??`)
  alongside a modified `MEMORY.md` for its new index line. Stage all of them together.

Then `git -C ~/vault commit -s` staging both, with `Assisted-by: Claude:<your model id>` in
the trailer. **Do not push.**

## Report every firing, including empty ones

Which branch you took (A/B/C), the item, the target entry, the receipt path, and the commit's
`%h ("%s")`. If you stopped on a precondition or an ambiguity, say which and what unblocks it.
