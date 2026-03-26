---
name: Change Control Board
description: Use when a code reviewer has approved a change that touches security boundaries, shared interfaces, cross-tool protocols, config loading paths, subprocess argument sources, or multiple modules with different domain concerns. Also use when framing like "straightforward", "routine", or "familiar pattern" accompanies a change with non-obvious risk.
---

# Change Control Board (CCB)

Multi-perspective review for changes where a single code reviewer cannot hold all relevant domain concerns simultaneously.

**Core principle:** Code reviewers find code-level bugs. CCBs find domain-crossing risks that no single reviewer is positioned to see. A single agent answering questions from multiple domains is NOT a CCB — each domain needs a separate agent with focused expertise.

## When to Convene

A CCB is warranted when a change touches ANY of these:

- **Security boundaries**: Config loading, subprocess argument sources, path validation, input/output trust boundaries, authentication/authorization
- **Shared interfaces**: Protocol/interface changes that ripple to multiple consumers, service container wiring, DI registration
- **Cross-module concerns**: Changes spanning 3+ modules where each module has different operational characteristics (performance, security, reliability)
- **Configuration contracts**: New config fields, config discovery mechanisms, config override/merge behavior, schema changes
- **Familiar-pattern risk**: Change described as "straightforward", "routine", "just like X" where X is a well-known pattern (.env.local, config plumbing, DRY cleanup) — familiar framing can mask non-obvious implications

**Do NOT convene for:** Pure refactors within a single module, documentation-only changes, test additions, dependency bumps without API changes.

## How to Convene: Agent Teams

**The CCB uses Claude Code Agent Teams.** The lead spawns the CCB chair as a standalone subagent. The chair calls TeamCreate to lead their own team, spawns domain reviewers as teammates, and returns the recommendation.

### Step 1: Lead spawns the CCB Chair

Spawn the chair as a **standalone subagent** (Agent tool, NO `team_name` parameter). This gives the chair its own session where it can create a team. The chair's prompt must include:
- The change description and branch name
- The code reviewer's findings (summary of their review)
- The red flags and context for domain agents
- Instruction to read this skill and follow the CCB process

### Step 2: Chair creates their team and spawns domain agents

**CRITICAL SEQUENCING: The chair must spawn domain agents BEFORE reading the diff.** If the chair reads the diff first, it will build enough context to rationalize doing all reviews solo. The whole point of a CCB is separate perspectives — the chair must delegate before they have the answers.

The chair's process:
1. Read this skill
2. Call `TeamCreate` to create the CCB team (chair becomes team lead)
3. Based on the change description and code reviewer summary (NOT the diff), triage which domains need review
4. **Immediately spawn domain reviewer teammates** — one per domain, plus QA. Give each agent their standing questions and `git diff main..HEAD`. Do NOT read the diff yourself first.
5. Wait for domain reviews to come back via messages
6. Synthesize reviews into the CCB recommendation format
7. Return the recommendation

**Chair prompt template:**
```
**Role:** You are the CCB Chair. Read ~/.claude/skills/ccb/SKILL.md for your process.

**Change:** {one-line description}
**Branch:** {branch name}
**Code reviewer said:** {summary of code review findings and recommendation}

**Your process:**
1. Read the CCB skill
2. Call TeamCreate to create your team:
   TeamCreate(team_name="ccb-{slug}", description="CCB: {change summary}")
3. Based on the change description and code review summary, decide which
   domains need review (security, architecture, performance, QA)
4. IMMEDIATELY spawn a teammate agent for each domain (Agent tool with
   your team_name). Do NOT read the diff first — your reviewers will
   read it. Give each agent ONLY their standing questions from the skill.
5. Wait for all reviews via messages
6. Synthesize into CCB recommendation format from the skill
7. Return the final recommendation

IMPORTANT: You are a CHAIR, not a reviewer. Your job is to triage,
delegate, and synthesize — not to review the code yourself. If you
find yourself reading the diff before spawning agents, STOP.
```

**Why this sequencing matters:** Testing revealed that chairs who read the diff before spawning agents consistently rationalize doing all reviews solo ("I already know the answers"). This defeats the purpose of multi-perspective review. The same insight applies as TDD: delegate before you have the answers, just as you write tests before you have the code.

