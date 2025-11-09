---
name: writing-plans
description: Use when design is approved and you need a modular, TDD-friendly implementation plan that an agent can execute task-by-task after review
---

# Writing Plans

## Overview

Translate a validated design into an execution-ready plan that balances speed with longevity. Plans list the minimal set of bite-sized tasks required to hit the goal without cutting quality corners: correct algorithms and data structures, maintainable abstractions, test-first mindset. Every task should be bite-sized for a focused agent to use, but the prompt should provide enough context to work independently or in parallel workspaces.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Prerequisites

- Brainstorming skill completed; design decisions are stable.
- Discovery notes and consultation transcripts available (link them in the plan for traceability).
- Worktree prepared if execution will follow immediately.

## Align on Constraints & Signals

1. Summarize critical constraints from brainstorming: goals, success metrics, rollout risks.
2. Identify architecture or stack preferences that surfaced during consultations.
3. Note opportunities for tracer bullet/MVP delivery and possible parallel work streams.

If new gaps appear, revisit `consulting-agents` before drafting tasks.

## Plan Skeleton

Every plan starts with this header (update placeholders):

```markdown
# <Feature Name> Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use subagent-driven-development to execute this plan task-by-task.

**Goal:** <Single sentence outcome>

**Architecture:** <2-3 sentences describing the selected approach and why>

**Tech Stack:** <Key frameworks, storage layers, tooling>

---
```

Follow with sections for global considerations (migrations, rollout toggles, monitoring) before listing tasks.

## Task List Structure - MANDATORY WORKFLOW

**CRITICAL:** For EACH task, you MUST follow this sequence:

1. Write task objective (2-3 sentences with user impact, acceptance criteria, testing)
2. List dependencies (e.g., "Depends on Task 1 tracer logging")
3. **IMMEDIATELY** use `writing-tasks` skill to generate the prompt file
4. Reference the generated prompt: `Task Prompt: docs/tasks/<date>-<feature>-task-<n>.md`
5. Mention preferred execution agent (general-purpose by default; include role guidance if needed)
6. Move to next task

**DO NOT:**
- Write all task objectives first, then generate prompts later
- Defer prompt generation as "optional follow-up work"
- Reference prompts that don't exist yet
- Skip prompt generation and mark it as "TODO"

**If you find yourself with task descriptions but no prompt files, STOP - you're doing it wrong.**

Keep tasks bite-sized (see guidelines below), and independent where possible so agents can work in parallel worktrees.

## Task Size Guidelines (Prevent Mega-Tasks)

A properly-sized task should:
- Modify 1-3 closely related files (not 5+ files across subsystems)
- Take 30-90 minutes for focused implementation
- Have ONE primary objective (not "integrate all X")
- Be independently testable without other tasks
- Fit in ~300 lines of implementation code

**RED FLAGS - Task is too large if it:**
- Uses "all" or "each" ("modify all generators", "update each component")
- Lists 5+ files to modify
- Has multiple sub-bullets in objective
- Would take >2 hours to implement
- Requires touching multiple architectural layers

**When you detect a mega-task:**
1. STOP immediately
2. Break into separate tasks (one per file/component/generator)
3. Update dependencies between new tasks
4. Generate separate prompt for each
5. Update task numbering and tracer bullet if needed

## Modularity, Extensibility, and TDD Checks

After drafting the tasks, run a quick audit:
- **Tracer bullet first:** Does the plan deliver a vertical slice early?
- **Parallel lanes:** Are there at least two tasks that can proceed concurrently without merge conflicts?
- **Flexibility:** Are extension points (configuration, interfaces, contracts) documented, not hard-coded?
- **Testing:** Does every task specify the tests to add/run, including integration, smoke, or regression coverage as appropriate?
- **Quality guardrails:** Highlight any performance caps, security constraints, or data-retention rules that must stay intact.

Update task objectives if any of these checks fail.

## Agent Review Gate

Before finalizing, request critique from a general-purpose agent with an explicit role prompt tailored to the domain:

```
Role: Staff Platform Architect focused on maintainability, modular growth, and test discipline.
Task: Review this implementation plan (link) for:
- Modular breakdown that supports parallel execution
- Adequate tracer bullet coverage before expansions
- TDD alignment (tests per task, verification path)
- Risks of over/under-engineering given project scope
Provide blocking issues, improvement ideas, and confirm if the plan is ready.
```

Iterate up to three times using the Task Prompt Iteration Protocol until the reviewer confirms the plan meets the criteria. Capture their feedback and the final approval note at the end of the plan document.

## Finalize & Handoff

1. Ensure all tasks reference their prompts generated via (`writing-tasks`).

2. **Create task issues in beads (bd):**

   If project uses beads (check for AGENTS.md or epic already created), create bd issues for all tasks using the two-phase pattern:

   ```bash
   # Phase 1: Create all task issues, capture IDs
   task1_id=$(bd create "Task 1: <scope>" --parent <epic-id> --json | jq -r '.id')
   task2_id=$(bd create "Task 2: <scope>" --parent <epic-id> --json | jq -r '.id')
   task3_id=$(bd create "Task 3: <scope>" --parent <epic-id> --json | jq -r '.id')
   # ... for all N tasks

   # Phase 2: Wire dependencies
   bd dep add "$task2_id" "$task1_id"  # Task 2 depends on Task 1
   bd dep add "$task5_id" "$task1_id"  # Task 5 depends on Task 1
   bd dep add "$task5_id" "$task3_id"  # Task 5 depends on Task 3
   # ... for all dependencies documented in plan
   ```

   Then update plan with bd issue IDs:
   ```markdown
   ### Task N: <scope>
   **Beads Issue:** <issue-id>
   **Task Prompt:** docs/tasks/...
   ```

   Verify all tasks linked: `bd list --parent <epic-id>`

3. Add a short "Next Steps" section:
   - "All task prompts generated and bd issues created"
   - "Decide execution mode (subagent-driven vs executing-plans)"

4. Save the plan to `docs/plans/…` and note it in the session scratchpad.

5. Offer the execution options, reminding that subagent-driven development expects the plan plus task briefs.

A solid plan is composable, review-backed, and easy for agents (or humans) to follow without improvising. Optimize for clarity and correctness—future contributors should thank you for how little they have to guess.
