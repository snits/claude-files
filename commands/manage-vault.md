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
2. Identify the existing atlas entry it belongs to. Read that entry in full first.
3. Fold the source's contribution into the entry's body — integrate the claim, do not restate
   the source — and append its `## Sources` line. `## Sources` is append-only; never rewrite
   an existing entry there.
4. If the source contradicts the current body, follow the contradiction rules in `routing.md`
   (`contradictions:`, both sides dated, `contested:` where the claim itself is disputed).
5. Record it:
   `python3 _system/promote.py --ingest intake/<subtype>/<slug>.md --into atlas/concepts/<slug>.md --by jerry-directed`

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
- create a new atlas entry, on the count floor or on judgment;
- use `--action archive` — deciding material is not worth compounding is Jerry's call;
- use `--by jerry-curated` or `--by jerry-authored`; those assert Jerry read the folded text.
  `jerry-directed` is your ceiling.

## Route ambiguity out, not through

If the target entry is unclear, the source would require a new concept entry, or a
contradiction needs a ruling rather than a note: write what you found, file it, and stop. Do
not guess a home.

`kata -C ~/vault create "..." --as claude-vault-loop-<random-suffix>` — the default actor
string collides with every other Claude, and kata run from outside `~/vault` resolves to the
wrong project. Label a genuine two-options-need-a-ruling issue `needs-decision`.

## Verification — artifacts, not assertions

For an ingest (A), before claiming done, show:

- `python3 _system/promote.py --backlog` with the item now absent;
- `git -C ~/vault status --porcelain` showing the atlas entry **and** `_surface/index.html`
  both modified — the surface is tracked and must land in the same commit.

Then `git -C ~/vault commit -s` staging both, with `Assisted-by: Claude:<your model id>` in
the trailer. **Do not push.**

## Report every firing, including empty ones

Which branch you took (A/B/C), the item, the target entry, the receipt path, and the commit's
`%h ("%s")`. If you stopped on a precondition or an ambiguity, say which and what unblocks it.