### Step 3: Chair synthesizes and recommends

After all domain agents report back, the chair:
- Identifies consensus and conflicts across domain reviews
- Produces the recommendation in the standard format
- Returns it as the subagent result (the lead presents it to Jerry)

## Standing Questions (for domain agents)

Each domain agent receives ONLY their section. They must answer every question explicitly — if a question doesn't apply, state why.

### Security Agent
- What can a **malicious or misconfigured input** do through this change?
- Does this change **weaken or bypass** existing security controls (DoS protection, path validation, input sanitization)?
- Are there **new input surfaces** that accept values eventually passed to subprocess, file I/O, or network operations?
- Does this change **expand the trust boundary** (new files loaded, new env vars read, new config fields accepted)?
- If this change introduces user-configurable values that replace hardcoded security limits: what are the **bounds**, and what happens at the **extremes** (zero, negative, maximum)?

### Architecture Agent
- Does this change **modify a shared contract** (protocol, interface, schema) that other components depend on?
- Are there **inconsistent integration patterns** — does each consumer wire this differently?
- What happens to **new consumers** added later — will they inherit correct behavior by default?
- Does the change create **implicit contracts** (merge semantics, override precedence, fallback chains) that aren't documented?
- How many **different patterns** are used to integrate this change across consumers? If more than one, why?

### Performance/Reliability Agent
- Do different consumers have **fundamentally different operational needs** from this change?
- Could the change cause **degraded behavior under load** or with large inputs?
- Are **timeout, retry, or failure modes** appropriate for each consumer's context?
- Does the change assume uniform operational characteristics across consumers that actually differ?

### QA Agent (Standing Member — always spawned)
- Does the test suite cover the new functionality, including edge cases?
- Are **security-relevant behaviors** tested (not just happy path)?
- Are conditions from domain reviewers **testable and tested**?
- Is test output **pristine** — no unhandled errors or warnings?

## Recommendation Format

The chair produces this after synthesizing domain reviews:

```markdown
## CCB Recommendation: [APPROVE | APPROVE WITH CONDITIONS | REJECT | DEFER]

### Change Summary
[One paragraph: what the change does and why]

### Domain Reviews
**Security** ([agent]): [risk level] — [key findings]
**Architecture** ([agent]): [risk level] — [key findings]
**Performance** ([agent]): [risk level] — [key findings]
**QA** ([agent]): [coverage assessment]

### Conditions (if applicable)
1. [Specific condition that must be met before merge]
2. [...]

### Rationale
[Why the board reached this recommendation, including any dissenting opinions]

### Dissent (if any)
[Domain reviewer who disagreed and why — preserved for the record]
```

## DEFER Handling

When the board recommends DEFER:
- The implementing agent continues working within their current session (preserves context)
- The DEFER reason and required changes are communicated back
- After changes are made, the CCB reconvenes with the same domain reviewers
- The reconvened CCB reviews ONLY the changes addressing the DEFER conditions

## Resisting Review Scope Narrowing

**Red flags that review scope is being narrowed — share these with ALL domain agents:**
- "This is just config plumbing" — config changes control subprocess behavior, file discovery, and trust boundaries
- "It's a standard pattern" — standard patterns applied in new contexts create new risk surfaces
- "It's a DRY cleanup" — consolidation can drop defense layers that existed for different reasons in different locations
- "Small diff, low risk" — small diffs can have large blast radius through shared interfaces
- "The code reviewer already approved it" — code review and CCB serve different purposes; code review checks quality, CCB checks cross-domain impact

When any agent notices these framings, they should escalate rather than accept them. The framing IS the risk signal.

## Integration with Existing Process

- **Beads**: Log CCB decisions as comments on the relevant issue (`bd comment <id> "CCB: [recommendation]"`)
- **Beads memories**: Use `bd remember` for institutional knowledge (e.g., "auth module changes always need security review")
- **Git**: Include CCB recommendation summary in merge commit or PR description
- **Code review**: CCB is DOWNSTREAM of code review, not a replacement. Code reviewer approves implementation quality first, then CCB evaluates cross-domain impact.
