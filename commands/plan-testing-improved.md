# Optimized Project Planning & Testing Strategy Workflow (WITH SCOPE PROTECTION)

## 🚨 CRITICAL ADDITION: MANDATORY TASK DECOMPOSITION CHECK

### **NEW PHASE 0: Task Scope Assessment** (5 minutes - BLOCKS ALL OTHER WORK)

**Before ANY planning begins, assess for scope overrun risk:**

```
project-scope-guardian → Scope overrun risk assessment
- Input: Raw project requirements or task description
- Output: Decomposition requirement flag (ATOMIC | NEEDS_DECOMPOSITION)
```

**AUTOMATIC DECOMPOSITION TRIGGERS:**
- Task mentions multiple security controls → DECOMPOSE
- Task includes "comprehensive" or "robust" → DECOMPOSE
- Task bundles discovery + implementation + deletion → DECOMPOSE
- Task estimated >4 hours → DECOMPOSE
- Task touches >3 files → DECOMPOSE
- Task description >200 words → DECOMPOSE

## PHASE 1: Parallel Foundation Research (15-20 minutes)

### TIER 1: Foundation Layer *(Parallel Execution)*

Execute these three activities **simultaneously**:

#### 1.1 Structure Generation WITH ATOMIC VALIDATION

```
planner-agent (using `mcp__zen__planner`) → High-level project architecture
- **NEW**: Validate each task meets ATOMIC CRITERIA:
  - Single responsibility (one clear outcome)
  - <2 hour implementation time
  - Clear "DONE" definition
  - No bundled operations
- Output: Plan skeleton with ONLY atomic tasks
```

#### 1.2 Technology Discovery *(Critical: Execute BEFORE detailed planning)*

```
web-search-researcher → Technology landscape analysis
- Research existing solutions for each ATOMIC component
- **NEW**: Flag any task requiring multiple technologies as NEEDS_DECOMPOSITION
- Evidence requirement: Document why existing solutions were/weren't used
```

#### 1.3 Architecture Validation WITH SCOPE LIMITS

```
systems-architect (using `mcp__zen__consensus`) → Pattern validation
- Multi-model validation of technical approach
- **NEW**: Reject any "enterprise patterns" for personal tools
- **NEW**: Apply YAGNI filter to all architectural decisions
```

### TIER 1 Output Requirements

- [ ] **NEW**: All tasks validated as ATOMIC or decomposed
- [ ] **NEW**: Personal tool vs enterprise scope confirmed
- [ ] Project structure with phases identified
- [ ] Technology decisions documented with rationale
- [ ] Architecture patterns validated by multiple models

## PHASE 2: Systematic Task Generation (10-15 minutes)

### TIER 2: Refinement Layer *(Sequential with HARD LIMITS)*

#### 2.1 Automated Task Breakdown WITH SCOPE ENFORCEMENT

**ENHANCED SIZING CRITERIA (NOW MANDATORY):**

- **Context Budget**: <4000 tokens HARD LIMIT
- **Time Boundary**: 2 hours MAXIMUM (not 2-4)
- **File Touch Limit**: Maximum 2 files modified
- **Single Focus**: ONE functionality change only
- **No Bundling**: Discovery OR implementation OR deletion (never mixed)
- **Description Limit**: <100 words or automatic decomposition

**NEW DECOMPOSITION RULES:**
```python
if task.contains_any(["and", "also", "then", "plus", "with"]):
    REQUIRE_DECOMPOSITION()

if task.estimated_hours > 2:
    FORCE_ATOMIC_BREAKDOWN()

if task.file_changes > 2:
    SPLIT_INTO_ATOMIC_COMMITS()
```

#### 2.2 Continuous Validation WITH BLOCKING

```
plan-validator → Real-time validation with VETO POWER
- **NEW**: BLOCK any task exceeding atomic limits
- **NEW**: REJECT tasks with undefined scope
- **NEW**: FAIL tasks bundling multiple operations
```

#### 2.3 Personal Tool Filter

**NEW SECTION: YAGNI Enforcement**
- Remove "comprehensive" from all task descriptions
- Delete any "enterprise" patterns for personal tools
- Eliminate "robust error handling" for single-user tools
- Cut "extensive documentation" requirements

## PHASE 3: Parallel Output Generation (10-15 minutes)

### TIER 3: Output Layer *(WITH SCOPE GUARDS)*

#### 3.1 TODO.md Generation WITH DECOMPOSITION

```
Automated TODO.md generation with:
- **NEW**: Atomic task validation badges [ATOMIC] or [NEEDS_DECOMPOSITION]
- **NEW**: Maximum 2-hour time estimates enforced
- **NEW**: Bundled operation detection and rejection
- Agent assignments pre-populated
- Clear dependency tracking
```

#### 3.2 Testing Strategy WITH SCOPE LIMITS

```
Automated prompt generation with HARD CONSTRAINTS:
- **NEW**: Include "This is a PERSONAL TOOL - apply YAGNI"
- **NEW**: Include "Maximum 2-hour implementation window"
- **NEW**: Include "If task seems complex, STOP and decompose"
- **NEW**: Include specific anti-patterns to avoid
```

#### 3.3 Execution Pipeline WITH CIRCUIT BREAKERS

```
Configure handoff with SCOPE PROTECTION:
- **NEW**: Task complexity assessment before agent assignment
- **NEW**: Automatic decomposition for >2 hour estimates
- **NEW**: Scope creep detection during execution
- **NEW**: STOP triggers if task expands beyond original scope
```

## Quality Safeguards WITH SCOPE DISCIPLINE

### NEW: Anti-Pattern Detection

**Automatic Rejection Triggers:**
- "Implement minimal security controls" → TOO VAGUE, decompose
- "Day 2: Delete 14,633 lines" → DELUSIONAL SCOPE, decompose
- "Extract and implement and test" → BUNDLED OPERATIONS, split
- "Comprehensive anything" → ENTERPRISE THINKING, simplify

### NEW: Scope Creep Prevention

**During Execution Monitoring:**
- Agent mentions "while we're at it" → IMMEDIATE STOP
- Agent suggests "also implement" → SCOPE VIOLATION
- Agent claims "comprehensive approach" → YAGNI VIOLATION
- Task exceeds 2-hour window → FORCE DECOMPOSITION

### Success Metrics (ENHANCED)

- **Planning Time**: 45-60 minutes
- **Task Completion Rate**: 90% first-attempt
- **NEW: Scope Creep Rate**: <5% of tasks expand
- **NEW: Average Task Size**: <2 hours actual time
- **NEW: Atomic Commit Rate**: 100% single-purpose commits

## Usage Instructions (WITH SCOPE GATES)

1. **NEW: Execute PHASE 0** scope assessment - BLOCKS if decomposition needed
2. **Execute PHASE 1** parallel activities with atomic validation
3. **Synthesize** PHASE 1 outputs with scope limits applied
4. **Execute PHASE 2** with mandatory decomposition rules
5. **Execute PHASE 3** with scope protection enabled
6. **Validate** no tasks exceed atomic limits
7. **Handoff** to do-todo.md with scope guards active

## Integration Notes

**Critical Learning from Security Failure:**
The security task failed because it bundled 5 different security controls into one task, leading to surface-level, dangerous implementations. This enhanced workflow PREVENTS that pattern by enforcing atomic task decomposition at every stage.

**Scope Protection is NOT Optional:**
Every task MUST pass atomic validation or be decomposed. No exceptions.