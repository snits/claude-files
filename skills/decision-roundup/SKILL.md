---
name: decision-roundup
description: Use when Jerry wants to clear standing decisions across projects, asks "what am I blocking" or "what decisions are waiting on me", or after a stretch of work in one project while others sat idle; reads projstat's cross-project roll-up for needs-decision and needs-review and presents each as a decision-ready brief to rule on in one sitting.
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
offering a round-up when `waiting_on_you` reaches 5 or the oldest passes 14 days. That check is
the reminder mechanism — the same shape as the retro and dream due-checks, and like them there
is no scheduler behind it.

One deliberate difference: the retro and dream checks fire on **elapsed days**, this one fires
on the **live count**. A round-up run against an empty backlog is noise, and a calendar interval
cannot tell the difference.

## Where the numbers come from

The project set and the issue enumeration are read from **projstat's `--json` feed**, not swept
from kata directly — `z64h`'s ruling is that consumers read one aggregated source. The feed's
tracked set comes from `~/.config/projstat/config.toml`.

`--brief` reports `waiting_on_you`: `needs-decision` plus `needs-review`, counted once per item
even when it carries both, with the split shown. `needsinfo` is deliberately off that line — a
triage loop clears it without Jerry, so a persistent count of it would read as his own backlog
(Jerry ruling, 2026-08-16). It stays in the feed, and `--label needsinfo` still reports it here.

**Ages are the one thing not taken from the feed.** The feed's `age_days` counts from
`created_at`; what matters is how long an issue has been *waiting*, which is when the label went
on. The two diverge wildly — fatescroll `kmgh` reads 159 days by filing and 15 by label, so a
batch triaged last week would present as months of neglect. The label-applied age is enriched
from kata's event log for the handful of issues the feed already named; enriching named issues
is not a second sweep. An age printed as `159?d` means no label event was found and the number
is filing age, not waiting age — do not quote it as neglect.

Pushing label-applied age into the feed itself was considered and rejected here: it would break
projstat's verified property that the roll-up needs no new endpoint and is a filter over bytes
already in flight. That belongs in a projstat issue, not this skill.

## Flow

**1. Sweep.**

```bash
python3 ~/.claude/skills/decision-roundup/sweep_decisions.py
```

Prints three sections: **awaiting a ruling** (oldest first), **deferred** (parked, with the
`defer_until` date), and **could not query** (gaps).

Read all three. The deferred section is not backlog — it is the control that stops you
presenting a parked issue as though it were rotting. See the failure below.

Other labels: `--label needs-review|needsinfo`. `retitle` is gone on purpose — it is a
maintenance queue, not a blocked state, and must never gate anything.

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
ignores the exclusion and returns deferred issues as though they were standing. The feed carries
a `deferred` flag per item and this script reports those separately, so the sweep is immune —
but **if you query kata by hand, you will reproduce the bug.**

Age alone is not evidence of neglect. Check for `deferred` before calling anything stale.

## Known scope limits — state them, do not let them read as zeroes

- The sweep covers the projects **projstat tracks** (`include = true` in
  `~/.config/projstat/config.toml`), not every kata-registered project. A project registered in
  kata after the last config edit is invisible here. Re-run the set difference before treating
  a zero as complete; on 2026-08-16 the only kata projects outside the tracked set were
  `kata-probe` and `kata-probe2`, both empty.
  `agentsview`, `forge` and the upstream `kata` checkout are out of scope by ruling (Jerry,
  2026-08-15, on `projstat#hgd6`) — they are not our development projects. Their absence is
  not config drift and needs no fix.
- A project the feed could not ask (`tasks: null` with a binding other than `unbound`) is
  reported under "could not query". Never fold it into the standing count. A project with an
  **empty** `blocked` array was asked and holds nothing — a different fact. A project whose
  binding is `unbound` had nothing to ask; that is correct and permanent, not a gap.

## The gate is the point

Jerry rules on each decision. The skill's job is converting a standing backlog into
decision-ready briefs, not making the calls. An issue that states its options in full is not
missing information — it is missing a ruling, and the ruling is his.
