---
name: consulting-agents
description: Use when you need information you don't have, expertise outside your comfort zone, or a single fresh perspective on code — even if you think you already know the answer. Also triggered by "I'm not sure about", "what's the best approach", "second opinion", "research how X works", or any need for discovery, expertise, or review. For multi-perspective reviews where agents discuss and converge, use design-meeting instead. NOT for implementation delegation (see subagent-driven-development).
---

# Consulting Agents

## The Trigger

**Use this skill when you think:**
- "I need to find something in this codebase"
- "I'm not sure about the best approach here"
- "I want a second opinion on this code/design"
- "I need to research how X works"

**Ask yourself:** "Do I need information, expertise, or a fresh perspective?" If yes → consult an agent.

**NOT for:**
- Implementation work → `subagent-driven-development`
- Multi-perspective review where agents need to discuss and converge → `design-meeting`

## Core Principle

Agents provide **fresh context** for focused tasks. You own the through-line understanding. Agents research, advise, and review.

**No blocking authority.** Agents provide input, you decide.

## Choosing the Agent

Check the current Agent tool registry first — it varies by project. Common general-purpose types:

| Need | Agent Type | Example |
|------|-----------|---------|
| Broad fan-out search, locate code | `Explore` | "Find every consumer of the ActionQueue" |
| Implementation planning | `Plan` | "Plan the migration to the new schema" |
| Correctness review of changes | `code-reviewer` | "Review this diff for bugs" |
| Research external docs | `web-search-researcher` | "Best practices for JWT refresh tokens" |
| Anything else | `general-purpose` + role line | "Review this retry logic for failure modes" |
| Domain judgment | project persona, or ad-hoc persona | invariant-analyst, premise-auditor, ... |

**Personas are the right tool for domain judgment — when they're built right.**
The failure mode research warned about (identity prompt → overconfidence →
skipped tool use) comes from *naked identity*: "You are an expert" sitting on
a thin capability list. A persona earns its dispatch when identity sits on a
**capability foundation**: a domain reasoning chain, opinionated principles,
and a verification mandate (cite file:line, compute the numbers, attack the
claim). See `writing-personas` and the `agent-personality` plugin for
construction; foundation-first is what prevents the overconfidence trap, not
identity avoidance.

**Ad-hoc personas** (generated for one dispatch, no file) follow the same
rule, compressed: one identity line, 3-5 domain-specific reasoning steps, a
review posture, an explicit verification mandate. If you can't write the
reasoning steps, you wanted `general-purpose` with a role line.

**Pair complementary lenses for reviews that matter.** Two reviewers with
different orientations (e.g., an invariant tracer and a premise auditor) on
the same artifact produce mostly disjoint findings — each catches a failure
class the other's lens misses — and their overlap is high-confidence
confirmation. One reviewer, however strong, has one bias. `team-composition`
(agent-personality plugin) analyzes orientation balance across a roster.

## Dispatch Mechanics

**Every consultation prompt needs target and audience framing** (see global
CLAUDE.md): what is being built and at what fidelity; who consumes the output
and what jargon they tolerate. Without these, agents answer at the
sophistication of their sources, not your need.

**Follow-ups are cheap — use them.** A completed agent can be continued via
`SendMessage` with its context intact. Prefer continuing a warm agent over
re-briefing a fresh one for follow-up questions, applying review findings, or
reconciling its claims against new evidence. (This replaces the old practice
of pre-negotiating context with an agent before dispatch — current models go
find missing context themselves; brief well and iterate after.)

## Parallel Discovery

**Discovery can run in parallel easily** — no commit coordination needed.

Dispatch multiple agents in a SINGLE message when tasks are orthogonal:

```
[In one message, dispatch:]
- Explore: "find authentication entry points"
- Explore: "find session management"
- general-purpose: "review auth architecture for security concerns"

→ All run concurrently
→ You synthesize results
```

**When to parallelize discovery:**
- Multiple searches needed
- Different review perspectives on same code (security, performance, UX)
- Research from multiple sources
- Any orthogonal read-only operations

**Synthesis required:** You (or a coordinating agent) must synthesize parallel
results. Parallel agents catch task-specific issues but miss integration
concerns.

## Synthesis Layer

**Problem:** Parallel agents miss how pieces connect.

**Options:**
1. **You synthesize** (default for 2-4 agents)
2. **Coordinating agent** reviews all results (for 5+ agents)
3. **Two-phase:** Parallel task reviews, then integration review

**Decide who synthesizes before parallelizing.**

## Report Format

