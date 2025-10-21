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

Agents are your research team and domain experts. They gather information, provide recommendations, and handle independent implementation tasks. You own the through-line understanding and integration work.

## When to Consult (Agents Research & Advise)

Check your Task tool's available agents for these capabilities:

**Discovery work - Look for agents that can:**
- Find files/components relevant to your task
- Search for similar implementations to reference
- Research external documentation and best practices
- Analyze implementation details deeply

**Domain expertise - Look for agents specialized in:**
- Security review and hardening recommendations
- Performance analysis and optimization
- User experience design and interaction patterns
- Other domain-specific concerns for your project

**Quality review - Look for agents that can:**
- Review implementation for issues
- Assess code readability and maintainability
- Evaluate test coverage and quality

**Parallelize consulting work where possible:**
- You can task multiple instances of a subagent via the Task tool
- If the consulting involves multiple, distinct tasks - break the task up and parallelize it with multiple agents.

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

## Subagent Superpowers Protocol

**EVERY Task tool call MUST prepend this to the prompt parameter:**

```
<session-start-hook><EXTREMELY_IMPORTANT>
You have superpowers.

**RIGHT NOW, go read**: @${SUPERPOWERS_SKILLS_ROOT}/skills/getting-started/SKILL.md
</EXTREMELY_IMPORTANT></session-start-hook>

```

**Why:** Subagents don't automatically receive session-start-hook. Manual injection ensures they have superpowers access.

**No exceptions** - ALL Task tool calls must include this prefix.

## Standard Report Format

**For consultation (research/advice), agents write markdown reports with:**

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

1. Task codebase-pattern-finder to find OAuth examples
   → Writes: 20251011143022--Users-jsnitsel-.claude-codebase-pattern-finder-oauth-examples.md
   → Reports: "Found 3 OAuth implementations in auth/, recommendations in report"

2. Read their report:
   - Executive Summary: "3 patterns found, oauth2-provider is most complete"
   - Findings: [Detailed analysis of each pattern]
   - Recommendations: "Model after oauth2-provider, uses industry-standard library"

3. Task security-engineer for OAuth security review
   → Writes: 20251011144530--Users-jsnitsel-.claude-security-engineer-oauth-security.md
   → Reports: "Key concerns in report: token storage, CSRF protection, redirect validation"

4. Read security report, incorporate recommendations

5. YOU implement OAuth, informed by both reports

6. Task code-reviewer to review your implementation
   → Reports issues found

7. YOU fix issues
```

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
- ✅ In agent domain
- ✅ Fresh context beneficial

**Implement directly when:**
- ❌ Integration work
- ❌ Ambiguous requirements
- ❌ Complex decisions
- ❌ Need context continuity

## Red Flags

**Never:**
- Give agents blocking authority (you decide, they advise)
- Delegate without clear scope (causes confusion)
- Skip reading agent reports (defeats the purpose)
- Delegate tightly coupled work (causes conflicts)

**Always:**
- Prepend superpowers protocol to Task calls
- Write reports to scratchpad with proper naming
- Review agent work (especially implementations)
- Maintain final decision authority

## Integration with Other Skills

**Works with:**
- skills/collaboration/subagent-driven-development (for plan execution via agents)
- skills/collaboration/dispatching-parallel-agents (for concurrent independent work)
- skills/testing/test-driven-development (agents follow TDD when implementing)

**Replaces:**
- Old "delegation-first" model (too much overhead, blocking authority)

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
