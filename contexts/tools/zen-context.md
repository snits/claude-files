# Zen MCP Tools: Advanced Multi-Model Analysis

## Core Analysis Tools

**`mcp__zen__thinkdeep`** - Systematic Investigation & Root Cause Analysis
- **When to Use**: Complex problems, architectural decisions, unknown issues requiring hypothesis testing
- **Key Capabilities**: Multi-step investigation with evidence-based reasoning, expert validation, systematic problem decomposition
- **Usage Pattern**: Structured investigation with confidence tracking, backtracking support, and progressive refinement

**`mcp__zen__consensus`** - Multi-Model Decision Making
- **When to Use**: Critical decisions, architecture choices, technology evaluations requiring multiple perspectives
- **Key Capabilities**: Structured debate across AI models with different stances, comprehensive recommendation synthesis
- **Usage Pattern**: Multi-expert consultation with systematic validation and rationale documentation

**`mcp__zen__debug`** - Systematic Debugging & Root Cause Analysis  
- **When to Use**: Complex bugs, mysterious errors, performance issues, race conditions requiring systematic investigation
- **Key Capabilities**: Evidence-based debugging with hypothesis testing, confidence tracking, expert analysis validation
- **Usage Pattern**: Systematic investigation with relevant file analysis and expert validation integration

## Secondary Analysis Tools

**`mcp__zen__codereview`** - Comprehensive Code Quality Analysis
- **Triggers**: Systematic quality analysis, security review, architectural assessment
- **Coverage**: Quality, security, performance, architecture with issue severity classification
- **Integration**: Expert validation and comprehensive recommendations with actionable guidance

**`mcp__zen__precommit`** - Git Change Validation
- **Triggers**: Multi-repository validation, change impact assessment, completeness verification  
- **Capabilities**: Systematic git change analysis, security validation, impact assessment across repositories
- **Usage**: Pre-commit validation with comprehensive change impact analysis

**`mcp__zen__planner`** - Interactive Strategic Planning
- **Applications**: Complex project planning, system design, migration strategies, architectural decisions
- **Features**: Sequential planning with revision and branching capabilities, alternative exploration
- **Benefits**: Interactive plan development with deep reflection and systematic approach refinement

**`mcp__zen__chat`** - Collaborative Thinking & Brainstorming
- **Purpose**: Bouncing ideas, getting second opinions, exploring approaches, validating thinking
- **Strengths**: Multi-model collaboration, context-aware brainstorming, cross-conversation continuity
- **Integration**: File and image support for comprehensive collaborative analysis

## Strategic Usage Guidelines

**Model Selection Strategy**:
- **`gemini-2.5-pro`**: Complex reasoning, deep analysis, architectural decisions (1M context + thinking mode)
- **`gemini-2.0-flash`**: Latest capabilities, balanced performance (1M context)
- **`gemini-2.5-flash`**: Quick analysis, simple queries, rapid iterations (1M context)

**Expert Validation Protocol**:
- **ALWAYS use external validation** (`use_assistant_model: true`) for critical decisions, security changes, unknown domains
- **Use internal validation** only for simple scenarios or when user explicitly requests faster processing

**Benefits Over Standard Tools**:
- **Systematic approach**: Structured investigation vs ad-hoc exploration
- **Expert validation**: Multi-model verification vs single-model analysis
- **Evidence-based reasoning**: Hypothesis testing vs assumption-based decisions
- **Comprehensive coverage**: Multiple perspectives vs limited viewpoints