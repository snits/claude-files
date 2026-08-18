---
name: architecture-case-study
description: Use when studying the architecture of an open-source codebase for the case-study series — "case study", "architecture study", "study how X is built", adding a subject under ~/devel/case-studies. Not for reviewing our own projects' code.
---

# Architecture Case Study

Study a real codebase the way architects study buildings. Output is one essay serving
two readers: **Jerry building a pattern vocabulary** for design discussions (names,
pictures, anchors), and the **vault's recall machinery** (density, wikilinks). The
series is cumulative — patterns graduate by recurring across studies.

Reference exemplar: `~/vault/atlas/case-studies/brew-architecture-case-study.md` — read it for
essay structure, depth, and section shape. It is the **promoted atlas entry**, so its
frontmatter is *not* the model for what you write; the stub you hand off takes a different
contract (Phase 6).

## Ground rules

- The subject repo is **read-only**. No edits, no kata binding, no handoff files in it.
  Session handoffs go to claudes-home.
- Every factual claim in recon reports and essay is file:line-cited at the pinned commit.
- A study that only flatters its subject is not evidence — the weaknesses section is
  mandatory.

## Phase 1 — Setup

1. Subject lives at `~/devel/case-studies/<name>`; clone it there if absent.
2. Pin the commit: `git -C ~/devel/case-studies/<name> show -s --format='%h ("%s")'`.
3. Write one paragraph: *why this subject earns a study* — the hard question its
   architecture is a sustained answer to. Confirm with Jerry before dispatching recon
   (fine to present this and the Phase 2 lens list together in one message).

## Phase 2 — Lens selection

Survey the tree top-level, build docs, and any architecture docs yourself (cheap reads
only). Propose **5–8 recon lenses** — subsystems or cross-cutting axes, sized so one
agent can cover one lens well. Re-derive lenses from the live tree; never reuse a stale
list from a plan or an earlier conversation. Get Jerry's sign-off.

## Phase 3 — Recon fan-out

Dispatch one read-only `general-purpose` agent per lens, all in a single message.
Model: **sonnet** by default; **opus** for lenses that are algorithmically deep or
judgment-dense. Each brief must contain:

- **Role:** architecture recon on <subject> for a case-study series.
- **Target framing:** an AOSA-style essay; we need the architectural shape, key
  mechanisms, and deliberate trade-offs — not exhaustive API inventory.
- **Audience framing:** a developer with no prior exposure to this codebase; translate
  jargon, surface intuitions.
- The pinned commit citation; instruction to cite every claim as `file:line`.
- Read-only mandate: no edits anywhere in the subject repo.
- Output path: `~/.claude/scratchpad/YYYYMMDD-<subject>-general-purpose-recon-<lens>.md`
- Report shape: system role of the lens; how it works (mechanism, not tour); design
  decisions and their apparent rationale; warts, hacks, and suspicious spots; 3–5
  candidate patterns or anti-patterns with evidence.
- Gap flagging: if a finding's evidence lives in another lens's files, state the gap
  explicitly in the report rather than stretching — the synthesizer follows up.

Before synthesis, read each report file and confirm it is substantive — an agent's
"done" is not evidence.

## Phase 4 — Synthesis (session model)

1. Read **all recon reports** and **every prior study** — at minimum their pattern-candidate
   lists. Prior studies live in **two** places and you must read both:
   - `~/vault/atlas/case-studies/` — studies that have completed the ingest loop.
   - `~/vault/intake/case-study/` — studies still in flight, promoted but not yet folded into
     the atlas. A study can sit here for a long time, so this directory is not an edge case.

   Reading only the atlas directory is how a recurrence check silently misses a sibling
   study: on 2026-08-11 the git study missed rsync entirely because rsync was in `intake/`
   and `atlas/case-studies/` held only brew.
