# Agent Prompt Design Principles

## Core Philosophy
**"What they actually need to do their job, not a bunch of other stuff"**

Agents are specialists, not process engineers. Give them domain context and clear objectives, not methodology lectures.

## Essential Components (Keep)

### 1. Core Mission (2-3 sentences max)
- What is this agent's primary responsibility?
- What domain expertise do they provide?

### 2. Project Context (Current state only)
- Relevant technical details for THIS project
- Current implementation status
- Key constraints or parameters they need to know

### 3. Critical Questions/Objectives (3-5 specific items)
- What decisions need their expertise?
- What problems are they solving?
- What deliverables are expected?

## Bloat to Remove

### ❌ Methodology Lectures
- Don't list every tool they might use (NumPy, SciPy, etc.)
- Don't enumerate all possible approaches (Monte Carlo, regression, etc.)
- Replace with: "Use [domain] methods" or "Apply [field] expertise"

### ❌ Communication Style Rules  
- Don't specify "be data-driven" or "provide specific recommendations"
- They're domain experts - they know how to communicate in their field

### ❌ Deliverable Format Details
- Don't list obvious outputs like "reports" or "recommendations" 
- Focus on WHAT decisions they're helping with, not HOW they format it

### ❌ Process Engineering
- No workflow management (that's in CLAUDE.md)
- No quality gate procedures (that's universal)
- No collaboration protocols (agents coordinate naturally)

## Template Structure
```markdown
# [Agent Type]

## Core Mission
[2-3 sentences: their domain expertise and primary responsibility]

## Project Context
[Current technical state, key parameters, constraints]

## Key Questions/Objectives
- [Specific decision/problem #1]
- [Specific decision/problem #2] 
- [Specific decision/problem #3]
```

## Anti-Patterns (Common Bloat)

### Tool Enumeration Bloat
❌ "Proficient in SageMath, NumPy, SciPy, matplotlib, pandas, scikit-learn..."
✅ "Use quantitative analysis methods"

### Methodology Bloat  
❌ "Monte Carlo simulation, mathematical modeling, optimization analysis, statistical validation..."
✅ "Apply statistical and mathematical analysis"

### Communication Bloat
❌ "Be data-driven, provide precise recommendations, consider strategic implications..."
✅ [Nothing - they're experts, they know this]

### Deliverable Bloat
❌ "Balance reports, mathematical models, simulation data, parameter recommendations..."
✅ "Provide numerical recommendations with rationale"

## Success Metrics
- Agent prompts under 50 lines
- No methodology instructions (they're experts)
- No communication style rules (trust their expertise)
- Focus on project-specific context and decisions

## Remember
**You can't prompt engineer agents into CMM Level 5.** Give them what they need to know, trust their expertise, get out of their way.