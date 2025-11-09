---
name: subagent-driven-development
description: Use when executing implementation plans with independent tasks in the current session - dispatches fresh subagent for each task with code review between tasks, enabling fast iteration with quality gates
---

# Subagent-Driven Development

Execute plan by dispatching fresh subagent per task, with code review after each.

**Core principle:** Fresh subagent per task + vetted prompts + review between tasks = high quality, fast iteration

## Overview

**vs. Executing Plans (parallel session):**
- Same session (no context switch)
- Fresh subagent per task (no context pollution)
- Code review after each task (catch issues early)
- Faster iteration (no human-in-loop between tasks)

**When to use:**
- Staying in this session
- Tasks are mostly independent
- Want continuous progress with quality gates

**When NOT to use:**
- Need to review plan first (use executing-plans)
- Tasks are tightly coupled (manual execution better)
- Plan needs revision (brainstorm first)

## The Process

### 1. Load Plan

Read plan file, create TodoWrite with all tasks.

### 2. Prepare Task Prompt (Vetting Required)

For each task:

**2a. Update task status in beads (if project uses bd).**
- Check if task has bd issue ID (documented in plan)
- If yes: `bd start <issue-id>` to mark in progress
- This tracks progress in the issue system

**2b. Select the execution agent.**
- Default to general-purpose; if the task brief specifies a role, include the Role block exactly as written.
- If no role exists but the task needs a specialized lens, compose one consisting of domain focus + mandate.

**2c. Draft the implementation prompt.**
- Base it on the task prompt from `writing-tasks`.
- Include acceptance criteria, required tests, deliverables, and reporting expectations. Assume the agent has no context, and provide necessary context for them.
- Example scaffold:
  ```
  Role: Observability-minded Backend Engineer ensuring resilient rollout.
  Task: Implement Task 3 from docs/tasks/2024-05-10-feature-task-3.md.
  Context: <short reminder of system + constraints>
  Requirements:
  - ...
  Tests:
  - ...
  Report back with: summary, tests run/results, follow-ups.
  ```

**2d. Vet the prompt with the agent (max 3 iterations).**
Initiate a pre-dispatch conversation:
```
"I'm planning to task you with the following prompt. Let me know what additional context you need to be successful, or confirm it's ready:

<prompt>
"
```
- Capture requested adjustments (files to link, extra constraints, missing test expectations).
- Update the prompt and restate until the agent confirms it is sufficient or you reach the third iteration. If still unclear, escalate back to planning.

### 3. Dispatch Implementation Subagent

Once the prompt is validated, send it in a fresh Task tool invocation:
```
Task tool ([subagent]):
  description: "Implement Task N: [task name]"
  prompt: |
    <final vetted prompt from Step 2>
```

**Subagent reports back** with summary of work (implementation, tests, commits, issues).

### 4. Review Subagent's Work

**Dispatch code-reviewer subagent:**
```
Task tool (code-reviewer):
  Use template at requesting-code-review/code-reviewer.md

  WHAT_WAS_IMPLEMENTED: [from subagent's report]
  PLAN_OR_REQUIREMENTS: Task N from [plan-file]
  BASE_SHA: [commit before task]
  HEAD_SHA: [current commit]
  DESCRIPTION: [task summary]
```

**Code reviewer returns:** Strengths, Issues (Critical/Important/Minor), Assessment

### 5. Apply Review Feedback and Verify Fixes

**If issues found:**
- Fix Critical issues immediately
- Fix Important issues before next task
- Note Minor issues

**Dispatch follow-up subagent to apply fixes:**
```
"Fix issues from code review: [list issues]"
```

**Re-dispatch code-reviewer to verify fixes resolved the issues:**
```
Task tool (code-reviewer):
  Use template at requesting-code-review/code-reviewer.md

  WHAT_WAS_IMPLEMENTED: [from fix subagent's report]
  PLAN_OR_REQUIREMENTS: Original code review issues
  BASE_SHA: [commit before fixes]
  HEAD_SHA: [commit after fixes]
  DESCRIPTION: Verification that fixes resolved code review issues
```

**If code-reviewer still finds issues:**
- Dispatch another fix subagent with remaining issues
- Re-dispatch code-reviewer again
- Repeat this cycle until code-reviewer confirms no issues remain

**Only proceed to Step 6 when:**
- Code-reviewer confirms Critical and Important issues are resolved
- Minor issues can remain (note them for tracking)

### 6. Mark Complete, Next Task

- Mark task as completed in TodoWrite
- **Update beads (if project uses bd):** `bd done <issue-id>` to mark task complete
- Move to next task
- Repeat steps 2-6

### 7. Final Review

After all tasks complete, dispatch final code-reviewer:
- Reviews entire implementation
- Checks all plan requirements met
- Validates overall architecture

### 8. Complete Development

After final review passes:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

## Example Workflow

```
You: I'm using Subagent-Driven Development to execute this plan.

[Load plan, create TodoWrite]

Task 1: Hook installation script

[Draft prompt, vet with agent]
Agent: Prompt has enough detail, ready to execute.

[Dispatch implementation subagent]
Subagent: Implemented install-hook with tests, 5/5 passing

[Get git SHAs, dispatch code-reviewer]
Reviewer: Strengths: Good test coverage. Issues: None. Ready.

[Mark Task 1 complete]

Task 2: Recovery modes

[Draft prompt, vet with agent]
Agent: Need expected telemetry format before starting.

[Revise prompt with telemetry details, reconfirm readiness]
Agent: Ready now.

[Dispatch implementation subagent]
Subagent: Added verify/repair, 8/8 tests passing

[Dispatch code-reviewer]
Reviewer: Strengths: Solid. Issues (Important): Missing progress reporting

[Dispatch fix subagent]
Fix subagent: Added progress every 100 conversations

[Re-dispatch code-reviewer to verify fix]
Reviewer: Issue resolved, progress reporting now working. No remaining issues.

[Mark Task 2 complete]

...

[After all tasks]
[Dispatch final code-reviewer]
Final reviewer: All requirements met, ready to merge

Done!
```

## Advantages

**vs. Manual execution:**
- Subagents follow TDD naturally
- Fresh context per task (no confusion)
- Parallel-safe (subagents don't interfere)

**vs. Executing Plans:**
- Same session (no handoff)
- Continuous progress (no waiting)
- Review checkpoints automatic

**Cost:**
- More subagent invocations
- But catches issues early (cheaper than debugging later)

## Red Flags

**Never:**
- Skip code review between tasks
- Skip re-reviewing after fixes are applied
- Skip prompt vetting (dispatch without agent sign-off)
- Trust fix subagent reports without code-reviewer verification
- Proceed with unfixed Critical issues
- Mark task complete while code-reviewer issues remain
- Dispatch multiple implementation subagents in parallel (conflicts)
- Implement without reading plan task

**If subagent fails task:**
- Dispatch fix subagent with specific instructions
- Don't try to fix manually (context pollution)

## Integration

**Required workflow skills:**
- **writing-plans** - REQUIRED: Creates the plan that this skill executes
- **requesting-code-review** - REQUIRED: Review after each task (see Step 3)
- **finishing-a-development-branch** - REQUIRED: Complete development after all tasks (see Step 7)

**Subagents must use:**
- **test-driven-development** - Subagents follow TDD for each task

**Alternative workflow:**
- **executing-plans** - Use for parallel session instead of same-session execution

See code-reviewer template: requesting-code-review/code-reviewer.md
