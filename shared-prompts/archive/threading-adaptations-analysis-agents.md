# Threading Adaptations: Analysis Agents

## ANALYSIS AGENT THREADING SPECIALIZATION

**Target Agents**: debug-specialist, systems-architect, security-engineer, data-analyst, performance-engineer (analysis phase)

## Core Analysis Threading Patterns

### Investigation Continuations

**Evidence Building Across Sessions**:
```python
# Initial investigation
mcp__zen__debug({
  step: "Starting root cause investigation for [issue]",
  findings: "Initial symptoms and hypotheses",
  hypothesis: "Working theory based on available evidence",
  step_number: 1,
  total_steps: 3,
  next_step_required: True
})

# Continued investigation (building evidence)
mcp__zen__debug({
  step: "Deepening investigation with additional evidence",
  findings: "New evidence discovered, patterns identified",
  hypothesis: "Refined theory based on expanded evidence",
  continuation_id: "[previous-response-continuation-id]",
  step_number: 2,
  total_steps: 3,
  next_step_required: True
})
```

### Cross-Tool Evidence Synthesis

**Analysis Tool Chain Pattern**:
```python
# Step 1: Code structure analysis
Grep({
  pattern: "class|function|def|interface",
  output_mode: "content"
})

# Step 2: Continue with pattern analysis
Grep({
  continuation_id: "[from-symbols-analysis]",
  pattern: "evidence patterns"
})

# Step 3: Synthesize with expert reasoning
mcp__zen__thinkdeep({
  step: "Synthesizing code analysis with expert reasoning",
  continuation_id: "[from-pattern-analysis]",
  findings: "Code structure + patterns reveal..."
})
```

## Analysis-Specific Coordination Protocols

### Deep Investigation Thread Management

**For Complex Root Cause Analysis**:

**Main Investigation Thread Pattern**:
```markdown
INVESTIGATION THREAD: [thread-uuid]
Objective: [root cause analysis goal]
Method: [systematic investigation approach]
Evidence Threads: 
  - Code Analysis: [sub-thread-uuid]
  - Performance Data: [sub-thread-uuid]  
  - Historical Context: [sub-thread-uuid]
Synthesis: [scheduled for main thread]
```

**Sub-Investigation Delegation**:
```markdown
Creating focused analysis thread for [specific evidence area].
Parent investigation: [main-thread-uuid]
Scope: [specific analysis boundary]
Return pattern: Post findings summary to parent thread when complete
```

### Evidence Correlation Threading

**Cross-Evidence Analysis Pattern**:
```python
# Correlating evidence from multiple sources
mcp__zen__consensus({
  step: "Correlating evidence from multiple investigation threads",
  continuation_id: "[main-investigation-uuid]",
  findings: "Evidence from code analysis, performance data, and historical context",
  models: [
    {"model": "gemini-2.5-pro", "stance": "for"},
    {"model": "gemini-2.0-flash", "stance": "against"},
    {"model": "gemini-2.5-flash", "stance": "neutral"}
  ]
})
```

## Analysis Agent Resource Management

### Investigation Context Optimization

**Managing Investigation File Context**:
- **Evidence files**: Include only files directly relevant to current investigation step
- **Context preservation**: Use continuation_id to maintain evidence chain across analysis tools
- **File deduplication**: System automatically handles file context across investigation turns
- **Checkpoint summaries**: Document key evidence findings to prevent loss during token budgeting

### Long-Running Analysis Strategies

**For Complex Multi-Session Investigations**:
```markdown
INVESTIGATION CHECKPOINT - Turn [X] of [Y]:
Primary Hypothesis: [current leading theory]
Supporting Evidence: [key evidence supporting theory]
Contradictory Evidence: [evidence that challenges theory]  
Confidence Level: [low/medium/high/very-high]
Next Investigation Focus: [specific area to explore next]
Thread Health: [any resource or coordination issues]
```

## Analysis Handoff Protocols

### Analysis → Implementation Handoffs

**Delivering Analysis Results for Implementation**:
```markdown
ANALYSIS COMPLETE - HANDOFF TO IMPLEMENTATION:
Thread: [analysis-continuation-id]
Root Cause: [definitive cause identification]
Impact Assessment: [scope and severity of issue]
Solution Approach: [recommended implementation strategy]
Implementation Files: [specific files requiring changes]
Testing Strategy: [how to validate the fix]
Risks: [potential implementation complications]

Ready for implementation agent continuation using thread: [continuation-id]
```

