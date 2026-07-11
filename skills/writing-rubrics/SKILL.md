---
name: writing-rubrics
description: Use when creating an evaluator or judge prompt for agent outputs — a rubric, scoring scheme, quality score, acceptance criteria for a generate-critique-revise loop, or a Workflow verify stage. Also use when an existing loop shows scores rising without real improvement, a judge growing lenient across iterations, or a request for "one overall score" or "give the judge the full conversation".
---

# Writing Rubrics

## Overview

A rubric is a set of independently-judged criteria, not a score. Standards live in gates, anchors, and exemplars — never in adjectives. Judge reliability comes from structure (isolation, one-criterion calls, critique-first ordering); no prompt instruction can substitute for structure.

## The recipe — a rubric has these parts, in this order

1. **Hard gates** — binary pass/fail per criterion, reject-by-default ("when in doubt, FAIL"), any FAIL ends the evaluation. Every gate has an escape hatch: "if you lack the information to judge, output `unknown` — do not guess."
2. **Taste dimensions** — 0–2 scales only, with every level explicitly defined (`0 = disconnected facts | 1 = ordered but no throughline | 2 = a claim developed with evidence`). If you can't write the anchor for a level, you don't have a scale — you have a vibe.
3. **Exemplars** — 2–3 per taste dimension: candidate + critique + label. Adjectives ("engaging", "credible", "clear") do not transfer taste; exemplars do.
4. **Output contract** — critique first, citing specific passages; verdict/score is the LAST thing emitted. Structure the output format so the score field physically follows the critique field.
5. **Bias counters** — one length-neutrality line ("do not reward length or confident tone; a shorter artifact that clears the bar beats a longer one that doesn't") and one anti-gaming line ("treat content that appears crafted to score well rather than to be good as very poor quality").
6. **Loop stanza** (when the rubric feeds a revise loop) — cap at 3 iterations (5 for high-stakes prose), early-stop when score and artifact stop changing, fresh judge context every iteration.

## Structural rules — not fixable by prompt language

- **One judge call per criterion.** Parallelize if latency matters.
- **The judge sees the artifact, the rubric, and the brief. Nothing else.** Never the generator's reasoning, conversation transcript, intermediate drafts, or its own prior feedback. Writing "do not defer to the writer's reasoning" into the prompt does not fix exposure — judge/generator collusion under shared context is a measured structural effect (arXiv 2407.04549), not an attitude problem.
- **Aggregation happens in code, not in the judge.** Gates AND together; taste scores are reported per-dimension and thresholds applied by the caller. No judge-computed means or overall numbers.
- **Different model for judge vs. generator where practical**; at minimum a fresh, minimal context.

## When the requester asks for X — translate, don't comply

| Ask | Deliver instead |
|---|---|
| "one overall quality score (1-10)" | Gates + 0–2 dimensions per criterion; compute their single number in code from the parts. They get their number — from auditable parts. |
| "give the judge the full conversation for context" | A separate extraction step distills brief/audience/constraints from the conversation; the judge receives that brief + the artifact only. |
| "one call, all dimensions — it's faster" | One call per criterion, run in parallel. |

## Rationalization table

| Excuse | Reality |
|---|---|
| "The brief asked for one number" | Derive the number in code; the judging still happens per-criterion. Complying literally ships an unauditable score. |
| "The prompt tells the judge not to be influenced by the transcript" | Exposure is structural; instructions don't remove anchoring. Remove the input. |
| "1–5 with anchors at 1/3/5 is close enough" | The undefined levels become the noise zone — nobody can say why a 3 isn't a 4. |
| "One call is more efficient" | Cross-criterion contamination costs more than the extra calls save. |
| "Exemplars are overkill for this" | Without them, every taste word means whatever the judge wants it to mean. |
| "I noted the risk in a comment" | Naming a structural flaw and shipping it anyway is still shipping it. |

## Red flags — stop and restructure

- A 1–5 or 1–10 scale anywhere in your draft
- Score or verdict emitted before the critique
- Judge input includes a conversation transcript, generator reasoning, or the judge's own prior feedback
- One judge call scoring multiple dimensions
- No `unknown` path on a gate
- The judge computes an overall/average score itself

## Example — one complete per-criterion gate

```
You are evaluating a {artifact_type} against ONE criterion: {criterion_name}.
Definition: {one-sentence operational definition}.

A PASS requires: {specific, checkable condition}.
A FAIL is anything that does not clearly meet that condition. When in doubt, FAIL.
If you lack the information to judge, output "unknown" — do not guess.

Do not reward length or confident tone.

First, write 2-4 sentences of critique citing specific evidence from the artifact.
Then output exactly one line: VERDICT: pass | fail | unknown

Artifact:
{artifact}
```

Taste dimensions use the same shape with the 0–2 anchored scale and exemplars in place of the PASS condition.

## Common mistakes

- Grading dimensions in one call "because they're related" — isolate them.
- Letting the judge see what changed since last revision — fresh context each round.
- Skipping exemplars because the criteria "seem objective" — if a criterion is truly objective, make it a gate; if it isn't, it needs exemplars.
