---
name: domain-review-before-implementation
description: Use when about to dispatch implementation work or start coding from a plan, task brief, or spec. Catches design flaws in the brief before they become bugs in the code. Also triggered by "implement this plan", "start coding", "dispatch implementation agent", or when you recognize the thought "this brief looks straightforward, just implement it." Do NOT activate for code review of already-written code — that's a different skill.
---

# Domain Review Before Implementation

## The Trigger

**Use this skill when you're about to:**
- Dispatch a `Task()` for implementation work
- Start coding from a plan or task description
- Send a prompt to a subagent that will write code

**The prompt you write IS the brief.** If you're about to send an implementation agent a task, that task description needs review first.

**Ask yourself:** "Am I about to have code written (by me or an agent)?" If yes → domain review first.

## Overview

**Core principle:** Task briefs contain design flaws. Domain experts catch them before implementation, not code reviewers after.

**Real-world data:** A "straightforward serialization" brief reviewed by domain expert found 8 issues (3 critical type safety bugs, 3 important design gaps, 2 minor improvements). Cost: 5 minutes review. Savings: hours of debugging and refactoring.

## The Iron Law

```
NO IMPLEMENTATION FROM AN UNREVIEWED BRIEF
```

Review coverage is inherited, not re-earned per dispatch:

- **Plan/design level: review is MANDATORY, no exceptions.** Before any
  implementation begins, the plan or design the briefs derive from gets
  domain-expert review (in addition to any human review). This is where
  unimplementable assertions, wrong approaches, and flawed test designs get
  caught — a good plan review catches per-task flaws because the task briefs
  ARE the plan's tasks.
- **Task-brief level: review is CONDITIONAL.** A brief lifted directly from a
  reviewed plan inherits that review. Dispatch a focused brief review when ANY
  of these hold:
  - the brief adds material the reviewed plan doesn't contain, or deviates
    from it
  - the task enters a novel or high-risk domain (security, concurrency,
    serialization, data loss) the plan review didn't examine in depth
  - there was no plan-level review (ad-hoc task) — then the brief IS the
    plan, review it
- **Time pressure is not an exemption** — it's when review pays most.

A capable implementation agent will sometimes catch a brief flaw mid-task and
deviate with justification. Treat that as the last line of defense, not the
plan — require agents to report deviations, never to silently absorb them.

## When to Use

**MANDATORY for:**
- Any plan, spec, or design about to drive implementation
- Ad-hoc task briefs with no reviewed plan behind them

**Dispatch an additional per-brief review when:**
- Brief includes code examples the plan review didn't see (may have anti-patterns)
- Specialized domain (serialization, networking, security, concurrency, data modeling)
- You recognize the pattern (familiarity breeds assumptions)
- The brief paraphrases the plan rather than quoting it (paraphrase drift is real)

## The Pattern

### BEFORE This Skill

```
Read brief → Implement → Code review finds issues → Refactor
Cost: Implementation time + refactoring time + context switching
```

### AFTER This Skill

```
Read brief → Domain experts review brief → Fix brief → Implement with corrections
Cost: 5 minutes review
Savings: Hours of rework
```

## Implementation

### Step 1: Dispatch Domain Expert

**If you have the Agent tool available:**

Use the Agent tool to dispatch domain-appropriate expert agents — project
personas where the roster has the right lens (pairing complementary lenses,
e.g. an invariant tracer plus a premise auditor, catches more than two passes
of the same lens), `general-purpose` with a role line otherwise.

- If reviewing an implementation plan, dispatch multiple agents focused on different aspects (examples: algorithmic correctness, architecture, api, tasks properly sized, ...)
- If reviewing a design, dispatch multiple agents focused on different aspects (examples: conceptual correctness, ui/ux, architecture, api, ...)
- If reviewing a task brief dispatch domain-appropriate expert agents to validate the prompt.

Dispatch the agents with a prompt similar to this format:

```
Agent(subagent_type="general-purpose", prompt="""
**Role:** You are a [domain] expert specializing in [specific area].

**Task:** Review this task brief for technical correctness and design flaws.

**Brief location:** [path to brief]

**Review focus:**
1. [Domain-specific concerns - e.g., serialization format, data types, security, industry standards]
2. Edge cases and error handling
3. Performance implications
4. Best practices compliance
5. Integration considerations
6. Coherence with overall plan
7. Task complexity and whether it should be decomposed

**Provide:**
1. List of issues (Critical/Important/Minor)
2. For each: what's wrong and recommended fix
3. Things done well
4. Overall: "Ready to implement" or "Needs revision"

**Note:** Review the BRIEF/DESIGN, not code. Focus on flaws that cause problems during implementation.
""")
```

**If Task tool not available:**

STOP and ask your human partner: "I need to have a domain expert review this brief before implementing. How should I dispatch a consulting agent in this environment?"

Don't skip review because tool isn't obvious. Escalate to get the right mechanism.

### Step 2: Address Issues

- Fix all Critical issues in brief before implementing
- Fix Important issues (or document why skipping)
- Note Minor issues for cleanup

### Step 3: Implement with Corrections

Now dispatch implementation agent with corrected brief.

