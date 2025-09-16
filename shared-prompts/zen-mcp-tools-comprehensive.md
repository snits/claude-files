# Zen MCP Tools: Comprehensive Multi-Model Analysis Capabilities

## CRITICAL TOOL AWARENESS

**zen MCP tools provide POWERFUL multi-model analysis capabilities that can dramatically improve your effectiveness. Use these tools proactively for complex challenges requiring systematic analysis, consensus-building, or expert validation.**

## Core Zen MCP Tools

### `mcp__zen__thinkdeep` - Systematic Investigation & Analysis
**When to Use**: Complex problems requiring hypothesis testing, root cause analysis, architectural decisions
**Key Capabilities**: 
- Multi-step investigation with evidence-based reasoning
- Hypothesis generation and testing with confidence tracking
- Expert validation through multi-model consultation
- Systematic problem decomposition with backtracking support

**Usage Pattern**:
```
mcp__zen__thinkdeep({
  step: "Investigation strategy and findings",
  step_number: 1,
  total_steps: 3,
  findings: "Evidence discovered, patterns identified",
  hypothesis: "Current theory based on evidence",
  confidence: "medium", // exploring, low, medium, high, very_high, almost_certain, certain
  next_step_required: true,
  model: "gemini-2.5-pro" // Use most suitable model for complexity
})
```

### `mcp__zen__consensus` - Multi-Model Decision Making
**When to Use**: Complex decisions, architecture choices, feature proposals, technology evaluations
**Key Capabilities**:
- Consults multiple AI models with different perspectives
- Structured debate and analysis synthesis
- Systematic recommendation generation with rationale

**Usage Pattern**:
```
mcp__zen__consensus({
  step: "Clear proposal for all models to evaluate",
  findings: "Your independent analysis",
  models: [
    {"model": "gemini-2.5-pro", "stance": "for"},
    {"model": "gemini-2.0-flash", "stance": "against"}, 
    {"model": "gemini-2.5-flash", "stance": "neutral"}
  ],
  model: "gemini-2.5-pro"
})
```

### `mcp__zen__planner` - Interactive Planning & Strategy
**When to Use**: Complex project planning, system design, migration strategies, architectural decisions
**Key Capabilities**:
- Sequential planning with revision and branching capabilities
- Interactive plan development with deep reflection
- Alternative approach exploration and comparison

**Usage Pattern**:
```
mcp__zen__planner({
  step: "Planning step content, revisions, questions",
  step_number: 1,
  total_steps: 4,
  next_step_required: true,
  model: "gemini-2.5-pro"
})
```

### `mcp__zen__debug` - Systematic Debugging & Root Cause Analysis
**When to Use**: Complex bugs, mysterious errors, performance issues, race conditions, memory leaks
**Key Capabilities**:
- Systematic investigation with hypothesis testing
- Evidence-based debugging with confidence tracking
- Expert analysis and validation of findings

**Usage Pattern**:
```
mcp__zen__debug({
  step: "Investigation approach and evidence",
  findings: "Discoveries, clues, evidence from investigation",
  hypothesis: "Current root cause theory",
  confidence: "medium",
  relevant_files: ["/absolute/paths/to/relevant/files"],
  model: "gemini-2.5-pro"
})
```

### `mcp__zen__codereview` - Comprehensive Code Review
**When to Use**: Systematic code quality analysis, security review, architectural assessment
**Key Capabilities**:
- Structured review covering quality, security, performance, architecture
- Issue identification with severity levels
- Expert validation and recommendations

**Usage Pattern**:
```
mcp__zen__codereview({
  step: "Review strategy and findings", 
  findings: "Quality, security, performance, architecture discoveries",
  relevant_files: ["/absolute/paths/to/files/for/review"],
  review_type: "full", // full, security, performance, quick
  model: "gemini-2.5-pro"
})
```

### `mcp__zen__precommit` - Git Change Validation
**When to Use**: Multi-repository validation, change impact assessment, completeness verification
**Key Capabilities**:
- Systematic git change analysis
- Security and quality validation
- Impact assessment across repositories

