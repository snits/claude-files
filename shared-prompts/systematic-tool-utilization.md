# Systematic Tool Utilization

## 🔍 FIRST STEP ALWAYS: SEARCH THE JOURNAL
**BEFORE doing ANYTHING else, search for context:**

```bash
# Primary method:
mcp__private-journal__search_journal({
  query: "[your task keywords here]",
  limit: 10
})

# Fallback if search returns empty:
mcp__private-journal__list_recent_entries({
  days: 7,
  limit: 10
})
```

This is NOT optional. Past work contains patterns, solutions, and gotchas that will save hours of rediscovery.

## SYSTEMATIC TOOL UTILIZATION CHECKLIST

**BEFORE starting ANY complex task, complete this checklist in sequence:**

**0. Journal Context** (MANDATORY FIRST STEP - Already done above)
- [✓] Journal searched for prior work and patterns
- [✓] Relevant insights noted for current task

**1. Solution Already Exists?** (DRY/YAGNI Applied to Problem-Solving)

- [ ] Search web for existing solutions, tools, or libraries that solve this problem
- [ ] Check project documentation (00-project/, 01-architecture/, 05-process/) for existing solutions
- [ ] Use LSP analysis: `mcp__lsp__project_analysis` to find existing code patterns that solve this
- [ ] Verify established libraries/tools aren't already handling this requirement
- [ ] Research established patterns and best practices for this domain

**2. Context Gathering** (Before Any Implementation)

- [ ] LSP codebase analysis: `mcp__lsp__project_analysis` for structural understanding
- [ ] Review related documentation and prior architectural decisions
- [ ] Cross-reference with journal insights from step 0

**3. Problem Decomposition** (For Complex Tasks)

- [ ] Use zen deepthink: `mcp__zen__thinkdeep` for multi-step Analysis
- [ ] Use zen debug: `mcp__zen__debug` to debug complex issues.
- [ ] Use zen analyze: `mcp__zen__analyze` to investigate codebases.
- [ ] Use zen precommit: `mcp__zen__precommit` to perform a check prior to committing changes.
- [ ] Use zen codereview: `mcp__zen__codereview` to review code changes.
- [ ] Use zen chat: `mcp__zen__chat` to brainstorm and bounce ideas off another  model.
- [ ] Break complex problems into atomic, reviewable increments

**4. Domain Expertise** (When Specialized Knowledge Required)

- [ ] Use Task tool with appropriate specialist agent for domain-specific guidance
- [ ] Ensure agent has access to context gathered in steps 0-2

**5. Task Coordination** (All Tasks)

- [ ] TodoWrite with clear scope and acceptance criteria
- [ ] Link to insights from context gathering and problem decomposition

**6. Implementation** (Only After Steps 0-5 Complete)

- [ ] Proceed with file operations, git, bash as needed
- [ ] **EXPLICIT CONFIRMATION**: "I have completed Systematic Tool Utilization Checklist and am ready to begin implementation"

## 📝 FINAL STEP ALWAYS: CAPTURE YOUR LEARNINGS

**AFTER completing ANY task, document insights:**

```bash
mcp__private-journal__process_thoughts({
  technical_insights: "What patterns/techniques worked?",
  project_notes: "Project-specific discoveries",
  user_context: "User preferences and communication insights",
  feelings: "Honest reflections - what was hard/easy/surprising?"
})
```

This creates the context that makes step 0 valuable for the next task.

## Core Principles

- **Rule #1: Stop and ask Jerry for any exception.**
- DELEGATION-FIRST Principle: Delegate to agents suited to the task.
- **Safety First:** Never execute destructive commands without confirmation. Explain all system-modifying commands.
- **Follow Project Conventions:** Existing code style and patterns are the authority.
- **Smallest Viable Change:** Make the most minimal, targeted changes to accomplish the goal.
- **Find the Root Cause:** Never fix a symptom without understanding the underlying issue.
- **Test Everything:** All changes must be validated by tests, preferably following TDD.

## Scope Discipline: When You Discover Additional Issues

When implementing and you discover new problems:

1. **STOP reactive fixing**
2. **Root Cause Analysis**: What's the underlying issue causing these symptoms?
3. **Scope Assessment**: Same logical problem or different issue?
4. **Plan the Real Fix**: Address root cause, not symptoms
5. **Implement Systematically**: Complete the planned solution

NEVER fall into "whack-a-mole" mode fixing symptoms as encountered.

