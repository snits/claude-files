---
name: writing-plans
description: Use when design is complete and you need detailed implementation tasks validated by domain experts - consults specialists (database, architecture, security, performance, etc.) to validate technical approach, then creates comprehensive implementation plans with exact file paths, complete code examples, and verification steps
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Discovery Phase (Before Writing Tasks)

**Consult agents to ground the plan in reality:**

See `consultants:consulting-agents` for full protocol.

**Discovery agents - Find what exists:**
- Locate relevant files and components for this feature
- Find similar implementations to reference
- Identify existing patterns to follow

**Domain experts - Understand constraints:**
- Security considerations that affect design
- Performance requirements or bottlenecks
- UX patterns or user expectations
- Other domain-specific concerns

**Why:** Plans with zero context about what exists or what matters produce generic tasks. Agent consultation gives you specifics: actual file paths, proven patterns, real constraints.

**Output:** Agents write findings to scratchpad. Read their reports before drafting tasks.

## Task Validation with Domain Specialists (Before Finalizing Plan)

**After discovery, before writing detailed tasks:**

**When specialist validation is needed:**
- Database schema changes, migrations, or query optimization
- Async processing, pipelines, or distributed systems
- Security-sensitive code (auth, payments, PII handling, API keys)
- Performance-critical paths (high-traffic APIs, real-time processing)
- Complex architecture changes (new patterns, major refactors)
- Non-trivial testing strategy

**When you can skip specialist validation:**
- Straightforward cleanup (deleting files, removing dead code)
- Simple CRUD operations following existing patterns
- Obvious bug fixes with clear solutions
- Documentation-only changes

**If skipping:** Briefly explain why (e.g., "This is cleanup work with no technical decisions to validate").

**If needed:** For each major task in the plan, validate the approach with the appropriate domain specialist.

**1. Identify the right specialist:**

Review the Task tool's available agent types to find the appropriate domain specialist. Match the task domain to agent expertise:
- Security-sensitive code → security specialist
- Performance-critical paths → performance specialist
- User-facing features → UX specialist
- Complex architecture → architecture specialist
- Testing strategy → test specialist
- API design → API design specialist

The Task tool's agent descriptions tell you when to use each agent.

**2. Draft initial task prompt:**

Create a task description with:
- What needs to be built
- Why it's needed
- Key constraints (DRY, YAGNI, project scale context)
- Files that will be touched (from discovery)
- Patterns to follow (from codebase-pattern-finder)

**3. Iterative refinement with specialist (up to 3 iterations):**

Task the specialist agent to validate the approach:

```
"Review this task prompt and validate the approach:

[Task prompt]

Please:
1. Walk through how you would implement this
2. Identify any missing context or unclear requirements
3. Flag potential issues or concerns
4. Suggest improvements to the approach

I'm writing a detailed implementation plan and want to ensure the task is well-scoped before writing specific steps."
```

**Refinement process:**
- Iteration 1: Get specialist feedback, identify gaps
- Iteration 2: Refine prompt based on feedback, get validation
- Iteration 3: Final refinement if needed
- Stop early if specialist confirms approach is sound

**4. Incorporate specialist feedback:**

Update task prompt with:
- Specialist-recommended approach
- Security/performance/UX considerations they raised
- Any additional steps or validations they identified

**5. Write detailed implementation steps:**

Now write the bite-sized steps with exact code, incorporating the specialist-validated approach.

**Why this matters:** Specialists shape WHAT gets built (architecture, security patterns, performance considerations) during planning. The detailed steps tell HOW to build it (exact code, commands, commits). This shifts quality left while keeping execution precise.

**Output:** Task prompts validated by domain experts, ready for detailed step-by-step expansion.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

```markdown
### Task N: [Component Name]

**Subagent to Task:** [subagent that will be tasked to complete task or general-purpose if you plan to task general-purpose]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -s -m "feat: add specific feature"
```
Commit message should contain: `Co-authored-by: Claude <no-reply@anthropic.com>`
If agents involved Commit message should contain
for each agent: `Assisted-by: [agent-name (general-purpose if general-purpose used, otherwise subagent name)] ([model])`
```

## Remember
- Exact file paths always
- Complete code in plan (not "add validation")
- Exact commands with expected output
- Reference relevant skills with @ syntax
- DRY, YAGNI, TDD, frequent commits

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `docs/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?"**

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use subagent-driven-development
- Stay in this session
- Fresh subagent per task + code review

**If Parallel Session chosen:**
- Guide them to open new session in worktree
- **REQUIRED SUB-SKILL:** New session uses superpowers:executing-plans