**Usage Pattern**:
```
mcp__zen__precommit({
  step: "Validation strategy and findings",
  findings: "Git changes, modifications, issues discovered", 
  path: "/absolute/path/to/git/repo",
  relevant_files: ["/absolute/paths/to/changed/files"],
  model: "gemini-2.5-pro"
})
```

### `mcp__zen__chat` - Collaborative Thinking & Brainstorming
**When to Use**: Bouncing ideas, getting second opinions, exploring approaches, validating thinking
**Key Capabilities**:
- Multi-model collaboration and idea exploration
- Context-aware brainstorming with file and image support
- Cross-conversation continuity with continuation_id

**Usage Pattern**:
```
mcp__zen__chat({
  prompt: "Your question or idea for collaborative exploration",
  files: ["/absolute/paths/to/relevant/files"],
  model: "gemini-2.5-pro",
  use_websearch: true
})
```

### `mcp__zen__secaudit` - Comprehensive Security Audit
**When to Use**: OWASP Top 10 analysis, compliance evaluation, threat modeling, security architecture review
**Key Capabilities**:
- Systematic vulnerability assessment with OWASP focus
- Compliance requirements validation (SOC2, PCI DSS, HIPAA, GDPR)
- Threat level assessment and security scope analysis
- Expert validation of security findings with severity levels

**Usage Pattern**:
```
mcp__zen__secaudit({
  step: "Security audit strategy and findings",
  findings: "Vulnerabilities, auth issues, validation gaps discovered",
  relevant_files: ["/absolute/paths/to/files/for/audit"],
  audit_focus: "owasp", // owasp, compliance, infrastructure, dependencies, comprehensive
  threat_level: "medium", // low, medium, high, critical
  security_scope: "web application with user authentication and payment processing",
  model: "gemini-2.5-pro"
})
```

### `mcp__zen__docgen` - Comprehensive Code Documentation Generation
**When to Use**: Documentation generation, code analysis, complexity assessment, API documentation
**Key Capabilities**:
- Systematic analysis of functions, classes, and code complexity
- Algorithmic complexity (Big O) analysis and documentation
- Call flow and dependency information documentation
- Inline comments for complex logic with update capabilities

**Usage Pattern**:
```
mcp__zen__docgen({
  step: "Documentation strategy and findings",
  findings: "Code structure analysis and documentation needs discovered",
  relevant_files: ["/absolute/paths/to/files/needing/documentation"],
  document_complexity: true,
  document_flow: true,
  update_existing: true,
  comments_on_complex_logic: true,
  model: "gemini-2.5-pro"
})
```

### `mcp__zen__analyze` - Comprehensive Code Analysis
**When to Use**: Architecture analysis, performance assessment, maintainability evaluation, pattern analysis
**Key Capabilities**:
- Strategic architecture and code quality assessment
- Performance implications and scalability characteristics analysis
- Maintainability factors and tech debt identification
- Systematic investigation with expert validation

**Usage Pattern**:
```
mcp__zen__analyze({
  step: "Analysis strategy and findings",
  findings: "Architectural patterns, performance, maintainability discoveries",
  relevant_files: ["/absolute/paths/to/files/for/analysis"],
  analysis_type: "architecture", // architecture, performance, security, quality, general
  confidence: "medium",
  model: "gemini-2.5-pro"
})
```

### `mcp__zen__refactor` - Code Refactoring Analysis
**When to Use**: Code smell detection, decomposition planning, modernization, maintainability improvements
**Key Capabilities**:
- Systematic code smell identification and categorization
- Decomposition opportunities and modernization recommendations
- Organization improvements and pattern enhancement suggestions
- Style guide compliance and refactoring prioritization

**Usage Pattern**:
```
mcp__zen__refactor({
  step: "Refactoring analysis strategy and findings",
  findings: "Code smells, decomposition opportunities, modernization needs",
  relevant_files: ["/absolute/paths/to/files/needing/refactoring"],
  refactor_type: "codesmells", // codesmells, decompose, modernize, organization
  focus_areas: ["performance", "readability", "maintainability"],
  style_guide_examples: ["/absolute/paths/to/style/reference/files"],
  model: "gemini-2.5-pro"
})
```