### Step 4: Code Review After Implementation

Use code-reviewer to catch implementation gaps.

## Domain Expert Examples

**Serialization tasks:** "Data serialization expert specializing in format design, type safety, and versioning"

**Security tasks:** "Application security specialist focusing on OWASP Top 10, attack vectors, and secure design patterns"

**Networking tasks:** "Distributed systems expert specializing in protocols, error handling, and network reliability"

**Database tasks:** "Database architect specializing in schema design, indexing strategies, and query optimization"

**Algorithm tasks:** "Algorithm specialist focusing on complexity analysis, edge cases, and correctness proofs"

**Concurrency tasks:** "Concurrency expert specializing in race conditions, deadlocks, and synchronization patterns"

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Brief is simple/straightforward" | Task 16 "straightforward serialization" had 8 issues. Simple briefs hide complex issues. |
| "Brief has TDD steps already" | TDD tests the implementation, not the design. Flawed design → passing tests for wrong behavior. |
| "Not security-critical" | Technical correctness matters everywhere. Type safety bugs, data loss, performance issues affect all code. |
| "I know this pattern" | Familiarity causes assumptions. Expert finds issues you overlook because "I've done this before." |
| "Domain review is overkill" | Minutes of review vs hours of debugging. The ratio has narrowed with stronger models, but it has not inverted — and the worst flaws (unimplementable designs, wrong approaches) still cost a full implementation cycle. |
| "I can see issues myself" | Then fix them in the brief BEFORE implementing. Domain expert systematically finds what you miss. |
| "We already reviewed the plan, so we don't need a review for this task brief" | True ONLY if the brief is lifted from the reviewed plan without additions. If the brief paraphrases, extends, or deviates — review the delta. |
| "The implementation agent will catch brief flaws" | Sometimes it will — that's the last line of defense, not the plan. Flaws it absorbs silently become code. |

## Red Flags - You're Rationalizing

If the plan behind the brief was never domain-reviewed and you think ANY of
these thoughts, STOP and dispatch domain expert:

- "Brief is well-specified, just implement it"
- "This is a standard pattern"
- "The examples look good"
- "We're in a hurry"
- "Domain review for this is overkill"
- "I'll catch issues during implementation"

**All of these mean: Dispatch domain expert first.** The only legitimate skip
is documented inheritance: the brief is the reviewed plan's task, verbatim.

## Integration with Workflows

### With subagent-driven-development

**CRITICAL:** If you're using subagent-driven-development, domain review of
the PLAN is a mandatory gate before the first dispatch.

```
Before any task dispatch:
  1. DISPATCH DOMAIN EXPERT(S) to review the plan      ← MANDATORY
  2. ADDRESS findings, revise plan                     ← MANDATORY

For each task:
  3. READ the task from plan
  4. If the brief deviates from the reviewed plan, is novel/high-risk,
     or had no plan review: dispatch a focused brief review first
  5. Dispatch implementation subagent (brief quotes the plan; agent must
     report any deviations, never absorb them silently)
  6. Code review
  7. Fix code review issues
```

**Why both reviews:**
- Domain review: Catches design flaws in the BRIEF (wrong approach, anti-patterns, security issues)
- Code review: Catches implementation gaps in the CODE (missed requirements, bugs, style issues)

Skipping domain review = implementing flawed designs. Code review can't fix architectural problems.

### With executing-plans

Add domain review as first step before parallel execution:

```
1. Load plan
2. For each task: Dispatch domain expert, collect issues
3. Review all domain feedback with human
4. Execute tasks in parallel with corrections applied
```

## Why This Works

**Prevention vs remediation.** A review costs minutes; a flawed brief costs an
implementation cycle plus debugging plus rework. The exact ratio shifts with
model strength — implementation agents now catch some brief flaws themselves —
but the asymmetry survives because the worst brief flaws (unimplementable
assertions, wrong approach, vacuous tests) produce work that *looks* done and
fails later, which is the most expensive failure shape there is.

Worked example from practice: a reviewed implementation plan for a
determinism-contract branch had two MAJOR flaws caught by plan review — an
assertion targeting a container with no defined order, and a mutation check
that was a silent no-op. Each would have burned a full subagent session and
produced a false-confidence test suite.

## Real-World Example

**Task:** "Implement data serialization using NumPy npz format"

**Without domain review:**
- Implement using code from brief
- Tests pass ✓
- MyPy fails (numpy scalars vs Python types)
- Runtime errors (ID arrays not numpy arrays)
- Missing validation (corrupted files accepted)
- Refactor for 2+ hours

**With domain review:**
- 5 min domain review finds 8 issues
- Fix in brief before implementing
- Implementation takes 30 min
- Tests pass ✓
- MyPy passes ✓
- Code review finds 1 minor issue
- Fix in 5 min
- Done

## The Bottom Line

**Task briefs lie.** Not maliciously - they're written without complete knowledge. Authors don't know every edge case, anti-pattern, or domain best practice.

**Domain experts find the lies before they become bugs.**

Every plan, before the first dispatch. Every brief that goes beyond the
reviewed plan. No silent exceptions.
