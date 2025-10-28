---
name: Consulting Agents
description: Strategic use of agents for research, expertise, and selective implementation delegation
when_to_use: When you need discovery, domain expertise, code review, or can delegate independent implementation tasks
version: 1.0.0
---

# Consulting Agents

## Overview

**Strategic delegation: Use agents when it makes sense.** They research, advise, review, and sometimes implement.

**No blocking authority.** You make final calls. Agents provide input, you decide.

## Core Principle

Agents provide **fresh context** for focused tasks. The value comes from clean slate + clear task description, not from specialist identity.

You own the through-line understanding and integration work. Agents research, advise, review, and sometimes implement specific tasks.

## Available Agent Types

**Discovery Agents (Codebase Exploration):**
- `codebase-locator`: Find files/components relevant to your task
- `codebase-analyzer`: Analyze implementation details deeply
- `codebase-pattern-finder`: Search for similar implementations to reference
- `web-search-researcher`: Research external documentation and best practices

**General-Purpose Agent:**
- Use for: consultation, code review, premise validation, implementation
- Provide **domain-focused task wording** instead of relying on specialist identity
- Fresh context + clear task description = expert-level results
- Naturally uses research tools (alexandria, web-search) when uncertain

**Example domain-focused task wording:**
- "Review this code for security issues: authentication, authorization, input validation, SQL injection, XSS"
- "Analyze performance: identify bottlenecks, unnecessary allocations, N+1 queries, algorithmic complexity"
- "Validate premise: is there real need for an MCP tool that allows desktop native GUI debugging by AI assistants?"

## When to Consult (Agents Research & Advise)

**Use discovery agents when you need:**
- File/component location in codebase
- Similar implementation patterns to reference
- External documentation and best practices
- Deep analysis of existing code

**Use general-purpose when you need:**
- Domain expertise (security, performance, UX) with domain-focused task wording
- Code review for quality, maintainability, test coverage
- Premise validation with fresh perspective
- Technical consultation on design decisions

## Task Prompt Iteration Protocol

**Before dispatching agents, refine the task prompt through iteration:**

1. **Draft initial task prompt** with:
   - What you want the agent to do
   - Domain-specific concerns to focus on
   - Any context or constraints

2. **Present to general-purpose agent** (in current context):
   ```
   "I'm planning to task an agent with: [task description]

   What additional information or context would help ensure a thorough response?"
   ```

3. **Agent responds with needs**:
   - "I need X, Y, Z"
   - Usually 1-2 iterations max (rarely need 3rd)

4. **Update task prompt** with requested info

5. **Confirm with agent**: "Does this have everything needed?"
   - Agent gives thumbs up

6. **Dispatch to fresh agent context** with refined prompt

**Why this works:**
- Same model, different context = fresh perspective without accumulated assumptions
- Task iteration ensures clear, complete requirements
- Domain-focused wording triggers domain expertise without specialist identity baggage

## Parallelization Patterns

Dispatch multiple agents in a SINGLE message when tasks are orthogonal and read-only.

**Pattern: Multiple discovery agents**
```
[Dispatch 3 codebase-locator agents in one message:
  Agent 1: "find authentication components"
  Agent 2: "find session handling code"
  Agent 3: "find authorization middleware"
]
→ all three run concurrently → you synthesize results
```

**Pattern: Discovery + domain review**
```
[Dispatch codebase-locator + 2 general-purpose agents in one message:
  - codebase-locator: "find OAuth implementation patterns"
  - general-purpose #1: "review OAuth patterns for security: token storage, CSRF, redirect validation"
  - general-purpose #2: "review OAuth patterns for performance: token caching, API rate limiting, connection pooling"
]
→ discovery + security review + performance review in parallel
→ you synthesize their findings
```

**When to parallelize:**
- Discovery work (multiple searches, different targets)
- Domain reviews (security, performance, UX perspectives on same code)
- Research (multiple web searches, documentation lookup)
- Any orthogonal read-only operations

**Critical: Parallelization trades task-specific depth for speed, but can miss integration issues.** See Synthesis Layer below.

**Agents write findings to scratchpad (see Scratchpad Protocol below), you read and apply their recommendations.**

