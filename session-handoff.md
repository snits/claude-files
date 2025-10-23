# Session Handoff: Add NIH Evaluation to Brainstorming Skill

**Date:** 2025-10-22
**Task:** Update `skills/brainstorming/SKILL.md` to add NIH (Not Invented Here) evaluation step

## The Idea

Before we start designing solutions (current Phase 1.5: Premise Validation), we should first check if a solution already exists that meets our needs. We shouldn't reinvent the wheel.

## Where It Goes

**Current flow:**
- Phase 1: Understanding (gather requirements)
- Phase 1.5: Premise Validation (validate with domain experts)
- Phase 2: Exploration (propose approaches)

**Proposed flow:**
- Phase 1: Understanding (gather requirements)
- **Phase 1.5: NIH Evaluation (check if solution already exists)**
- Phase 2: Premise Validation (if building, validate the premise)
- Phase 3: Exploration (propose approaches)

This means current Phase 1.5 becomes Phase 2, and everything shifts down one number.

## Implementation Approach

Use `web-search-researcher` agents to:
1. Search for existing solutions/libraries/tools that solve the problem
2. Evaluate if they meet our needs
3. If yes: use existing solution, skip to integration design
4. If no: proceed to premise validation and custom implementation

## Why This Matters

We've probably built things that already exist as mature libraries. This step forces us to check before committing to custom development.

## Process Requirements

Per `skills/writing-skills/SKILL.md`, we MUST follow RED-GREEN-REFACTOR:

### RED Phase (Baseline Testing)
- Create pressure scenarios where agent is asked to build something
- Run WITHOUT the NIH evaluation step
- Document: Do agents naturally check for existing solutions?
- Capture rationalizations for skipping the search
- Expected result: Agents jump straight to building custom solutions

### GREEN Phase (Write Skill)
- Add NIH evaluation step to brainstorming skill
- Address specific baseline failures identified in RED
- Run same scenarios WITH updated skill
- Verify: Agents now check for existing solutions first

### REFACTOR Phase (Close Loopholes)
- Identify any new rationalizations for skipping NIH check
- Add explicit counters (e.g., "it's faster to build" → NO, evaluating is faster)
- Build rationalization table
- Re-test until bulletproof

## Key Questions for Implementation

1. **When to skip NIH check?**
   - Truly novel features only we need
   - Internal tooling specific to our workflows
   - What else?

2. **How thorough should the search be?**
   - Just check npm/PyPI?
   - Include GitHub/GitLab projects?
   - Check Stack Overflow patterns?

3. **Evaluation criteria?**
   - Maintained (recent commits)?
   - Popular (usage stats)?
   - License compatible?
   - API quality?

## Files to Reference

- `/home/jsnitsel/.claude/skills/brainstorming/SKILL.md` - Current skill
- Skill tool's `<available_skills>` - Check for `web-search-researcher`
- `/home/jsnitsel/.claude/skills/writing-skills/SKILL.md` - TDD process for skills

## Starting Point Tomorrow

1. Read this handoff
2. Use `superpowers:writing-skills` skill
3. Follow RED-GREEN-REFACTOR cycle
4. Test with subagents before editing the skill

---

**Notes for tomorrow's Claude:**
- Jerry explicitly wants proper TDD process, not quick edits
- This is a discipline-enforcing change (agents must check before building)
- Expect rationalizations like "I know there's nothing out there" or "faster to build ourselves"
- The NIH check should use web-search-researcher agents, not manual searches
