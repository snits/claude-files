---
name: decision-roundup
description: Use when Jerry wants to clear standing decisions across projects, asks "what am I blocking" or "what decisions are waiting on me", or after a stretch of work in one project while others sat idle; sweeps every kata project for needs-decision and presents each as a decision-ready brief to rule on in one sitting.
---

# Decision round-up

The counterpart to `/retro`. Same gate structure, different source: `/retro` mines transcripts
for friction, this mines **kata for rulings Jerry owes**.

## Why this exists

`/wakey` surfaces `needs-decision` **per project**. An issue in a project Jerry has not opened
lately is therefore invisible indefinitely — not deprioritized, just never shown. A cross-project
sweep is the only thing that finds them. On 2026-08-15 that sweep found 15 standing decisions
across 5 projects, including a five-issue pcitopo cluster that had stalled the entire project
(zero closes in the window).

The startup check reporting "0 needs-decision" is true for the current project and misleading
about everything else.

**`/wakey` surfaces this at session start**, by running `sweep_decisions.py --brief` and
offering a round-up when 5+ decisions are standing or the oldest passes 14 days. That check is
the reminder mechanism — the same shape as the retro and dream due-checks, and like them there
is no scheduler behind it.

One deliberate difference: the retro and dream checks fire on **elapsed days**, this one fires
on the **live standing count**. A round-up run against an empty backlog is noise, and a calendar
interval cannot tell the difference. `z64h` part 1 (the projstat roll-up) would let `/wakey`
read one aggregated source instead of shelling out here; until then this script is the source.

## Flow

**1. Sweep.**

```bash
python3 ~/.claude/skills/decision-roundup/sweep_decisions.py
```

Prints three sections: **awaiting a ruling** (oldest first), **deferred** (parked, with the
`defer_until` date), and **could not query** (gaps).

Read all three. The deferred section is not backlog — it is the control that stops you
presenting a parked issue as though it were rotting. See the failure below.

Other labels: `--label needs-review|needsinfo|retitle`.

**2. Prepare briefs.** For each standing decision, dispatch a `general-purpose` subagent on
**sonnet**, one per issue, capped at 6 per round, oldest first. Each reads the issue and its
comments and returns a brief with:

- **The decision, in one sentence** — what changes depending on the answer
- **Options**, each argued to a conclusion, not merely listed
- **A recommendation**, with the reason
- **What it blocks** — who is waiting, what stalls while it stands
- **Whether it is actually a decision** (see triage below)

Instruct them to send **one brief per message**; long message bodies are dropped by the relay.

**3. Present one at a time.** Jerry rules on each before you move to the next. Never bundle.

**4. Record each ruling immediately**, before presenting the next one:

```bash
kata comment <ref> --as jerry-via-claude \
  --body "RULING (Jerry, <date> decision round-up): chose <option> because <reason>."
kata label rm <ref> needs-decision
```

Comment **then** remove the label — a cleared label with no recorded rationale reads as
resolved and isn't. Never `--as jerry`; that asserts he typed it.

**5. Stamp the run.**

```bash
mkdir -p ~/.claude/decisions && date -I > ~/.claude/decisions/last-roundup
```

Same convention as `~/.claude/retro/last-retro` and `~/.claude/dream/last-pass`. `/wakey`
reports it via `sweep_decisions.py --brief`; skipping the write makes the next startup say
`last=never` forever.

## Triage — three things wear the same label

The brief must say which one it is, because two of them cannot be cleared by a ruling:

| Shape | Tell | What clears it |
|---|---|---|
| **A ruling** | Options stated and argued; nothing missing but a choice | Jerry, in one line |
| **A missing fact** | An answer exists and someone could go get it | `needsinfo` work, then a ruling |
| **A session** | The material needs walking through together before it can be judged | Scheduling, not a comment |

The third is the one that gets misfiled. alexandria `qxq2` sat labelled `needs-decision` while
what it actually needed was a working session where its ~441 scoring rows get explained — "the
instructions are not very human friendly." Presenting it as a ruling would have produced either
a guess or another deferral. If a brief cannot state the options crisply enough for Jerry to
choose from the brief alone, that is the signal it is a session, not a decision.

## The deferred trap — verified failure, do not repeat

**A deferred issue is not a standing decision.** It is parked with a date and nothing is
waiting on it.

On 2026-08-15 a retro miner reported alexandria `f16t` as the headline finding — "114 days old,
no ruling." The recommendation drawn from it was to close it `wontfix` as decided-by-default.
Wrong on both counts: `f16t` carries `deferred` with `defer_until 2026-10-02`, and a session on
2026-08-05 had *deliberately* left it standing with written reasoning — ruling now would fix a
calibration strategy against the very corpus the issue says cannot discriminate.

The mechanism that produced the error is a kata gotcha worth knowing: **only the first
`--label`/`--no-label` flag applies**, so `--label needs-decision --no-label deferred` silently
ignores the exclusion and returns deferred issues as though they were standing. The sweep script
filters client-side for exactly this reason. If you query kata by hand, you will reproduce the
bug.

Age alone is not evidence of neglect. Check for `deferred` before calling anything stale.

## Known scope limits — state them, do not let them read as zeroes

- The sweep covers **registered** kata projects (`kata projects list`). Directories holding a
  `.kata.toml` that were never registered — as of 2026-08-15: `agentsview`, `forge`, and the
  upstream `kata` checkout — are never queried and never appear. That is config drift; fix or
  exclude it deliberately.
- A project that errors is reported under "could not query". Never fold it into the standing
  count.

## The gate is the point

Jerry rules on each decision. The skill's job is converting a standing backlog into
decision-ready briefs, not making the calls. An issue that states its options in full is not
missing information — it is missing a ruling, and the ruling is his.
