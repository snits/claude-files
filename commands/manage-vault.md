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

   Then read what is already known about it: `cd ~/vault && kata search "<slug>"` for any open
   issue referencing this item. Corrections, rulings, and cross-item findings collect on those
   issues — branch B *writes* them and, until now, nothing ever *read* them, so a defect
   recorded weeks ago is invisible to you unless you go and look. Apply what you find, and name
   the issue in your report. If an issue says the item is blocked on a ruling that has not
   landed, stop and say so rather than authoring around it.
2. Find its atlas home. **Prefer an existing entry; create one when none exists.**

   Look for the existing atlas entry the source belongs to — `MEMORY.md` is the index, and
   `rg` over `atlas/` catches the near-misses an index line hides — and read any candidate in
   full before deciding it is not the home. Folding into an entry that already owns the claim
   is always better than a second entry beside it.

   **If no entry owns it, create one.** RULING (Jerry, 2026-08-12): the create carve-out is
   valid for anything already in `intake/`, whatever its `subtype:`. Promotion is where the
   judgment was made — Jerry decided this material was worth compounding when he promoted it,
   and the ceiling exists to protect *that* judgment, not to re-litigate it one hop later. A
   loop that cannot author the target cannot drain the backlog at all, which is how
   `atlas/tools/graphify.md` sat blocked (kata#g2z9) after case studies got the same carve-out
   too narrowly (kata#kvwm).

   Pick the directory from what the material is, per `routing.md`: `atlas/case-studies/` for a
   study of one named system, `atlas/tools/` for a keep/switch verdict on a tool, otherwise
   `atlas/concepts/`. The slug matches the source for a case study (one entry per subject
   studied); elsewhere it names the thing the entry is about, which need not equal the source
   slug — `kg-tools-for-notes-corpus` became `graphify`.

   Read the siblings in whichever directory you land in before writing. For case studies this
   is load-bearing rather than courtesy: the series is cumulative and a study's recurrence
   claims are checked against its siblings.
3. Fold the source's contribution into the entry's body — integrate the claim, do not restate
   the source — and append its `## Sources` line. `## Sources` is append-only; never rewrite
   an existing entry there.

   For an entry you are creating, this is a synthesis, not a copy: the intake file is the raw
   research or essay, the atlas entry is the curated one. Frontmatter takes the matching
   contract in `_system/schemas.md` — **Atlas case study** (`type: case-study`, plus
   `subject:` naming the system studied), **Atlas tool** (`type: tool`, plus `verdict:` from
   the adopt/adapt/reference-only/reject/evaluating vocabulary), or **Atlas concept**
   (`type: concept`). In all three, `provenance: inbox-promoted` (`routing.md:16` — authoring
   under Jerry's direction does not confer a `jerry-*` provenance).

   Carry the source's stated weaknesses into the body rather than filing them off — derived
   figures labelled as derived, caught confabulations, flags never confirmed against `--help`.
   They are what sets `confidence:`, and an entry that reads as settled fact when its source
   did not is the failure mode here.
4. If the source contradicts the current body, follow the contradiction rules in `routing.md`
   (`contradictions:`, both sides dated, `contested:` where the claim itself is disputed).
5. Add the `MEMORY.md` index line by hand: `- [slug](atlas/.../slug.md) — description`.
   **`--ingest` does not write it** — `_append_memory_line` runs only on the promotion path
   (`promote.py:279`), so nothing enforces `routing.md`'s one-index-line-per-atlas-file rule
   on this hop. Skip only if the entry already existed and already has its line.
6. Record it:
   `python3 _system/promote.py --ingest intake/<subtype>/<slug>.md --into atlas/<concepts|tools|case-studies>/<slug>.md --by jerry-directed`

   The gate accepts all three atlas directories (`promote.py:77-82`) and matches the citation
   on the *source's* slug, so a target named differently from its source is fine.

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
- create an atlas entry for anything **not already in `intake/`** — in particular, a concept
  entry earned on the count floor or on judgment, such as a pattern that has recurred across
  enough case studies to graduate. That decision is Jerry's and has no promotion behind it.
  Creating the home for a backlog item is *not* covered by this: see branch A step 2, where
  the 2026-08-12 ruling puts every `intake/` subtype inside your authority;
- use `--action archive` — deciding material is not worth compounding is Jerry's call;
- use `--by jerry-curated` or `--by jerry-authored`; those assert Jerry read the folded text.
  `jerry-directed` is your ceiling.

## Route ambiguity out, not through

If a contradiction needs a ruling rather than a note, two existing entries both plausibly own
the claim, or the source turns out to be about something other than what its promotion assumed:
write what you found, file it, and stop.

"No entry exists yet" is **not** ambiguity — that is the ordinary case for a first-of-its-kind
source, and branch A step 2 tells you to create the home. Route out when the *judgment* is
genuinely unmade, not when the work is merely new.

`cd ~/vault && kata create "..." --as claude-vault-loop-<random-suffix>` — the default actor
string collides with every other Claude, and kata run from outside `~/vault` resolves to the
wrong project. **kata has no `-C` flag** (`unknown shorthand flag: 'C'`) — cd into the vault,
or pass `--workspace ~/vault`. Label a genuine two-options-need-a-ruling issue
`needs-decision`.

## Verification — artifacts, not assertions

For an ingest (A), before claiming done, show:

- `python3 _system/promote.py --backlog` with the item now absent;
- `git -C ~/vault status --porcelain` showing the atlas entry **and** `_surface/index.html`
  — the surface is tracked and must land in the same commit. Expect four or five paths: the
  atlas entry (` M` for a fold into an existing one, `??` for one you created), the source
  under `intake/` now reading `status: integrated`, the new `_ops/applied/` receipt (`??`),
  `_surface/index.html`, and `MEMORY.md` when you added an index line. Stage all of them
  together — the receipt is easy to leave behind, and a commit without it loses the audit
  trail for the fold it records.

Then `git -C ~/vault commit -s` staging all of them, with `Assisted-by: Claude:<your model id>`
in the trailer. **Do not push.**

**In a background session the isolation guard refuses edits to the shared checkout.** Call
`EnterWorktree` before the first Write, do the whole ingest inside the worktree (the gate and
`kata` both resolve correctly there — `.kata.toml` is committed), commit, rebase onto `main`
from inside it, then `ExitWorktree --action keep` and `git merge --ff-only` from `~/vault`.
The superpowers hook drops a `.superpowers` symlink into the worktree that blocks
`git worktree remove`; delete the *symlink* only, never its target.

## Report every firing, including empty ones

Which branch you took (A/B/C), the item, the target entry, the receipt path, and the commit's
`%h ("%s")`. If you stopped on a precondition or an ambiguity, say which and what unblocks it.
