# Tiered Parallel Pipeline Architecture

1. **Task Selection**: Open `docs/00-project/TODO.md` and select the first unchecked actionable task in the todo list to work on. An actionable task is the most granular, concrete item that has no further sub-tasks beneath it (a true leaf node with no children). Always traverse down through all nested levels to find the deepest unchecked item that represents actual work to be done, not a category or grouping. Parent node items should only be marked as complete when all of the descendant node items are marked complete.

After reading the task assess whether or not the task should be decomposed into multiple sub-tasks, or if it can reasonably be completed by an agent without running into context window issues. If yes, update `docs/00-project/TODO.md` with these new sub-tasks, and complete the rest of these steps with the first of those sub-tasks.

2. **Automated Setup Phase** - Using ToDoWrite create a list that includes the following steps:

   ## **TIER 1: Agent Selection & Context Preparation** *(Sequential - Foundation Layer)*

   - **Thoughtful Agent Selection**: Determine the most domain-relevant agent by:
     - Analyzing the specific task requirements and domain
     - Reviewing what agents are actually available to the current project
     - Considering the agent's expertise match to the task needs
     - Prioritizing technical implementation and domain expert agents for code changes
     - Prioritizing architectural agents for design decisions
     - Prioritizing security-auditor for security concerns
     - Prioritizing test-specialist for testing tasks
     - **SCOPE DISCIPLINE**: Keeping in mind project scope, goals, and end use-case - include PROJECT SCALE CONTEXT in agent prompt
     - **COMPLEXITY BUDGET**: Include DRY/YAGNI principles and complexity constraints in agent prompt
     - Read existing prompt from `docs/00-project/task-prompts/` or create new one if missing

   - **Context Research**: Research whether existing technology/libraries solve this task (web-search-researcher for external solutions, codebase-pattern-finder for existing patterns). **Persistent Output Requirement:** - A markdown report summarizing the research should be created to document what was found for future reference.

   - **Iterative Prompt Refinement**: Task selected agent to validate prompt sufficiency with requirements:
     - Walk through thought process step-by-step
     - Request any missing information needed
     - **Up to 3 iterations maximum** - refine prompt based on feedback, gathering improvement suggestions
     - Stop early if agent confirms prompt is sufficient
     - Update finalized prompt in `docs/00-project/task-prompts/`

   ## **TIER 2: Implementation Execution** *(Sequential - Critical Path)*

   - **Primary Implementation**: Task agent selected with completing the todo item using finalized prompt. Include project scale context and YAGNI/DRY constraints in task prompt. Agent must use the `mcp__zen__precommit` tool prior to completion if code changes involved.

   - **Quality Gates & Commit**: Execute all type checking, linting, formatting, and testing gates. Use get-agent-hash for agent attribution. Commit changes only after all gates pass.

   ## **TIER 3: Quality Review** *(Quality Assurance Layer)*

      - **SCOPE DISCIPLINE**: Keeping in mind project scope, goals, and end use-case - include PROJECT SCALE CONTEXT in agent prompt
      - **Persistent Output Requirement:** - code-reviewer agent must create a document recording their findings and reference that document when they report back via the Task tool.
      - **Adversarial:** While not being rude, the reviewer should take a challenging/adversarial viewpoint when reviewing completed work as part of a quality review in order to ensure work is of the highest quality.

   ```
   // Core Quality Review (Always Execute)
   ├── code-reviewer (using `mcp__zen__codereview`) → Comprehensive quality gates analysis
   ```

   **Review Consolidation Rules**:
   - Task project-orchestrator to assess scope of, properly prioritize, and add tasks to `docs/00-project/TODO.md` for any issues raised (avoid duplicates). Include PROJECT SCALE CONTEXT when tasking project-orchestrator.
   - Consolidate similar findings across the three core reviewers

   ## **TIER 4: Human Approval Gate** *(Sequential - Final Validation)*

   - **Jerry Approval**: Get approval from Jerry to move forward with the completed implementation and quality reviews.

3. **Execution Phase**: Carry out the steps in the ToDoWrite list using the Tiered Parallel Pipeline:
   - Execute TIER 1 sequentially (foundation must be solid)
   - Execute TIER 2 sequentially (implementation is critical path)
   - Execute TIER 3 review sequentially
   - Execute TIER 4 approval gate (human validation checkpoint)

4. **Scope & Complexity Validation**: Assess whether any tasks added to `docs/00-project/TODO.md` are appropriate for the project context:
   - **Scope Alignment**: Tasks must align with project goals, scope, and end use-case (refer to `docs/00-project/plan.md`)
   - **Solution Complexity Matching**: Engineering practices and architectural patterns must match project type:
     - Simple tools/games: Avoid enterprise patterns, prefer straightforward solutions
     - Developer utilities: Focus on usability over complex abstractions
     - Enterprise systems: Apply appropriate scaling patterns and robust error handling
     - Libraries/frameworks: Design for extensibility and maintainability
   - **Architectural Appropriateness**: Solution complexity should match actual requirements, not impose unnecessary patterns or over-engineering

5. **Task Completion**: Check off the item in `docs/00-project/TODO.md` when it is completed. Items with children, should only be marked complete when all items nested below them are marked complete.

---

## **Implementation Notes**

### **Automation Fallbacks**

- If agent selection is unclear, use codebase-analyzer for task analysis
- If code-reviewer using `mcp__zen__codereview` fails, retry once before proceeding

### **Performance Optimizations**

- Consolidate similar review findings to avoid duplicate tasks

### **Quality Assurance**

- `mcp__zen__precommit` tool validation required before any commits
- **Human approval gate (Jerry) required after all quality reviews complete**