## When to Delegate Implementation

**Delegate when:**
1. Task is independent and well-scoped
2. Clear acceptance criteria exist
3. In agent's domain expertise
4. Fresh context is beneficial (prevents pollution)
5. Parallel work is possible

**Examples:**
- Independent bug fix in isolated module
- Implementing task from detailed plan
- Multiple parallel fixes (different subsystems)
- Agent-specific work (security hardening after security-engineer review)

**Don't delegate when:**
- Integration work across multiple areas
- Ambiguous requirements need clarification
- Complex decisions required
- You need to maintain context

**Parallelizing implementation tasks:**

- This requires careful consideration, and justification before proceeding.
- It must be work that is orthogonal with respect to files being touched, to avoid conflicts among agents working at the same time.
- In this case agents should commit only their changes, or you must tell them not to commit the changes, and you handle it yourself.
- If you do plan to parallelize implementation of something, you must announce it to the user, and get their explicit approval to proceed.

## Synthesis Layer (Avoiding "Forest for Trees")

**Problem:** Parallel task-specific agents can miss integration issues.

**What parallel agents catch well:**
- Task 1's code quality, security, performance (agent 1)
- Task 2's code quality, security, performance (agent 2)
- ... etc for all N tasks

**What parallel agents might miss:**
- How Task 1 and Task 3 interface with each other
- Whether Task 2's assumptions contradict Task 5's approach
- Overall architectural coherence across all tasks
- Cross-cutting concerns spanning multiple components

**Synthesis Options:**

**Option 1: You coordinate (default)**
- Read all parallel agent reports
- Identify integration issues yourself
- Make architectural decisions
- Best when: Small number of agents (2-4), you understand domain

**Option 2: Coordinating agent**
- Dispatch architecture specialist to review all N results
- Tasked with finding cross-task issues
- Reports integration concerns to you
- Best when: Large number of agents (5+), complex integration

**Option 3: Two-phase review**
- Phase 1: Parallel task-specific reviews (speed)
- Phase 2: System-level integration review (coordination)
- Best when: Time-critical + complex integration

**Coordination tax cannot be eliminated, only optimized.**

When parallelizing, explicitly decide who synthesizes: you, a coordinating agent, or phased approach.

## Scratchpad Protocol

**Location:** `~/.claude/scratchpad/` (gitignored)

**Filename format:**
```
{timestamp}-{project-slug}-{agent-type}-{task-slug}.md
```

**Components:**
- `timestamp`: YYYYMMDDHHmmss (e.g., 20251011143022)
- `project-slug`: Working directory path with `/` and `.` replaced by `-` (matches .claude/projects format)
- `agent-type`: Agent name (e.g., codebase-locator, security-engineer)
- `task-slug`: Short kebab-case description (e.g., oauth-patterns, security-review)

**Example:**
```
20251011143022--Users-jsnitsel-.claude-codebase-locator-oauth-patterns.md
20251011144530--Users-jsnitsel-.claude-security-engineer-review-oauth.md
```

**Project slug generation:**
From working directory `/Users/jsnitsel/.claude`:
1. Take full absolute path
2. Replace `/` with `-`
3. Replace `.` with `-`
4. Result: `-Users-jsnitsel-.claude`

## Standard Report Format

**For consultation (research/advice), agents write markdown reports with:**

**Objective Analysis Required:**
- Focus on technical facts and architectural patterns, not quality judgments
- Avoid superlatives: "production-grade", "textbook-perfect", "exceptional", "brilliant"
- Describe what exists and how it connects, not how good or bad it is
- Flag specific concerns and issues with evidence
- Let technical details speak for themselves
- If praising, cite specific measurable evidence (not subjective impressions)

```markdown
# Task: [What you asked them to do]

## Executive Summary
[2-3 sentences: What they found, key recommendation]

## Findings
[Detailed discoveries, analysis, evidence]

## Recommendations
[Specific actionable suggestions for you]

## References
[Files examined, sources consulted, relevant documentation]
```

**For implementation, agents report:**
- What they implemented
- Tests written and results
- Files changed
- Any issues encountered

## Consultation Workflow Example

