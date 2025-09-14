# Optimized Project Planning & TDD Prompt Generation Workflow

## Overview

This workflow uses a **Tiered Parallel Pipeline** approach to dramatically reduce planning time (50-60% improvement) while improving task completion rates from ~70% to ~90% through systematic automation and parallel execution.

## PHASE 1: Parallel Foundation Research (15-20 minutes)

### TIER 1: Foundation Layer *(Parallel Execution)*

Execute these three activities **simultaneously**:

#### 1.1 Structure Generation

```
zen planner mcp tool → High-level project architecture and phases
- Focus: Project structure, major components, dependencies
- Output: Initial plan skeleton with phases and major deliverables
```

#### 1.2 Technology Discovery *(Critical: Execute BEFORE detailed planning)*

```
search-specialist → Technology landscape analysis
- Research existing solutions for each major component
- Document build vs buy vs integrate decisions
- Create technology recommendation matrix
- Evidence requirement: Document why existing solutions were/weren't used
```

#### 1.3 Architecture Validation

```
zen consensus mcp tool → Architecture pattern and approach validation
- Multi-model validation of technical approach
- Risk assessment and mitigation strategies
- Integration pattern recommendations
```

### TIER 1 Output Requirements

- [ ] Project structure with phases identified
- [ ] Technology decisions documented with rationale
- [ ] Architecture patterns validated by multiple models
- [ ] Risk mitigation strategies defined

## PHASE 2: Systematic Task Generation (10-15 minutes)

### TIER 2: Refinement Layer *(Sequential with Automation)*

#### 2.1 Automated Task Breakdown

Apply **systematic sizing criteria** instead of subjective "right-sized" assessment:

**AUTOMATED SIZING CRITERIA:**

- **Context Budget**: <4000 tokens (measured via token counter)
- **Time Boundary**: 2-4 hour implementation window maximum
- **Test Isolation**: Single testable unit with clear inputs/outputs
- **Dependency Limit**: Maximum 2 direct dependencies per task
- **Description Trigger**: >200 words automatically requires breakdown

#### 2.2 Continuous Validation Checkpoints

```
plan-validator → Real-time validation during breakdown (not end-stage)
- Validate each major component as it's defined
- Catch issues early to prevent late-stage rework
- Ensure alignment with project goals and scope
```

#### 2.3 Technology Integration Validation

For each task, validate against discovered technologies:

- Can existing solution handle this requirement?
- Integration complexity assessment
- Custom implementation justification if building

### TIER 2 Output Requirements

- [ ] Tasks meet all automated sizing criteria
- [ ] Each task validated by plan-validator
- [ ] Technology integration decisions confirmed
- [ ] Clear dependency chains established

## PHASE 3: Parallel Output Generation (10-15 minutes)

### TIER 3: Output Layer *(Parallel Execution)*

Execute these three activities **simultaneously**:

#### 3.1 TODO.md Generation with Agent Mapping

```
Automated TODO.md generation with:
- Nested task structure maintained
- Agent assignments pre-populated based on task type
- Integration with Tiered Parallel Pipeline from do-todo.md
- Clear dependency tracking and completion criteria
```

#### 3.2 TDD Prompt Template Population

```
Automated prompt generation using agent-specific templates:
- rust-specialist: Cargo setup, testing patterns, error handling
- debug-specialist: Debugging context, log analysis, trace setup
- security-engineer: Threat model, security requirements, validation
- Context injection: Project state, dependencies, test requirements
```

#### 3.3 Execution Pipeline Configuration

```
Configure handoff to do-todo.md workflow:
- Agent assignment validation
- Quality gate requirements
- Integration test requirements
- Documentation requirements
```

### TIER 3 Output Requirements

- [ ] docs/00-project/plan.md with complete project blueprint
- [ ] docs/00-project/TODO.md with agent assignments
- [ ] docs/00-project/tdd-prompts/ directory with templated prompts
- [ ] Execution pipeline configured for seamless handoff

## Quality Safeguards

### Synthesis & Conflict Resolution

**Critical Addition**: Implement **Synthesis Step** to resolve conflicts from parallel feedback:

- Consolidate outputs from parallel TIER 1 activities
- Resolve conflicts using priority rules (security > performance, etc.)
- Ensure coherent final plan despite parallel generation

### Automation Confidence Scoring

**Fallback Mechanisms** for automation layers:

- **Agent Selection**: Confidence scoring <0.85 triggers human review
- **Prompt Generation**: Self-critique validation for generated prompts
- **Technology Decisions**: Evidence requirements for build vs buy

### Success Metrics

- **Planning Time**: 45-60 minutes (vs 2-3 hours previously)
- **Task Completion Rate**: Target 90% first-attempt success
- **Integration Friction**: Seamless handoff to do-todo.md execution
- **Rework Cycles**: Eliminate late-stage validation rework

## Usage Instructions

1. **Execute PHASE 1** parallel activities simultaneously
2. **Synthesize** PHASE 1 outputs, resolve any conflicts
3. **Execute PHASE 2** systematic task breakdown with automation
4. **Execute PHASE 3** parallel output generation
5. **Validate** all success metrics achieved
6. **Handoff** to do-todo.md for execution

## Integration with do-todo.md

This optimized workflow feeds directly into the existing Tiered Parallel Pipeline:

- Pre-populated agent assignments eliminate selection overhead
- Validated TDD prompts eliminate prompt refinement cycles
- Technology decisions eliminate research during execution
- Quality gates pre-configured for seamless execution

The spec, or initial plan is in the file called:
