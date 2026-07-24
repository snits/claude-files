---
name: retro
description: Use when Jerry asks for a retrospective, a weekly review, a summary of the past week's work, or "what kept getting in our way"; also when /wakey reports a retro is due.
---

# Retro

## Overview

A retrospective built from **evidence, not memory**. Miner agents read the window's raw
session transcripts for friction; the session lead clusters findings into candidates with
typed remedies; Jerry decides each one. The miner proposes, Jerry commits.

Memory-based retros re-report what a journal entry already concluded. The transcripts hold
what actually happened — the corrections, the retries, the abandoned approaches.

## Flow

**1. Window.** Read `~/.claude/retro/last-retro` (ISO date). Absent → 7 days back.

**2. Prefilter (deterministic, do this before dispatching anything).**

```bash
python3 ~/.claude/skills/retro/mine_transcripts.py --days N > /tmp/mine.md
```

Transcripts run to tens of MB per week; this cuts ~300× by keeping only human turns and
failed tool results, each stamped `file:line`. Read the header — it reports session counts,
raw MB, and headless sessions skipped. Those numbers go in the recap.

**3. Mine.** One `general-purpose` subagent on **sonnet** per project in the prefilter
output, highest human-turn count first, **capped at 6**. Give each miner the prefilter
slice for its project (`--project <substring>`) and this instruction:

> Each entry begins with a pointer `/full/path/session.jsonl:LINE`, optionally followed by
> `[TEAMMATE]` (relayed from another agent session — **not** Jerry) or `[TOOL ERROR]`.
> Findings come only from the slice provided. Every finding cites the pointer **exactly as
> it appears at the start of the entry, copied verbatim**, with the quoted text beside it.
> If a pattern is real but you cannot cite a pointer for it, report it under
> `Uncited impressions` — do not promote it to a finding.

Give the miner the pointer format verbatim like that. Tested: miners handed a bare `L648:`
marker cited the *slice file's* own line numbers instead about 40% of the time, because two
coordinate systems were visible at once. A whole-token pointer removes the ambiguity.

Run these in parallel alongside two more miners:
- **journal/`.remember`** — mnemosyne entries and `~/claudes-home/.remember/` in window
- **kata** — closed / deferred / `needs-review` deltas across projects in the window

**4. Synthesize** (session lead, not a subagent). Dedupe across miners and cluster.

**5. Retro conversation.** Accomplishments recap first — short, unembellished. Then walk
candidates **one at a time**, waiting for Jerry on each.

**6. Commit phase.** Apply only what Jerry approved. Write
`~/.claude/scratchpad/retros/YYYY-MM-DD.md`, journal via mnemosyne, then write today's date
to `~/.claude/retro/last-retro`.

## Candidate contract

Every friction candidate has exactly these five parts, in this order:

1. **Pattern** — one sentence, what recurs
2. **Evidence** — one pointer per *instance*, as `path/to/session.jsonl:LINE` with the
   quoted text. Two instances is what makes it a pattern rather than an incident. A single
   vivid instance is not a pattern; keep it, label it as one-off, and let Jerry judge.
   The prefilter emits one line per event, so a second pointer means it happened twice —
   not two citations for the same event.
3. **Cost** — what it actually cost (time, rework, a wrong turn taken)
4. **Remedy type** — exactly one of: `hookify rule` · `skill edit` · `new skill` ·
   `feedback memory` · `kata issue` · `tooling fix`
5. **Draft remedy** — the concrete change, specific enough for Jerry to say yes to

A candidate missing any part is not ready to present. Fix it or drop it to
`Uncited impressions`.

## Verify citations before presenting

Run every miner's output through the checker. It resolves each pointer and confirms the
quoted text is actually at that line:

```bash
python3 ~/.claude/skills/retro/verify_citations.py <miner-output.md>
```

Non-zero exit means something did not check out:

| Status | Meaning |
|---|---|
| `TEXT-MISMATCH` | Quote is not at that line. It reports where the quote *does* live, if anywhere — usually an off-by-N to fix, occasionally an invention to drop. |
| `ABBREVIATED-POINTER` | Written `.../session.jsonl:21`. Not resolvable by a reader; make the miner emit the full path. |
| `NO-SUCH-LINE` / `NO-SUCH-FILE` | Pointer into empty space. |
| `UNVERIFIABLE` | Pointer with no quoted text beside it. Add the quote or drop the finding. |

Fabricated-but-plausible citations are the characteristic failure of mining agents and are
invisible in a clean-looking report. State the checker's summary line in the recap.

## The gate is the point

Jerry approves each candidate before anything is applied. Nothing in step 6 runs early.

**Red flags — stop:**
- "I'll apply this obvious one and show him the rest"
- "He approved a similar remedy last retro"
- "Applying it is the fastest way to demonstrate the candidate"
- Writing a hook, skill, or memory file during steps 2–5

All of these mean: present it as a candidate and wait.

## Report what you did not cover

The recap states per-source status: which projects were mined, which were **dropped by the
cap and why**, and any source that failed or returned nothing ("mnemosyne unavailable",
"kata: no closes in window"). A source that is silently missing reads as a source with
nothing in it.

## Common mistakes

| Mistake | Fix |
|---|---|
| Retro built from journal entries | Journal is one miner of three; transcripts are the primary source |
| "Recurred several times in alexandria" | Cite `file:line` per instance or it is an impression |
| Bundling candidates into one verdict | One at a time — Jerry decides each |
| Silent cap at 6 projects | Name the dropped projects in the recap |
| Grouping project dirs by splitting on `--` | Dotfile and `/tmp` paths contain `--` too (`.claude` → `-claude`). Worktree siblings are `<known-slug>--*`, only identifiable against a known project root |
| Skipping the stamp write | Next retro re-mines the same window |
