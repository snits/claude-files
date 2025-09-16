## Workflow Integration

### MANDATORY WORKFLOW CHECKPOINTS
These checkpoints MUST be completed in sequence. Failure to complete any checkpoint blocks progression to the next stage.

**TESTING METHODOLOGY INTEGRATION**: These checkpoints support all testing methodologies (TDD, discovery testing, integration-first, etc.). The key is ensuring quality gates are met regardless of methodology approach.

### Checkpoint A: TASK INITIATION
**BEFORE starting ANY coding task:**
- [ ] Systematic Tool Utilization Checklist completed (steps 0-5: Solution exists?, Context gathering, Problem decomposition, Domain expertise, Task coordination)
- [ ] Git status is clean (no uncommitted changes) 
- [ ] Create feature branch: `git checkout -b feature/task-description`
- [ ] Confirm task scope is atomic (single logical change)
- [ ] TodoWrite task created with clear acceptance criteria
- [ ] **EXPLICIT CONFIRMATION**: "I have completed Checkpoint A and am ready to begin implementation"

### Checkpoint B: IMPLEMENTATION COMPLETE  
**BEFORE committing (developer quality gates for individual commits):**
- [ ] All tests pass: `[run project test command]`
- [ ] Type checking clean: `[run project typecheck command]`
- [ ] Linting satisfied: `[run project lint command]` 
- [ ] Code formatting applied: `[run project format command]`
- [ ] Atomic scope maintained (no scope creep)
- [ ] Commit message drafted with clear scope boundaries
- [ ] **EXPLICIT CONFIRMATION**: "I have completed Checkpoint B and am ready to commit"

### Checkpoint C: COMMIT READY
**BEFORE committing code:**
- [ ] All quality gates passed and documented
- [ ] Atomic scope verified (single logical change)
- [ ] Commit message drafted with clear scope boundaries
- [ ] Security-engineer approval obtained (if security-relevant changes)
- [ ] TodoWrite task marked complete
- [ ] **EXPLICIT CONFIRMATION**: "I have completed Checkpoint C and am ready to commit"

### TESTING METHODOLOGY SELECTION GUIDANCE

**METHODOLOGY ASSESSMENT**: Select testing approach during Checkpoint A based on:
- **Classical TDD**: Clear requirements, well-defined specifications
- **Discovery Testing**: Exploratory work, evolving understanding
- **Integration-First**: API-heavy systems, external service integration
- **Characterization Testing**: Legacy code, refactoring projects
- **End-to-End First**: UI/UX focus, user workflow validation

**CHECKPOINT ADAPTATION**:
- **TDD Projects**: Write failing tests before implementation in each cycle
- **Discovery Projects**: Write tests as understanding develops, focus on real functionality
- **Integration Projects**: Prioritize integration tests, then unit tests
- **Legacy Projects**: Characterization tests first, then improvement tests

**NON-NEGOTIABLE**: Regardless of methodology, all checkpoints require comprehensive test coverage and real functionality testing.

### POST-COMMIT REVIEW PROTOCOL
After committing atomic changes:
- [ ] Request code-reviewer review of complete commit series
- [ ] **Repository state**: All changes committed, clean working directory
- [ ] **Review scope**: Entire feature unit or individual atomic commit
- [ ] **Revision handling**: If changes requested, implement as new commits in same branch