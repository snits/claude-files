# Tiered Parallel Pipeline Architecture

1. **Task Selection**: Open `docs/00-project/TODO.md` and select the first unchecked actionable task in the todo list to work on. An actionable task is the most granular, concrete item that has no further sub-tasks beneath it (a true leaf node with no children). Always traverse down through all nested levels to find the deepest unchecked item that represents actual work to be done, not a category or grouping. Parent node items should only be marked as complete when all of the descendant node items are marked complete.

2. **Automated Setup Phase** - Using ToDoWrite create a list that includes the following steps:

   ## **TIER 1: Agent Selection & Context Preparation** *(Sequential - Foundation Layer)*

   - **Thoughtful Agent Selection**: Determine the most domain-relevant agent by:
     - Analyzing the specific task requirements and domain
     - Reviewing what agents are actually available to the current project
     - Considering the agent's expertise match to the task needs
     - Prioritizing technical implementation and domain expert agents for code changes
     - Prioritizing architectural agents for design decisions
     - Prioritizing security-engineer for security concerns
     - Prioritizing test-specialist for testing tasks
     - Keeping in mind project scope, goals, and end use-case
     - Read existing prompt from `docs/00-project/tdd-prompts/` or create new one if missing

   - **Context Research**: Research whether existing technology/libraries solve this task (search-specialist for discovery)

   - **Single-Round Prompt Validation**: Task selected agent to validate prompt sufficiency with requirements:
     - Walk through thought process step-by-step
     - Request any missing information needed
     - **One iteration only** - refine prompt immediately based on feedback, then proceed
     - Update finalized prompt in `docs/00-project/tdd-prompts/`

   ## **TIER 2: Implementation Execution** *(Sequential - Critical Path)*

   - **Primary Implementation**: Task agent selected with completing the todo item using finalized prompt. Agent must use the `mcp__zen__precommit` tool prior to completion if code changes involved.

   - **Quality Gates & Commit**: Execute all type checking, linting, formatting, and testing gates. Use get-agent-hash for agent attribution. Commit changes only after all gates pass.

   ## **TIER 3: Parallel Quality Review** *(Parallel - Quality Assurance Layer)*

   **⚡ PARALLEL EXECUTION BLOCK** *(All reviews execute simultaneously)*

   ```
   // Core Quality Reviews (Always Execute)
   ├── code-reviewer (using `mcp__zen__codereview`) → Comprehensive quality gates analysis
   ├── security-engineer → Security impact assessment
   └── test-specialist → Testing coverage validation

   // Specialized Reviews (Execute Based on Change Type)
   ├── clean-code-analyst → Code structure review (if code changes)
   ├── solid-principles-assessor → SOLID compliance (if code changes)
   ├── architectural-patterns-expert → Pattern compliance (if design changes)
   ├── maintainability-assessor → Long-term maintainability (if complex changes)
   ├── api-design-expert → API design review (if interface changes)
   └── documentation-assessor → Documentation review (if docs changed)
   ```

   **Review Consolidation Rules**:
   - If code-reviewer using `mcp__zen__codereview` identifies issues covered by specialist reviews, skip the corresponding specialist review. This requires the `mcp__zen__codereview` tool use to tag findings with the relevant domain (e.g., `[api-design]`, `[security]`).
   - Add tasks to `docs/00-project/TODO.md` for any issues raised (avoid duplicates)

   **Automated Review Selection**: Determine which specialist reviews to include:
   - **Code changes** → clean-code-analyst, solid-principles-assessor, maintainability-assessor
   - **API/Interface changes** → api-design-expert
   - **Architecture changes** → architectural-patterns-expert
   - **Documentation changes** → documentation-assessor
   - **All changes** → code-reviewer (using `mcp__zen__codereview`), security-engineer, test-specialist (always execute)

   ## **TIER 4: Human Approval Gate** *(Sequential - Final Validation)*

   - **Jerry Approval**: Get approval from Jerry to move forward with the completed implementation and quality reviews.

3. **Execution Phase**: Carry out the steps in the ToDoWrite list using the Tiered Parallel Pipeline:
   - Execute TIER 1 sequentially (foundation must be solid)
   - Execute TIER 2 sequentially (implementation is critical path)
   - Execute TIER 3 reviews in parallel (quality assurance can be parallelized)
   - Wait for all TIER 3 reviews to complete before proceeding
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

### **Parallel Execution Guidelines**

- Use separate Tool calls for each parallel review in TIER 3
- Batch similar reviews where possible (e.g., multiple code quality reviews)
- Collect all parallel results before moving to next phase

### **Automation Fallbacks**

- If agent selection is unclear, use search-specialist for task analysis
- If code-reviewer using `mcp__zen__codereview` fails, fall back to individual specialist reviews
- If parallel reviews conflict, prioritize security-engineer > code-reviewer (using `mcp__zen__codereview`) > specialists

### **Performance Optimizations**

- Skip redundant specialist reviews when code-reviewer using `mcp__zen__codereview` covers the same areas
- Consolidate similar review findings to avoid duplicate tasks

### **Quality Assurance**

- All TIER 3 reviews must complete successfully before proceeding to TIER 4
- Security-engineer approval is mandatory for all code changes
- `mcp__zen__precommit` tool validation required before any commits
- **Human approval gate (Jerry) required after all quality reviews complete**