### Analysis → Analysis Handoffs

**Specialist Analysis Coordination**:
```markdown
ANALYSIS HANDOFF - SPECIALIST REQUIRED:
Current Analysis: [continuation-id]
Analysis Focus: [what has been analyzed]
Specialist Needed: [security-engineer/performance-engineer/etc.]
Specific Questions: [targeted analysis requests]
Context Preservation: Continue with thread [continuation-id] for full context
Expected Output: [specific deliverables needed]
```

## Analysis-Specific Threading Examples

### systems-architect Threading Patterns

**Architectural Analysis Workflows**:
```python
# Step 1: System overview and component analysis
mcp__zen__thinkdeep({
  step: "Systematic architectural analysis of [system/component]",
  findings: "Component relationships and architectural patterns",
  relevant_files: ["/path/to/architectural/files"],
  model: "gemini-2.5-pro"
})

# Step 2: Continue with detailed component analysis
Grep({
  continuation_id: "[from-architectural-analysis]",
  pattern: "ComponentPattern",
  output_mode: "content"
})

# Step 3: Synthesize architectural recommendations
mcp__zen__consensus({
  continuation_id: "[from-component-analysis]",
  step: "Architectural decision validation for [system]",
  findings: "Component analysis reveals architectural decisions needed"
})
```

### debug-specialist Threading Patterns  

**Debug Investigation Workflows**:
```python
# Step 1: Problem investigation with evidence gathering
mcp__zen__debug({
  step: "Systematic debugging investigation for [issue]",
  findings: "Initial symptoms, error patterns, reproduction steps",
  hypothesis: "Working theory about root cause",
  relevant_files: ["/path/to/error/logs", "/path/to/failing/code"],
  model: "gemini-2.5-pro"
})

# Step 2: Continue with code analysis for evidence
Grep({
  continuation_id: "[from-debug-investigation]",
  pattern: "error.*pattern|exception.*handling",
  -B: 3,
  -C: 3
})

# Step 3: Return to debug analysis with code evidence
mcp__zen__debug({
  continuation_id: "[from-code-search]",
  step: "Incorporating code analysis evidence into debug investigation",  
  findings: "Code patterns confirm/refute initial hypothesis",
  hypothesis: "Refined root cause theory with code evidence"
})
```

## Analysis Quality Assurance

### Analysis Validation Patterns

**Self-Validation Threading**:
```python
# Validate analysis completeness and accuracy
mcp__zen__consensus({
  continuation_id: "[analysis-thread]",
  step: "Validation of analysis completeness and accuracy",
  findings: "Analysis results require multi-perspective validation",
  models: [
    {"model": "gemini-2.5-pro", "stance": "for"},
    {"model": "gemini-2.0-flash", "stance": "against"}
  ]
})
```

### Analysis Documentation Threading

**Analysis Documentation Workflows**:
```markdown
ANALYSIS DOCUMENTATION THREAD:
Source Analysis: [analysis-continuation-id]
Documentation Scope: [what aspects to document]
Target Audience: [implementation agents/stakeholders]
Format: [technical report/architectural decision/investigation summary]
Files to Update: [documentation files requiring updates]
```

## Best Practices for Analysis Agents

### Investigation Planning

1. **Thread Strategy**: Plan investigation thread structure before starting
2. **Evidence Organization**: Use sub-threads for different evidence categories  
3. **Context Management**: Regular checkpoints to preserve critical findings
4. **Tool Integration**: Seamless transitions between analysis tools via continuation_id

### Multi-Agent Coordination

1. **Analysis Handoffs**: Clear deliverables and context preservation for implementation agents
2. **Parallel Analysis**: Coordinate with other analysis agents using sub-thread pattern
3. **Quality Gates**: Build validation into analysis workflow through consensus tools
4. **Documentation**: Analysis findings properly captured for future reference

### Resource Optimization

1. **File Context**: Strategic file inclusion based on investigation phase
2. **Token Management**: Investigation checkpoints prevent context loss  
3. **Thread Hygiene**: Conclude analysis threads when investigation complete
4. **Evidence Synthesis**: Consolidate findings from multiple sub-investigations

**ANALYSIS AUTHORITY**: Analysis agents have authority to create investigation sub-threads, coordinate evidence gathering across multiple tools, and deliver definitive analysis results to implementation agents through proper thread handoff protocols.