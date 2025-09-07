# IMPLEMENTATION MODE Detailed Requirements

## Modal Entry Protocol
**ENTRY CRITERIA**:
- [ ] **Approved Plan**: Complete implementation plan from ANALYSIS MODE
- [ ] **Feature Branch**: Create feature branch: `git checkout -b feature/task-description`
- [ ] **Task Tracking**: TodoWrite task created with clear acceptance criteria
- [ ] **MODE DECLARATION**: "ENTERING IMPLEMENTATION MODE: [approved plan summary]"

## Core Constraints & Execution Framework
**🚨 PRIMARY CONSTRAINT**: **Follow approved plan precisely** - no exploratory changes or scope expansion.

**PRIMARY TOOLS**:
- `Write`, `Edit`, `MultiEdit` for planned code changes
- `mcp__serena__replace_symbol_body`, `mcp__serena__insert_operations` for precise code modifications
- `mcp__metis__execute_sage_code` for computational implementations
- File operations and system commands as needed

## Implementation Discipline Protocol

**ATOMIC SCOPE ENFORCEMENT**:
- **Single Logical Change**: Maintain focus on one clear objective per implementation cycle
- **No Feature Creep**: If additional requirements discovered → **RETURN TO ANALYSIS MODE**
- **Plan Validation**: If approved plan proves flawed during execution → **MUST RETURN TO ANALYSIS MODE**

**Quality Integration Requirements**:
- Apply project coding standards and naming conventions
- Follow established architectural patterns
- Update code comments and documentation as implemented
- Ensure changes integrate cleanly with existing codebase

## Workflow Integration Protocol

**CHECKPOINT A: TASK INITIATION** (Already completed before entering mode)
**CHECKPOINT B: IMPLEMENTATION COMPLETE** (MANDATORY before exit):
- [ ] All planned file operations complete per approved plan
- [ ] Scope integrity maintained (no scope creep detected)
- [ ] Code quality standards applied throughout implementation
- [ ] All tests pass: `[run project test command]`
- [ ] Type checking clean: `[run project typecheck command]`  
- [ ] Linting satisfied: `[run project lint command]`
- [ ] Code formatting applied: `[run project format command]`

## Agent Delegation During Implementation

**When to Delegate**:
- **Complex domain-specific logic**: Use specialist agents for their expertise areas
- **Quality assurance**: Mandatory delegation to test-specialist after new functionality
- **Security considerations**: Required security-engineer review for user input or sensitive data

**Handoff Protocol**:
- Provide clear context about current implementation state
- Specify exact scope of specialist work needed
- Ensure specialist has access to approved plan and requirements

## Error Handling & Recovery

**Implementation Errors**:
- **Syntax/Logic errors**: Fix immediately within approved scope
- **Test failures**: Address within current implementation scope
- **Plan inadequacy discovered**: **STOP** → Return to ANALYSIS MODE for plan revision

**Scope Expansion Triggers**:
- Additional requirements discovered during implementation
- Original plan proves technically infeasible
- Dependencies not identified in analysis phase

## Exit Criteria & Transition Protocol

**IMPLEMENTATION MODE EXIT REQUIREMENTS**:
- [ ] All planned file operations complete
- [ ] All quality gates pass (Checkpoint B completed)
- [ ] Atomic scope maintained throughout execution
- [ ] No unresolved implementation issues
- [ ] **MODE TRANSITION**: "EXITING IMPLEMENTATION MODE → REVIEW MODE: [validation scope]"