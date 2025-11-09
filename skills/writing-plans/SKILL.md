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

## Task List Structure

For each task:
- Use `### Task N: <scope>` as the heading.
- Provide a two-to-three sentence objective that states the user impact, critical acceptance criteria, and testing expectations.
- Call out dependencies (e.g., "Depends on Task 1 tracer logging").
- Generate a prompt using the `writing-tasks` skill, and reference the prompt here:
  ```
  Task Prompt: docs/tasks/<date>-<feature>-task-<n>.md
  ```
- Mention the preferred execution agent (general-purpose by default; include role guidance if the task will need it).

Keep tasks bite-sized, and independent where possible so agents can work in parallel worktrees.

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
2. Add a short "Next Steps" section:
   - "Confirm task briefs exist or schedule time to write them."
   - "Decide execution mode (subagent-driven vs executing-plans)."
3. Save the plan to `docs/plans/…` and note it in the session scratchpad.
4. Offer the execution options, reminding that subagent-driven development expects the plan plus task briefs.

A solid plan is composable, review-backed, and easy for agents (or humans) to follow without improvising. Optimize for clarity and correctness—future contributors should thank you for how little they have to guess.