2. Write the essay with these sections:
   - **Header paragraph:** series positioning, pinned commit, why this subject. **Do not
     number the entry** ("Second entry in the series…"). Studies are often researched in
     parallel and cannot know their own ordinal; the number carries nothing the series
     order does not already say, and two studies claiming the same one is a coordination
     problem with no upside. Name the subject and, where it helps, the prior studies whose
     patterns recur here.
   - **System shape:** one dense prose paragraph plus the required mermaid diagram
     (Phase 5).
   - **Cross-cutting themes:** shapes visible only across reports, not to any single
     recon pass. Each theme gets a **graspable name** and a **"reach for this when…"**
     line — the handle for a design conversation — then the evidence-backed description.
   - **Where this could bite or help us:** 1–2 sentences per applicable theme anchoring
     it to our own projects.
   - **Where the architecture is weakest** (mandatory).
   - **Style-catalog check** (one short paragraph): name the subject's implicit driving
     characteristic — the one nobody wrote down — and what was deliberately spent for it;
     then name the nearest mainstream architecture style and the "but" clause it needs, or
     state that no catalog entry fits. `atlas/concepts/style-catalogs-measure-distribution.md`
     makes a falsifiable prediction that the "but" clause goes empty on distributed subjects
     (kubernetes, containerd) — this paragraph is how that prediction gets tested, so report
     the result plainly whichever way it lands, including when it refutes the concept.
   - **Pattern candidates:** new candidates as unresolved `[[wikilinks]]` with one-line
     definitions, each carrying a **buys / spends** clause — which architecture
     characteristic the mechanism purchases and which one pays for it (adoptability bought
     with security-by-default; common-case latency bought with mirrored logic). Without it a
     candidate is a named mechanism; with it, it is a decision aid, which is the whole point
     of the vocabulary. Derive the trade from the subject's own evidence, not from a generic
     -ilities list. Required from 2026-08-18 forward; the first five studies do not carry it
     natively and are not being backfilled — the cross-study trades live in
     `atlas/concepts/style-catalogs-measure-distribution.md` instead.
     **Recurrence check:** if a prior study's candidate appears in this
     subject, cite its existing wikilink and say so explicitly, and state the running
     count — `routing.md`'s earn-an-entry floor of **3+ citations** is what graduates a
     candidate into a concept entry (writing the entry is a promoter's act, not this
     session's). Do not write "graduates on a second sighting": that wording came from
     this skill, contradicted `routing.md:29`, and propagated into three curated studies
     before Jerry ruled the 3+ floor standing (2026-08-15, kata vault#5btt). Judgment
     (routing clause b) may still fire earlier, but that is a promoter's call stated as
     one — never the default the study asserts.
   - **Sources:** method, recon report paths, working tree path, sha256 of the recon
     reports concatenated in **sorted filename order** (`cat <dir>/<glob>*.md | sha256sum`
     — glob order is sorted, so this is reproducible; repo state is pinned by the
     commit citation).

## Phase 5 — Diagrams

Mermaid, inline in the essay:

- **Required:** one system-shape diagram — components/processes and who talks to whom.
- **Strongly encouraged:** one sequence/flow diagram of the subject's *defining
  mechanism* (the thing the subject is famous for).
- Per-theme diagrams only where a picture beats a paragraph. No quota.
- Keep diagrams renderer-portable: plain `flowchart`/`sequenceDiagram`, no exotic
  features; node labels carry file names where that helps navigation.

## Phase 6 — Hand off to the vault + wrap-up

1. Write the essay to `~/vault/_inbox/session-lead/<subject>-architecture-case-study.md`.

   **Never write to `~/vault/intake/`** — despite the name, that is the vault's
   *post-promotion* home for source material, and agents may not write there
   (`_system/routing.md`). The agent's only write target is `_inbox/{agent-id}/`, and the
   directory name must match the `agent_id` field.

   **Frontmatter is the intake-stub contract** in `_system/schemas.md` ("Intake item") —
   *not* the frontmatter of the brew exemplar at line 13. That exemplar is the promoted
   **atlas** entry; its field set and its `provenance`/`status` vocabularies are different,
   and copying it produces a stub the gate rejects. Use exactly:

   ```yaml
   ---
   name: <subject>-architecture-case-study   # matches filename stem
   type: intake                              # literal — NOT `case-study`
   subtype: case-study                       # literal
   description: <~150 chars>
   provenance: agent-proposed                # literal — the gate confers trust, you cannot
   source_url: <github tree URL at the pinned commit>
   agent_id: session-lead                    # matches the _inbox/ subdirectory
   ingested: YYYY-MM-DD
   sha256: <recon reports concatenated, sorted filename order>
   status: pending-promotion                 # literal
   ---
   ```

   Do **not** add `subject`, `created`, `updated`, `confidence`, `contested`,
   `contradictions`, or `tags` — those are atlas fields, written later when the atlas entry
   is authored. There is no `commit` field in any schema; the pinned commit citation lives
   in the body's header paragraph and in `source_url`.

2. Promotion is Jerry's gate — do not promote, and do not run `promote.py` in any mode.
   Tell him the study is ready and note that it takes **two hops** (per the brew receipts in
   `~/vault/_ops/applied/`), because the essay is not on the reading surface until the
   second one runs:

   ```
   python3 _system/promote.py _inbox/session-lead/<slug>.md \
     --to intake/case-study/<slug>.md --action create --by jerry-curated

   python3 _system/promote.py --ingest intake/case-study/<slug>.md \
     --into atlas/case-studies/<slug>.md --by jerry-directed
   ```

   Hop 1 sets `status: promoted`, which is what makes the study visible to
   `promote.py --backlog`. Hop 2 authors the `atlas/case-studies/` entry — that hop creates a
   new atlas entry, so the autonomous `/manage-vault` loop cannot do it; it needs a directed
   session. Promoting the stub straight to `atlas/case-studies/` fails validation: that
   target expects `type: case-study`, and the stub is `type: intake`.
3. Journal entry (mnemosyne): what the study surfaced, what the method missed.
4. Session handoff in claudes-home if the session is ending.

## Common mistakes

| Mistake | Correction |
|---|---|
| Handoff or notes written into the subject repo | Subject is read-only; handoffs live in claudes-home |
| Lens list reused from a plan or prior chat | Re-derive from the live tree at Phase 2 |
| Synthesis without reading prior studies | Recurrence counting is the series' point — read them |
| Prior studies read only from `atlas/case-studies/` | In-flight studies sit in `intake/case-study/`; read both or the recurrence check misses siblings |
| Numbering the entry ("Second entry…") | Parallel studies can't know their ordinal — don't number them |
| Essay that only admires the subject | Weaknesses section is mandatory |
| Trusting recon agents' "done" | Read each report file before synthesis |
| Essay written into `~/vault/intake/` | That is the post-promotion home; agents write only to `_inbox/{agent-id}/` |
| Essay at bare `~/vault/_inbox/<slug>.md` | The `{agent-id}` subdirectory is required and must match the `agent_id` field |
| Stub frontmatter copied from the brew exemplar | The exemplar is the promoted *atlas* entry; a stub takes the intake contract in `schemas.md` |
| `type: case-study` on the stub | `type: intake` + `subtype: case-study`; `case-study` is the atlas type |
| Invented `provenance`/`status` values | Literals only: `provenance: agent-proposed`, `status: pending-promotion` |
| Running `promote.py` yourself | Promotion is Jerry's gate, in every mode |
| Telling Jerry one promotion finishes it | Two hops; the study is not on the reading surface until the ingest hop |
