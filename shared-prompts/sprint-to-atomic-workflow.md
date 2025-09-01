# Sprint-to-Atomic-Task Workflow

## SYSTEMATIC DEVELOPMENT FLOW
**This workflow enforces predictable commit sizes and maintains development momentum through systematic task breakdown and agent delegation.**

### Phase 1: Sprint Planning (Feature → Stories)

**Break complex features into user stories:**
- Each story = **1-4 hours of focused work**
- Each story = **one logical commit** when complete
- **5-10 stories per sprint cycle** for manageable scope
- Clear acceptance criteria for each story

**User Story Template:**
```
Story [X.Y]: [Concise functional description]

As a [user type], I want [functionality] so that [business value]

Acceptance Criteria:
- [ ] Specific testable requirement 1
- [ ] Specific testable requirement 2  
- [ ] All tests pass
- [ ] Code-reviewer approval obtained

Estimated Commit: "[type]: [concise description]"
```

### Phase 2: Story Breakdown (Story → Atomic Tasks)

**For each user story, create atomic tasks in TodoWrite:**
1. **Analysis Tasks**: Understanding requirements, researching existing code
2. **Implementation Tasks**: Single logical changes (≤500 lines, ≤5 files)
3. **Quality Tasks**: Testing, validation, documentation updates
4. **Integration Tasks**: Code review, merge coordination

**Atomic Task Criteria:**
- **Single responsibility**: One clear objective
- **Bounded scope**: Predictable time investment (30-90 minutes)
- **Testable outcome**: Clear success/failure criteria
- **Agent-assignable**: Matches specialist expertise domain

### Phase 3: Task Execution (Task → Agent → Commit)

**For each atomic task:**

1. **Agent Selection**: Delegate to appropriate specialist agent based on task domain
2. **Agent Execution**: Agent completes task following Checkpoints A, B, C
3. **Quality Gates**: All tests, lint, typecheck pass before commit
4. **Commit Creation**: Atomic commit with proper attribution
5. **Next Task**: Mark completed, move to next atomic task

**Agent Delegation Examples:**
- Database schema changes → `database-specialist`
- API endpoint implementation → `typescript-database-engineer`
- Security validation → `security-engineer`
- Performance optimization → `performance-engineer`
- Code quality review → `code-reviewer`

### Phase 4: Sprint Completion (All Stories → Feature Complete)

**After all stories complete:**
- **Feature validation**: End-to-end testing across story commits
- **Documentation updates**: User-facing documentation, API docs
- **Sprint retrospective**: Capture lessons learned in journal
- **Next sprint planning**: Based on completed work and learnings

## COMMIT SIZE CONTROL

**This workflow naturally enforces manageable commit sizes:**
- **Story-level commits**: 1-4 hours of work, single logical feature increment
- **Atomic task breakdown**: Prevents "onion peeling" scope expansion
- **Agent specialization**: Reduces complexity per commit through domain expertise
- **Quality gates**: Early detection of scope creep before commits grow large

## AGENT COORDINATION PROTOCOL

**Agent Handoff Requirements:**
- **Clear scope**: TodoWrite task with acceptance criteria
- **Context provision**: Relevant files, previous decisions, constraints
- **Authority boundaries**: What agent can decide vs. must escalate
- **Output requirements**: Files to update, documentation to create
- **Integration points**: How work connects to other story tasks

**Quality Assurance Integration:**
- **test-specialist**: Mandatory for all implementation tasks
- **qa-engineer**: Required for feature-level validation
- **code-reviewer**: Required after each atomic commit
- **security-engineer**: Required for any user input or sensitive data handling

## SUCCESS METRICS

**Workflow Effectiveness Indicators:**
- **Commit size consistency**: Most commits 100-500 lines
- **Story completion predictability**: Stories complete within estimated time
- **Quality gate pass rate**: >95% first-time pass on tests/lint/typecheck
- **Agent specialization effectiveness**: Reduced back-and-forth, clearer output
- **Sprint velocity**: Consistent story completion across sprint cycles

**Red Flags Requiring Process Adjustment:**
- Commits consistently >1000 lines (task breakdown insufficient)
- Stories taking >6 hours (scope estimation issues)  
- Frequent quality gate failures (agent coordination problems)
- Agent confusion or scope creep (task specification unclear)
- Story dependencies causing blocking (sprint planning needs improvement)