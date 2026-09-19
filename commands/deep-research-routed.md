---
description: Deep research with per-stage model routing (Sonnet for search/fetch/verify, session model for scope and synthesis)
argument-hint: <research question> [--max-fetch N] [--max-verify N]
---

Run the `deep-research-routed` named workflow on the question in `$ARGUMENTS`.

The workflow is the built-in deep-research method (scope → search → fetch/extract → 3-vote
adversarial verify → cited synthesis) with `model: "sonnet"` on the search, fetch, and verify
agents. Scope and synthesis inherit the session model. Script: `~/.claude/workflows/deep-research-routed.js`.
Rationale: kata claudes-home#0vv1 — the built-in inherits the session model on every agent, and
from a Fable session that put ~300 bounded search/fetch/verify agents on Fable.

Before invoking:

1. If the question is underspecified (no domain, scope, or use-case), ask 2-3 clarifying
   questions and weave the answers into the question you pass.
2. Parse optional `--max-fetch N` and `--max-verify N` from the arguments. Defaults are 15
   sources and 40 claims (about 145 agents and ~11M Sonnet tokens per question, measured 2026-09-19). Verify is the cost driver: every claim costs 3 Sonnet agents.
   `maxFetch` is a soft cap inherited from the built-in: once its slots are used, only
   medium/low-relevance search results are dropped; high-relevance results always fetch
   (smoke run 2026-09-19: maxFetch 3 still fetched 17). `maxVerifyClaims` is a hard cap.

Invoke exactly like this, passing an object so the caps reach the script as integers:

```
Workflow({
  name: "deep-research-routed",
  args: { question: "<refined question>", maxFetch: <N or omit>, maxVerifyClaims: <N or omit> }
})
```

The workflow runs in the background and returns a task ID. When the completion notification
arrives, write the returned report to `${PROJECT_ROOT}/.scratchpad/research/{YYYYMMDD}-deep-research-{slug}.md`
(findings with confidence and sources, refuted and unverified claims, stats) and give the user
the path plus the executive summary. Note in the report the `stats.agentCalls` count and which
model each stage ran on.

If the run stops early, do not resume expecting an incremental run: kata 0vv1 found that
`resumeFromRunId` replays only scope and search; fetch and verify re-run in full.