### `mcp__zen__tracer` - Systematic Code Tracing
**When to Use**: Method execution analysis, call chain tracing, dependency mapping, architectural understanding
**Key Capabilities**:
- Precision mode for execution flow analysis
- Dependencies mode for structural relationship mapping
- Systematic investigation of code paths and interactions
- Expert validation of tracing results

**Usage Pattern**:
```
mcp__zen__tracer({
  step: "Tracing strategy and findings",
  findings: "Execution paths and dependencies discovered",
  target_description: "Trace user authentication flow to understand security model",
  trace_mode: "precision", // precision (execution flow), dependencies (structural), ask
  relevant_files: ["/absolute/paths/to/files/in/trace"],
  model: "gemini-2.5-pro"
})
```

### `mcp__zen__testgen` - Comprehensive Test Suite Generation
**When to Use**: Creating test suites for specific functions/classes/modules with edge case coverage
**Key Capabilities**:
- Systematic analysis of code paths and failure modes
- Edge case identification and boundary condition testing
- Framework-specific test generation with comprehensive coverage
- Critical path analysis and error handling validation

**Usage Pattern**:
```
mcp__zen__testgen({
  step: "Test generation strategy and findings",
  findings: "Code analysis, critical paths, edge cases, boundary conditions discovered",
  relevant_files: ["/absolute/paths/to/code/needing/tests"],
  confidence: "medium",
  model: "gemini-2.5-pro"
})
```

### `mcp__zen__challenge` - Critical Thinking Enhancement
**When to Use**: When users critically question, disagree with, or challenge previous statements
**Key Capabilities**:
- Prevents reflexive agreement through forced critical analysis
- Promotes truth-seeking over compliance
- Ensures thoughtful evaluation rather than automatic agreement
- Triggers automatically when users show disagreement or skepticism

**Usage Pattern**:
```
mcp__zen__challenge({
  prompt: "User's challenging statement or disagreement to analyze critically"
})
```

### `mcp__zen__listmodels` - Model Provider Information
**When to Use**: Discovering available AI model providers, capabilities, and aliases
**Key Capabilities**:
- Shows configured model providers and available models
- Displays model aliases and capability information
- Helps with model selection for optimal task performance

**Usage Pattern**:
```
mcp__zen__listmodels({})
```

### `mcp__zen__version` - System Information
**When to Use**: Getting server version, configuration details, and available tool inventory
**Key Capabilities**:
- Server version and configuration information
- Complete list of available tools and capabilities
- System status and diagnostic information

**Usage Pattern**:
```
mcp__zen__version({})
```

## Strategic Usage Guidelines

### Model Selection Strategy
- **`gemini-2.5-pro`**: Complex reasoning, deep analysis, architectural decisions (1M context + thinking mode)
- **`gemini-2.0-flash`**: Latest capabilities, balanced performance (1M context)
- **`gemini-2.5-flash`**: Quick analysis, simple queries, rapid iterations (1M context)

### When to Use Expert Validation
**ALWAYS use external validation (`use_assistant_model: true`) for**:
- Critical system decisions
- Security-sensitive changes
- Complex architectural choices
- Unknown problem domains

**Use internal validation only when**:
- User explicitly requests faster processing
- Simple validation scenarios
- Low-risk decisions

### Continuation Strategy
**Use `continuation_id` for**:
- Multi-turn analysis sessions
- Building on previous conversations
- Maintaining context across tool calls
- Progressive problem refinement

**Benefits of zen tools over basic tools**:
- **Systematic approach**: Structured investigation vs ad-hoc exploration
- **Expert validation**: Multi-model verification vs single-model analysis  
- **Evidence-based reasoning**: Hypothesis testing vs assumption-based decisions
- **Comprehensive coverage**: Multiple perspectives vs limited viewpoints

## Integration with Other Tools

**zen tools complement**:
- **Metis MCP tools**: zen provides reasoning, metis provides mathematical computation
- **Standard tools**: zen provides systematic framework, standard tools provide implementation

**Tool selection priority**:
1. **For complex analysis**: zen tools first for systematic approach
2. **For code discovery**: Combine zen analysis with Search tool
3. **For mathematical work**: Combine zen reasoning with metis computation
4. **For implementation**: Use zen planning, then standard implementation tools