```
You: Need to add OAuth support

1. Task codebase-pattern-finder: "Find OAuth implementations - describe patterns objectively, no quality judgments"
   → Writes: 20251011143022--Users-jsnitsel-.claude-codebase-pattern-finder-oauth-examples.md
   → Reports: "Found 3 OAuth implementations in auth/, recommendations in report"

2. Read their report:
   - Executive Summary: "3 patterns found, oauth2-provider is most complete"
   - Findings: [Detailed analysis of each pattern]
   - Recommendations: "Model after oauth2-provider, uses industry-standard library"

3. Iterate on security review task prompt:
   You: "I want to task an agent to review OAuth patterns for security. What do they need?"
   Agent (current context): "I'd need: the file paths, specific OAuth flow being used, what security concerns matter most (tokens, sessions, etc.)"
   You: "Thanks, I'll include that."

4. Task general-purpose (fresh context): "Review OAuth implementations in auth/ for security issues. Focus on: token storage (where/how stored), CSRF protection (anti-CSRF tokens present?), redirect validation (whitelist checks), session management (secure flags, expiration). Files: auth/oauth2-provider.ts, auth/token-store.ts"
   → Writes: 20251011144530--Users-jsnitsel-.claude-general-purpose-oauth-security.md
   → Reports: "Key concerns in report: token storage uses localStorage (should be httpOnly cookies), missing CSRF protection, redirect validation incomplete"

5. Read security report, incorporate recommendations

6. YOU implement OAuth fixes, informed by both reports

7. Task general-purpose (fresh context): "Review OAuth implementation for code quality: readability, error handling, test coverage, DRY violations. Files changed: [list]"
   → Reports issues found

8. YOU fix issues
```

## Parallel Discovery Example

```
You: Need to understand authentication system architecture

1. Dispatch 3 codebase-locator agents + 1 general-purpose IN ONE MESSAGE:
   - codebase-locator #1: "find authentication entry points and middleware - describe what exists and how it connects"
   - codebase-locator #2: "find session management components - objective technical analysis"
   - codebase-locator #3: "find authorization and permission checking code - focus on patterns and architecture"
   - general-purpose: "review authentication architecture for security concerns: token expiration, session fixation, CSRF protection, secure storage. Flag specific issues with evidence."

   → All 4 run concurrently (massive time savings)
   → Each writes report to scratchpad

2. Read all 4 reports:
   - Auth entry points: API routes, middleware chain in routes/auth/, middleware/authenticate.ts
   - Session management: Redis store at lib/session-store.ts, JWT tokens in lib/token.ts
   - Authorization: RBAC implementation in services/permissions/, models/role.ts
   - Security concerns: Token expiration too long (7 days), session fixation risks (not regenerating SID), missing CSRF tokens

3. YOU synthesize findings:
   - Identified full auth flow from entry to authorization
   - Security gaps need addressing before new features (specific file paths identified)
   - Session and auth are coupled in middleware/authenticate.ts - refactor needed

4. Make architectural decisions informed by parallel discovery
```

**Key advantage:** Discovery that would take 15-20 minutes sequentially takes 5 minutes in parallel.

**Coordination cost:** You spend 5-10 minutes reading and synthesizing 4 reports instead of 1.

**Net win:** Faster discovery with manageable coordination overhead.

## Implementation Delegation Example

```
You: Have detailed plan with 5 independent tasks

1. Task 1: Hook installation (independent, clear scope)
   → Delegate to general-purpose agent
   → Agent implements, tests, commits
   → You review via code-reviewer

2. Task 2: Recovery modes (depends on Task 1 being complete)
   → Delegate to general-purpose agent
   → Agent implements, tests, commits
   → You review

3. Task 3: Integration work (touches multiple areas, complex decisions)
   → YOU implement (not suitable for delegation)

4. Task 4 & 5: Independent bug fixes in different subsystems
   → Delegate to TWO agents in parallel
   → Both work concurrently
   → You review and integrate
```

## Decision Matrix

**Consult when you need:**
- Information gathering
- Expert opinion
- Code review
- Pattern discovery

