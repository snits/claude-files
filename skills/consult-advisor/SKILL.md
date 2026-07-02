---
name: consult-advisor
description: Use when mid-task and needing stronger judgment — a complex decision, an ambiguous failure, a problem being circled without progress, before an irreversible step, or before declaring done — and the built-in advisor tool is unavailable, disabled, or errors when called.
---

# Consult Advisor

## Overview

Approximates Claude Code's server-side advisor tool with a subagent: a reviewer that sees your full working context and returns a verdict-first course correction. The value is raw-context visibility — the advisor reads what actually happened, not your summary of it.

## Mechanism selection

| Situation | Mechanism |
|---|---|
| A stronger Claude tier exists (sonnet/haiku main → opus) | `Agent` general-purpose with `model` set to the stronger tier + transcript distill (below) |
| Top-tier main AND `subagent_type: "fork"` is registered | Fork — inherits the full conversation automatically, skip the distill |
| Otherwise (fork errors "Agent type 'fork' not found" — common) | `Agent` general-purpose + transcript distill, no model override |

Fork is an opportunistic upgrade, not the default — it is frequently unregistered. The transcript distill path always works.

**Never make a hand-written state summary the advisor's only context.** Your summary filters through the same misconceptions the advisor exists to catch. Fork forwards context automatically; the non-fork path must pass the transcript.

## Transcript distill (non-fork path only)

The session transcript lives at `~/.claude/projects/<slug>/$CLAUDE_CODE_SESSION_ID.jsonl`, where `<slug>` is the cwd with every `/` and `.` replaced by `-` (example: `/home/jsnitsel/devel/orbweaver-rs` → `-home-jsnitsel-devel-orbweaver-rs`). Distill it (per-block truncation is load-bearing — one giant tool dump can otherwise fill the whole tail window):

```bash
jq -r 'select(.type=="user" or .type=="assistant") | (.type|ascii_upcase) + ": " +
  (.message.content | if type=="string" then .[0:1500]
   else ([.[]? | if .type=="text" then .text[0:1500]
     elif .type=="tool_use" then "[tool: "+.name+"]"
     elif .type=="tool_result" then "[result: "+((.content|tostring)[0:200])+"]"
     else empty end] | join("\n")) end) | select(test(": $")|not)' \
  <transcript.jsonl> | tail -c 150000 > <scratchpad>/advisor-state.txt
```

**Sanity-check before dispatch:** `head` the file — it must read as the conversation, not one dump. Tool results are elided by design; the advisor verifies claims against real files instead.

Tell the agent to read that file FIRST, before your question.

## Advisor prompt template

```
**Role:** You are the advisor — a skeptical senior reviewer consulted mid-task.
[Fork: You have the full conversation above.] [Non-fork: Read <scratchpad>/advisor-state.txt first — it is the task transcript.]
Do not redo the work. Do not edit anything. Where a claim looks shaky and a
check is cheap, verify against the actual files/output before opining.

**Assess:** (1) is the current interpretation/approach right, (2) does the
evidence gathered actually support the claims made, (3) what was missed,
mis-verified, or is about to bite.

**Output:** One-line verdict first (proceed / stop / done / course-correct).
Then at most 3-5 prioritized corrections, each anchored to specific artifacts
(file:line, test names, numbers). Explicitly list what should NOT be redone.
No questions back, no option menus. Target 400-700 tokens.
```

Append your specific question (one or two sentences) after the template.

## Expected output shape

Verdict line, then 3-5 bolded anchored corrections, then a don't-redo list. If the response asks you questions or offers option menus, the consultation failed — the prompt lost its Output block.

## Common mistakes

- **Summary-only consultation** — biased input, biased advice. Fork or transcript.
- **Garbage distill** — un-truncated blocks let one schema/log dump dominate the window; always sanity-check the state file before dispatch.
- **Advisor redoes the task** — the "do not redo / read-only verify" lines are load-bearing; keep them.
- **Output bloat** — keep the 400-700 token target in the prompt; a 2,000-word review buries the verdict.
- **Skipping model override on small mains** — a sonnet advising sonnet forfeits the quality lift; set `model: "opus"`.
- **Ignoring the advice you paid for** — if the advisor contradicts your evidence, reconcile explicitly (one follow-up with the conflict stated), don't silently pick.
