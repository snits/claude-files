---
name: architecture-case-study
description: Use when studying the architecture of an open-source codebase for the case-study series — "case study", "architecture study", "study how X is built", adding a subject under ~/devel/case-studies. Not for reviewing our own projects' code.
---

# Architecture Case Study

Study a real codebase the way architects study buildings. Output is one essay serving
two readers: **Jerry building a pattern vocabulary** for design discussions (names,
pictures, anchors), and the **vault's recall machinery** (density, wikilinks). The
series is cumulative — patterns graduate by recurring across studies.

Reference exemplar: `~/vault/atlas/case-studies/brew-architecture-case-study.md`.

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

1. Read **all recon reports** and **every prior study** in `~/vault/atlas/case-studies/`
   (at minimum their pattern-candidate lists).
2. Write the essay with these sections:
   - **Header paragraph:** series positioning, pinned commit, why this subject.
   - **System shape:** one dense prose paragraph plus the required mermaid diagram
     (Phase 5).
   - **Cross-cutting themes:** shapes visible only across reports, not to any single
     recon pass. Each theme gets a **graspable name** and a **"reach for this when…"**
     line — the handle for a design conversation — then the evidence-backed description.
   - **Where this could bite or help us:** 1–2 sentences per applicable theme anchoring
     it to our own projects.
   - **Where the architecture is weakest** (mandatory).
   - **Pattern candidates:** new candidates as unresolved `[[wikilinks]]` with one-line
     definitions. **Recurrence check:** if a prior study's candidate appears in this
     subject, cite its existing wikilink and say so explicitly — two citations is what
     graduates a candidate toward a concept entry (writing the concept entry is the
     vault ingest loop's job, not this session's).
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

## Phase 6 — Vault intake + wrap-up

1. Write the essay to `~/vault/intake/case-study/<subject>-architecture-case-study.md`
   with frontmatter matching the brew exemplar (`type: case-study`, subject, commit,
   tags, sha256 as above). Promotion is Jerry's gate — do not promote.
2. Journal entry (mnemosyne): what the study surfaced, what the method missed.
3. Session handoff in claudes-home if the session is ending.

## Common mistakes

| Mistake | Correction |
|---|---|
| Handoff or notes written into the subject repo | Subject is read-only; handoffs live in claudes-home |
| Lens list reused from a plan or prior chat | Re-derive from the live tree at Phase 2 |
| Synthesis without reading prior studies | Recurrence counting is the series' point — read them |
| Essay that only admires the subject | Weaknesses section is mandatory |
| Trusting recon agents' "done" | Read each report file before synthesis |
| Promoting the vault item | Intake only; promotion is Jerry's gate |
