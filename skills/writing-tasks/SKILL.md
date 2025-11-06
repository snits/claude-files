---
name: writing-tasks
description: Use after the plan is outlined to author detailed task briefs with TDD-first steps, role prompts, and verification notes for execution agents
---

# Writing Task Briefs

## Overview

Take each task from the implementation plan and expand it into an actionable brief that a subagent can execute without guessing. Briefs live alongside the plan, capture exact commands, and embed role prompts when a focused mindset is required.

**Announce at start:** "I'm using the writing-tasks skill to draft the task briefs."

**Save briefs to:** `docs/tasks/YYYY-MM-DD-<feature>-task-<n>.md`

## Inputs You Need

- The implementation plan (`writing-plans` output) with task summaries and dependencies.
- Discovery notes, code references, and architecture decisions linked in the plan.
- Any existing code or tests relevant to the task (open tabs/links ready).

If key information is missing, loop back to `writing-plans` or `consulting-agents` before drafting.

## Task Brief Template

Start from this structure:

```markdown
# Task <N>: <Scope Summary>

**Goal:** <Outcome and user impact>
**Dependencies:** <Link to prerequisite tasks or sections>  
**Related Docs:** <Links to design notes, specs, ADRs>

## Execution Context
- Working directory: `<path>`
- Branch expectations: `<branch or worktree info>`
- Feature flags / configs touched: `<list>`

## Steps (TDD cadence)
1. **Write failing test:** <file path, snippet, command to run failing test>
2. **Run tests (expect fail):** `<command>` → `<expected failure>`
3. **Implement minimal code:** <files, functions, specific patterns/algorithms>
4. **Run tests (expect pass):** `<command>` → `<expected success>`
5. **Additional verification:** <linters, integration checks, manual QA>
6. **Commit guidance:** `<git add/commit message template>`

## Deliverables
- Updated files: `<list>`
- New files: `<list>`
- Tests added/modified: `<list>`

## Execution Agent Role (optional)
Role: <If execution benefits from a perspective, define it here using the Dynamic Role Prompt Composer. Otherwise state "General-purpose agent.">

## Reporting Expectations
- Include command output summaries
- Call out follow-up work or open questions
```

Keep steps atomic (2-5 minutes each) and include concrete code snippets or scaffolding when ambiguity might arise.

## Drafting Workflow

1. **Re-state the Objective:** Translate the plan’s task summary into a succinct Goal line that highlights user impact and acceptance criteria.
2. **List Dependencies:** Reference earlier tasks or shared components so the executor verifies prerequisites before starting.
3. **Design the TDD Loop:** For each behavior, specify the exact test file, test name, or spec to edit. Include code skeletons or assertions when helpful.
4. **Detail Implementation Notes:** Spell out algorithm choices, data structures, or library APIs that must be used (or avoided) to balance correctness and pragmatism.
5. **Capture Observability & Rollback Hooks:** Mention logging, metrics, migrations, or feature flags that support safe rollout.
6. **Describe Verification:** Beyond automated tests, call out smoke checks, manual QA, documentation updates, or migration verification steps.
7. **Define the Agent Role (if needed):** When the executor needs a precise mindset—security, performance, UX—add a Role block in the brief using the same formula as `consulting-agents` (seniority + domain + mandate).

## Review Loop

Before publishing the brief, have a general-purpose agent review it:

```
Role: Senior QA-minded Tech Lead ensuring task briefs are executable and test-first.
Task: Review Task <N> brief. Confirm:
- Steps follow TDD (fail first, pass second, regression checks)
- Scope is bite-sized and independent
- Role guidance (if present) is clear and justified
- Commands, file paths, and acceptance criteria are complete
List required fixes and optional improvements.
```

Iterate up to three times, updating the brief after each round. Record the final approval summary at the end of the brief (`## Reviewer Sign-off`).

## Final Hooks

- Link each brief back in the implementation plan (under its task entry).
- Update the plan’s “Next Steps” or scratchpad with the path to each brief.
- If execution will proceed now, queue the tasks in TodoWrite using the same titles and brief links.

Great task briefs make execution predictable—future agents should be able to land the change, write tests, and ship without improvisation.
