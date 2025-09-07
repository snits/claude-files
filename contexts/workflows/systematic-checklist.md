# Systematic Tool Utilization Checklist

## MANDATORY PRE-TASK CHECKLIST
**BEFORE starting ANY complex task, complete this checklist in sequence:**

## 0. Solution Already Exists? (DRY/YAGNI Applied to Problem-Solving)
- [ ] **Web search**: Find existing solutions, tools, or libraries that solve this problem
- [ ] **Project documentation**: Check 00-project/, 01-architecture/, 05-process/ for existing solutions  
- [ ] **Journal search**: `mcp__private-journal__search_journal` for prior solutions to similar problems
- [ ] **Codebase analysis**: Use serena MCP tools (`mcp__serena__get_symbols_overview`) to find existing patterns
- [ ] **Best practices research**: Verify established libraries/tools aren't handling this requirement

## 1. Context Gathering (Before Any Implementation)
- [ ] **Domain knowledge**: `mcp__private-journal__search_journal` with relevant terms
- [ ] **Structural understanding**: Serena codebase analysis for architecture comprehension
- [ ] **Documentation review**: Related architectural decisions and prior established patterns

## 2. Problem Decomposition (For Complex Tasks)
**POWERFUL MCP ANALYSIS TOOLS** - Use systematic investigation:
- [ ] **Deep analysis**: `mcp__zen__thinkdeep` for multi-step investigation with expert validation
- [ ] **Systematic debugging**: `mcp__zen__debug` for complex issues requiring root cause analysis  
- [ ] **Collaborative thinking**: `mcp__zen__chat` to brainstorm approaches and validate thinking
- [ ] **Strategic planning**: `mcp__zen__planner` for complex system design and migration strategies
- [ ] **Multi-model consensus**: `mcp__zen__consensus` for critical decisions requiring expert agreement
- [ ] **Break into atomic increments**: Reviewable, testable chunks with clear boundaries

## 3. Domain Expertise (When Specialized Knowledge Required)
- [ ] **Agent delegation**: Use Task tool with appropriate specialist agent for domain expertise
- [ ] **Context provision**: Ensure agent has access to context from steps 0-2
- [ ] **Mathematical modeling**: Use metis MCP tools for computational problems requiring mathematical analysis

## 4. Task Coordination (All Tasks)
- [ ] **TodoWrite**: Clear scope and acceptance criteria with atomic boundaries
- [ ] **Link insights**: Connect to context gathering and problem decomposition findings
- [ ] **Scope verification**: Confirm task represents single logical change

## 5. Implementation (Only After Steps 0-4 Complete)
- [ ] **Execute systematically**: File operations, git, bash as needed following approved plan
- [ ] **EXPLICIT CONFIRMATION**: "I have completed Systematic Tool Utilization Checklist and am ready to begin implementation"

## Core Principles Integration

**Safety First**: Never execute destructive commands without confirmation. Explain all system-modifying commands.
**Follow Project Conventions**: Existing code style and patterns are the authority for implementation decisions.
**Smallest Viable Change**: Make minimal, targeted changes to accomplish the goal without scope expansion.
**Find Root Cause**: Never fix symptoms without understanding the underlying issue causing them.
**Test Everything**: All changes must be validated by tests, preferably following TDD methodology.

## Scope Discipline Protocol

**When discovering additional issues during implementation**:
1. **STOP reactive fixing** - Don't fall into "whack-a-mole" mode
2. **Root Cause Analysis**: Identify underlying issue causing symptoms
3. **Scope Assessment**: Determine if same logical problem or different issue
4. **Plan Real Fix**: Address root cause systematically, not individual symptoms
5. **Implement Systematically**: Complete planned solution with proper validation