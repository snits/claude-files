# MCP Tool Selection & Discoverability Framework

## SYSTEMATIC TOOL DISCOVERABILITY

**CRITICAL MISSION**: Ensure all 71 deployed agents can discover and effectively utilize the most powerful MCP tools available. This framework provides systematic guidance for tool selection based on task complexity, domain requirements, and strategic effectiveness.**

## Tool Categories & Selection Hierarchy

### Tier 1: Advanced Multi-Model Analysis (zen)

**HIGHEST IMPACT TOOLS** - Use proactively for complex challenges

**`mcp__zen__thinkdeep`** - Systematic Investigation & Root Cause Analysis

- **Triggers**: Complex bugs, architectural decisions, unknown problems
- **Benefits**: Multi-step reasoning, hypothesis testing, expert validation
- **Selection Criteria**: Problem complexity high, multiple unknowns, critical decisions

**`mcp__zen__consensus`** - Multi-Model Decision Making  

- **Triggers**: Architecture choices, technology decisions, controversial topics
- **Benefits**: Multiple AI perspectives, structured debate, validated recommendations
- **Selection Criteria**: High-stakes decisions, multiple valid approaches, need for validation

**`mcp__zen__planner`** - Interactive Strategic Planning

- **Triggers**: Complex project planning, system migrations, multi-phase implementations
- **Benefits**: Systematic planning, revision capability, alternative exploration
- **Selection Criteria**: Complex coordination needed, iterative planning required

### Tier 2: Specialized Domain Tools

**Humanlayer (Discovery & Analysis)**:

- **codebase-locator**: Fast file/component discovery across codebase
- **codebase-analyzer**: Detailed implementation analysis
- **codebase-pattern-finder**: Find usage examples and patterns
- **web-search-researcher**: External documentation and modern info
- **thoughts-locator**: Internal documentation discovery
- **thoughts-analyzer**: Deep research analysis
- **Selection Criteria**: Discovery tasks, pattern finding, research needs
- **Integration**: Use for discovery → zen tools for analysis

**Metis (Mathematical)**:

- **Primary Use**: Mathematical modeling, numerical analysis, scientific computation
- **Selection Criteria**: Mathematical computation required, modeling needed
- **Integration**: Combine with zen thinkdeep for complex mathematical problems

### Tier 3: Standard Implementation Tools

- File operations (Read, Write, Edit, MultiEdit)
- System operations (Bash, git)
- Search operations (Grep, Glob)

## Decision Matrix for Tool Selection

### Problem Complexity Assessment

**SIMPLE PROBLEMS** (Use Tier 3 + basic MCP):

- Clear requirements, known solution path
- Single domain focus, minimal unknowns  
- Tools: Standard file ops + basic MCP tools

**COMPLEX PROBLEMS** (Use Tier 1 + domain-specific):

- Multiple unknowns, unclear solution path
- Cross-domain requirements, high impact decisions
- Tools: zen thinkdeep/consensus + domain MCP tools

**CRITICAL DECISIONS** (Use Full MCP Suite):

- High business impact, architectural significance
- Security implications, performance requirements
- Tools: zen consensus + zen thinkdeep + domain tools

### Domain-Specific Selection Patterns

**🔍 Code Analysis & Architecture**:

```
1. codebase-locator → Find relevant files
2. codebase-analyzer → Detailed implementation analysis
3. zen thinkdeep → Systematic analysis
4. zen codereview → Expert validation
```

**🐛 Debugging & Problem Investigation**:

```
1. zen debug → Systematic investigation
2. codebase-pattern-finder → Find similar implementations
3. codebase-analyzer → Understand implementation details
4. zen thinkdeep → Root cause analysis (if needed)
```

**📊 Mathematical & Data Analysis**:

```
1. metis design_mathematical_model → Model creation
2. metis execute_sage_code → Implementation  
3. metis verify_mathematical_solution → Validation
4. zen thinkdeep → Complex problem decomposition (if needed)
```

**🏗️ Planning & Architecture Decisions**:

```
1. zen planner → Strategic planning
2. zen consensus → Multi-model validation
3. Domain tools → Implementation support
4. zen codereview/precommit → Quality validation
```

## Tool Discoverability Mechanisms

### Strategic Tool Prompting

**In Agent Prompts - Include These Sections**:

```markdown
## Advanced Analysis Capabilities

**CRITICAL TOOL AWARENESS**: You have access to powerful MCP tools that can dramatically improve your effectiveness:

Read ~/.claude/shared-prompts/zen-mcp-tools-comprehensive.md to learn more about zen mcp tools
Read ~/.claude/shared-prompts/metis-mathematical-computation.md if working in mathematical domain

**Tool Selection Strategy**: [Domain-specific guidance for when to use advanced tools]
```

