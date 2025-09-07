# Agent Delegation Protocol

## DELEGATION-FIRST PRINCIPLE
**CORE RULE**: If a specialized agent exists that is suited to a task, **YOU MUST delegate the task to that agent** via Task tool. NEVER attempt specialized work without domain expertise.

## Task Assessment for Delegation

**Systematic Evaluation Process**:
1. **Identify task domain**: What specialized knowledge/skills does this task require?
2. **Check existing agents**: Do we have an agent with the required expertise?
3. **Delegate if match exists**: Use Task tool with appropriate agent type
4. **Create agent if none exists**: Stop and work with Jerry to define and create needed agent
5. **Never attempt specialized work**: Better to pause and get right agent than proceed inadequately

## Quality Assurance Agent Triggers

**test-specialist MANDATORY Triggers**:
- After ANY new feature implementation (validate comprehensive test coverage)
- After bug fixes (ensure fix properly tested and won't regress)
- When discovering untested code (implement missing test coverage immediately)
- Before committing code (verify all tests pass and coverage complete)

**qa-engineer MANDATORY Triggers**:
- Before marking features as complete (validate end-to-end user workflows)
- After bug fixes (verify fix works in real user scenarios)
- Before releases (conduct final quality validation across environments)
- When integration issues suspected (test component interactions)

**Authority Level**: Both QA agents can **BLOCK commits/releases** for quality violations

## Hierarchical Decision Authority

**When Agents Disagree - Priority Order**:
1. **Quality Assurance** (test-specialist, qa-engineer can BLOCK releases for violations)
2. **User Experience** (ux-design-expert has final authority on user-facing decisions)
3. **System Integrity** (systems-architect has authority on architecture/scalability)
4. **Code Quality** (code-reviewer standards on maintainability/security)
5. **Implementation Pragmatism** (debug-specialist, performance-engineer on timeline/resources)

## Agent Workflow Integration

**Implementation Agents** (code-reviewer, debug-specialist, performance-engineer):
- **Full tool access**: Bash, Edit, Write, MultiEdit, Read, Grep, Glob + domain-specific tools
- **MUST follow workflow checkpoints A, B, C** before any commits
- **MUST enforce atomic scope discipline** to prevent scope expansion
- **MUST request code-reviewer review** after commits

**Quality Assurance Agents** (test-specialist, qa-engineer):
- **Proactive triggers**: MUST be used systematically, not just reactively
- **Blocking authority**: Can prevent commits if quality standards unmet
- **Full tool access**: For comprehensive testing and validation

**Analysis & Architecture Agents** (systems-architect, security-engineer, ux-design-expert):
- **Analysis-focused tools**: Read, Grep, Glob, WebFetch, WebSearch + domain tools
- **Implementation via handoff**: Coordinate with implementation agents for code changes
- **MUST respect atomic commit boundaries** in guidance provided

## Human-Hierarchical Reasoning Model
- **Jerry and Claude**: Strategic coordination and decision-making authority
- **Specialized agents**: Deep domain expertise in specific technical areas
- **Clear handoff protocols**: Systematic task delegation and result integration
- **Quality assurance loops**: Specialist review of non-specialist work mandatory