### Scratchpad Directory (Fallback Chain)

Agents write reports to a **project scratchpad** by default, with a fallback chain:

1. **Project scratchpad** (`${PROJECT_ROOT}/.scratchpad/`) — preferred location
   - If the directory does not exist, create it
2. **Global scratchpad** (`~/.scratchpad/`) — fallback if project scratchpad fails
3. **Project root** (`${PROJECT_ROOT}/`) — last resort if both scratchpads fail
   - **Inform the user** so they can move the report to its proper place
4. If all writes fail, **inform the user** that the report could not be saved

### File Naming

```
{timestamp}-{project-slug}-{agent-type}-{task-slug}.md
```

**Report structure:**
```markdown
# Task: [What you asked]

## Executive Summary
[2-3 sentences: findings + recommendation]

## Findings
[Detailed analysis with evidence]

## Recommendations
[Specific actionable suggestions]

## References
[Files examined, sources consulted]
```

**Objectivity required:** Focus on technical facts, not quality judgments. Avoid superlatives.

## Routing Source Material to the Vault

Some consultations yield **source material worth keeping** — an article, paper, YouTube
transcript, podcast, or a research synthesis with lasting reference value. That is distinct
from an **ephemeral work product** (a code review, a bug investigation, an analysis of *our
own* code), which stays in the scratchpad and nowhere else. You own the judgment of which is
which, because you know what you asked for.

When you dispatch a research/discovery agent whose output will be source material, assign it a
short kebab id like `web-search-researcher-jwt-refresh` and paste the block below into the
dispatch prompt — **substituting that id for `<agent-id>` yourself** (the agent can't derive
it). The agent then writes an intake stub alongside its report: the report stays as the full
content, the stub is the routed signal, quarantined as `agent-proposed` until a human promotes
it (trust comes from promotion, never the stub — see `~/.claude/vault/_system/routing.md`).

> **Vault intake:** Alongside your scratchpad report, write an intake stub per the **Intake
> item** contract in `~/.claude/vault/_system/schemas.md` (read it — it is authoritative) to
> `~/.claude/vault/_inbox/<agent-id>/<source-slug>.md`, where `<source-slug>` is a specific
> kebab-case name and `name:` in the frontmatter equals it. Normally write **one** stub:
> `subtype: research` for your synthesis, with `source_url` pointing at your scratchpad report
> and the underlying URLs listed in the body — write separate stubs only if you consumed
> several genuinely standalone documents (each its own `article`/`paper`/`youtube`/`podcast`).
> Set the literals `provenance: agent-proposed` (the only provenance you may write) and
> `status: pending-promotion`; set `agent_id` to `<agent-id>`, `ingested` to today, and
> `sha256` to a hash of what you saved (best-effort drift marker in V1). Body: one paragraph on
> what the source contributes, then the absolute path to your scratchpad report. Write ONLY
> under `_inbox/<agent-id>/` — never `atlas/`, `MEMORY.md`, or `_ops/`; if an atlas entry for
> the same concept exists, read it first so the stub adds rather than duplicates.

Skip this entirely when a consultation produces only read-only work products — there is
nothing to route.

## Related Skills

| Skill | Use When |
|-------|----------|
| `design-meeting` | Multiple domain perspectives needed, agents discuss and converge |
| `domain-review-before-implementation` | About to dispatch implementation work — review the brief first |
| `subagent-driven-development` | Executing plan tasks sequentially with review gates |
| `writing-personas` | Creating or tuning a persona; judging whether a persona adds value |
| `agent-personality` (plugin) | Building a durable persona file; `team-composition` for roster balance |

**This skill (consulting-agents):** Single-agent research, expertise, review — agents advise, you decide.

## Decision Matrix

**Consult when:**
- ✅ Need information
- ✅ Want expert opinion
- ✅ Need code review
- ✅ Validating approach
- ✅ Pattern discovery

**Don't consult, implement directly when:**
- ❌ You have the info already
- ❌ Simple/obvious task
- ❌ Need tight context continuity

**Don't consult, delegate implementation when:**
- Task is well-scoped with clear acceptance criteria
- Fresh context beneficial
- See `subagent-driven-development`

## Red Flags

**Never:**
- Give agents blocking authority (you decide)
- Skip reading agent reports
- Parallelize without deciding who synthesizes
- Dispatch a persona that is identity without a capability foundation

**Always:**
- Include target fidelity and audience framing in the prompt
- Synthesize parallel results (don't just aggregate)
- Prefer SendMessage continuation over re-briefing for follow-ups
- Maintain final decision authority