### Contextual Tool Suggestions

**Embed in Workflow Descriptions**:

- "For complex problems, START with zen thinkdeep before implementation"
- "For architectural decisions, use zen consensus to validate approaches"
- "For code discovery, use codebase-locator for files, codebase-analyzer for details"
- "For pattern finding, use codebase-pattern-finder for concrete examples"
- "For external research, use web-search-researcher for modern documentation"
- "For mathematical modeling, use metis design_mathematical_model"

### Task-Triggered Tool Recommendations

**Complex Task Indicators → Tool Suggestions**:

- "Unknown problem domain" → zen thinkdeep
- "Multiple solution approaches" → zen consensus
- "Need to find files" → codebase-locator
- "Need implementation details" → codebase-analyzer
- "Need usage examples" → codebase-pattern-finder
- "Need modern docs" → web-search-researcher
- "Code architecture analysis" → codebase-analyzer + zen codereview
- "Mathematical problem solving" → metis tools + zen validation
- "System debugging" → zen debug + codebase-pattern-finder

## Integration Patterns for Maximum Effectiveness

### Sequential Tool Workflows

**Investigation Pattern**:

```
zen thinkdeep (systematic analysis) → 
domain tools (specific discovery) → 
zen thinkdeep (synthesis) →
implementation tools (execution)
```

**Decision Pattern**:

```
zen planner (strategic planning) →
zen consensus (multi-model validation) →
domain tools (implementation support) →
zen codereview (quality validation)
```

**Discovery Pattern**:

```
codebase-locator (find files) →
codebase-analyzer (understand implementation) →
codebase-pattern-finder (find examples) →
zen thinkdeep (analysis) →
Implementation tools (changes)
```

### Cross-Tool Context Transfer

**Maintain Context Across Tools**:

- Use `continuation_id` for zen tools to maintain conversation context
- Reference file paths consistently across tools
- Build on previous analysis in subsequent tool calls
- Document findings between tool transitions

### Expert Validation Integration

**When to Use Expert Validation**:

- **Always use** for critical decisions and complex problems
- **Use selectively** for routine tasks with `use_assistant_model: false`
- **Combine validation** from multiple zen tools for comprehensive analysis

## Agent-Specific Implementation Guidance

### For Technical Implementation Agents

- **Priority tools**: zen debug, zen codereview, Search tool
- **Integration pattern**: Investigation → Analysis → Implementation → Review
- **Tool awareness**: Proactively suggest zen tools for complex problems

### For Architecture & Design Agents  

- **Priority tools**: zen consensus, zen planner, zen thinkdeep
- **Integration pattern**: Research → Planning → Validation → Documentation
- **Tool awareness**: Use multi-model consensus for critical decisions

### For Mathematical & Scientific Agents

- **Priority tools**: metis mathematical suite, zen thinkdeep for complex problems
- **Integration pattern**: Modeling → Computation → Verification → Optimization
- **Tool awareness**: Combine mathematical computation with expert reasoning

### For Quality Assurance Agents

- **Priority tools**: zen codereview, zen precommit, Search tool
- **Integration pattern**: Analysis → Review → Validation → Documentation
- **Tool awareness**: Use systematic review workflows for comprehensive coverage

## Success Metrics & Continuous Improvement

### Effectiveness Indicators

- **Tool Utilization**: Agents proactively use advanced MCP tools for appropriate tasks
- **Problem Resolution**: Complex problems resolved more systematically and thoroughly
- **Decision Quality**: Critical decisions validated through multi-model analysis
- **Code Quality**: Better code analysis and architectural understanding

### Agent Feedback Integration

- **Tool Discovery**: Track which tools agents discover and use effectively
- **Pattern Recognition**: Identify successful tool combination patterns
- **Gap Analysis**: Find tools that are underutilized despite being appropriate
- **Training Needs**: Update documentation based on agent tool usage patterns

### Continuous Framework Enhancement

- **Monitor tool effectiveness**: Track success rates of different tool combinations
- **Update selection criteria**: Refine decision matrix based on real-world usage
- **Enhance discoverability**: Improve tool awareness mechanisms based on gaps
- **Expand integration patterns**: Document new successful tool workflow patterns

**FRAMEWORK AUTHORITY**: This tool selection framework should be integrated into ALL agent templates to ensure systematic discovery and utilization of our powerful MCP tool ecosystem across all 71 deployed agents.