**Delegate implementation when:**
- ✅ Independent task
- ✅ Clear scope
- ✅ Well-defined outcomes
- ✅ Task description provides domain context (not relying on specialist identity)
- ✅ Fresh context beneficial

**Implement directly when:**
- ❌ Integration work
- ❌ Ambiguous requirements
- ❌ Complex decisions
- ❌ Need context continuity

**Parallelize consulting when:**
- ✅ Multiple orthogonal searches/reviews needed
- ✅ Read-only operations (no repository state changes)
- ✅ Tasks are independent (can run concurrently)
- ✅ Time savings justify synthesis overhead
- ✅ You can synthesize results (or dispatch coordinator)

**Don't parallelize when:**
- ❌ Tasks have dependencies (A must inform B)
- ❌ Single sequential flow makes more sense
- ❌ Only 1-2 agents needed (parallel overhead not worth it)
- ❌ Integration issues likely (tight coupling between components)
- ❌ No one to synthesize (coordination tax too high)

## Red Flags

**Never:**
- Give agents blocking authority (you decide, they advise)
- Delegate without clear scope (causes confusion)
- Skip reading agent reports (defeats the purpose)
- Delegate tightly coupled work (causes conflicts)
- Parallelize without deciding who synthesizes (you, coordinator, or phased)
- Skip synthesis when parallelizing (misses integration issues)

**Always:**
- Prepend superpowers protocol to Task calls
- Write reports to scratchpad with proper naming
- Review agent work (especially implementations)
- Maintain final decision authority
- Synthesize parallel agent results (don't just aggregate)

## Why Fresh Context + Domain-Focused Tasks Work

**Experimental finding:** General-purpose agents with clear domain-focused tasks consistently outperform specialist agents.

**What we tested:**
- Code review (Rust, TypeScript)
- Technical consultation (lifetime errors, architecture decisions)
- Test coverage analysis

**Results across all tests:**
- General-purpose found MORE issues (17 vs 12-14 in code review)
- General-purpose used research tools naturally (alexandria, web-search)
- Specialists missed API design patterns, naming conventions, standard traits

**Why specialists underperformed:**

1. **Overconfidence Trap**
   - "You are a senior X specialist" → agent commits to expert role
   - Expert identity prevents admitting uncertainty
   - Doesn't explore tools (experts don't need to look things up)
   - Relies on training data instead of current references

2. **Narrow Focus Blindness**
   - Specialists focus on "hard problems" (unsafe code, performance)
   - Miss systematic concerns (API design, naming, trait completeness)
   - General-purpose has no focus constraint → broader coverage

3. **Prompt Bloat Didn't Help**
   - Tested 21, 35, 63, 65 line versions
   - All missed same patterns
   - Checklists not systematically followed
   - "Principles" don't force behavior

**What actually works:**

- **Fresh context** = clean slate without accumulated assumptions
- **Domain-focused task wording** = triggers domain expertise without identity baggage
- **Tool exploration** = general-purpose naturally uncertain → uses alexandria, web-search
- **Comprehensive breadth** = no narrow focus → catches more issues

**Example:** Same model (Sonnet 4.5), different approaches:
- Specialist: "You're a Rust expert" → confident → no tools → missed 5 API patterns
- General-purpose: No identity claim → uncertain → searched alexandria → caught all patterns

**Lesson:** Expertise comes from tools and clear tasks, not from prompt identity claims.

## Integration with Other Skills

**Works with:**
- skills/collaboration/subagent-driven-development (for plan execution via agents)
- skills/collaboration/dispatching-parallel-agents (for concurrent independent work)
- skills/testing/test-driven-development (agents follow TDD when implementing)

**Replaces:**
- Old "delegation-first" model (too much overhead, blocking authority)
- Specialist consultant agents (general-purpose + domain-focused tasks performs better)

## Advantages

**vs. Always implementing yourself:**
- Faster discovery (parallel research)
- Domain expertise access
- Fresh perspective on reviews
- Can parallelize independent work

**vs. Always delegating:**
- You maintain context and control
- Less coordination overhead
- Faster for integrated work
- No authority gridlock

**Best of both worlds:** Flexibility to choose the right tool for each situation.
