# Agent Delegation Protocol

## DELEGATION-FIRST PRINCIPLE
If a specialized agent exists that is suited to a task, YOU MUST delegate the task to that agent. If no suitable agent exists, work with Jerry to create one.

## Task Assessment for Delegation:
1. **Identify task domain**: What specialized knowledge/skills does this task require?
2. **Check existing agents**: Do we have an agent with the required expertise?
3. **Delegate if match exists**: Use Task tool with appropriate agent type
4. **Create agent if none exists**: Stop and work with Jerry to define and create the needed agent
5. **Never attempt specialized work without domain expertise**: Better to pause and get the right agent than proceed with inadequate knowledge

## Human-Hierarchical Reasoning Model:
- **Jerry and Claude sit at the top**: Strategic coordination and decision-making
- **Specialized agents handle domain work**: Deep expertise in specific areas
- **Clear handoff protocols**: Systematic task delegation and result integration
- **Quality assurance loops**: Specialist review of non-specialist work

## Agent Creation Triggers:
- Task requires specialized knowledge not covered by existing agents
- Repeated similar tasks that could benefit from dedicated expertise
- Complex domain that would benefit from systematic approach
- Quality issues in area that needs specialist attention

## Hierarchical Decision Authority

### When Agents Disagree - Priority Order:
1. **Quality Assurance** (test-specialist and qa-engineer can BLOCK releases for quality violations)
2. **User Experience** (ux-design-expert has final authority on user-facing decisions)
3. **System Integrity** (systems-architect has authority on architecture/scalability)
4. **Code Quality** (code-reviewer standards on maintainability/security)
5. **Implementation Pragmatism** (debug-specialist and performance-engineer have authority on timeline/resource constraints)

## Agent-Specific Workflow Integration

**Implementation Agents** (code-reviewer, debug-specialist, performance-engineer):
- **CHECKPOINT A**: MUST verify git status clean and feature branch created before any code changes
- **CHECKPOINT B**: MUST run all quality gates and verify completion before committing
- **CHECKPOINT C**: MUST verify all requirements met before committing, then request code-reviewer review
- MUST reference TDD workflow and code-reviewer approval in their implementation process
- MUST mention quality gates in their handoff protocols
- MUST enforce atomic scope discipline to prevent "onion peeling"
- Have full tool access: Bash, Edit, Write, MultiEdit, Read, Grep, Glob, LS + domain-specific tools

**Quality Assurance Agents** (test-specialist, qa-engineer):
- **MANDATORY TRIGGERS**: MUST be used proactively, not just reactively
- **Authority Level**: Can BLOCK commits if quality standards not met
- Have full tool access for comprehensive testing and validation

**Analysis & Architecture Agents** (systems-architect, security-engineer, ux-design-expert):
- MUST coordinate with implementation agents for code changes
- MUST respect atomic commit boundaries in their guidance
- MUST reference quality gates when applicable to their domain
- Analysis-only tools: Read, Grep, Glob, LS, WebFetch, WebSearch + domain-specific tools
- Implementation via handoff to implementation agents