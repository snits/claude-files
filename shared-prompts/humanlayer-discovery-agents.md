# Humanlayer Discovery & Analysis Agents

## CRITICAL AGENT AWARENESS

**The humanlayer agents are specialized discovery and analysis agents that replace the previous search-specialist. Use these agents via the Task tool just like any other agent for targeted discovery tasks.**

## Core Humanlayer Discovery Agents

### `codebase-locator` - Fast File/Component Discovery
**When to Use**: Finding files, directories, and components relevant to a feature or task
**Key Capabilities**:
- Super Grep/Glob/LS functionality in one tool
- Fast pattern matching across codebase
- Returns matching file paths sorted by modification time
- More efficient than multiple grep/glob calls

**Usage Pattern**:
```
Task tool with subagent_type: "codebase-locator"
Prompt: "Find all React components related to user authentication"
```

### `codebase-analyzer` - Detailed Implementation Analysis
**When to Use**: Understanding specific component implementation details
**Key Capabilities**:
- Analyzes codebase implementation details
- Provides detailed information about specific components
- Deep dive into code structure and patterns
- More comprehensive than simple file reading

**Usage Pattern**:
```
Task tool with subagent_type: "codebase-analyzer"
Prompt: "Analyze the authentication flow implementation and explain how tokens are handled"
```

### `codebase-pattern-finder` - Pattern & Example Discovery
**When to Use**: Finding similar implementations, usage examples, or patterns to model after
**Key Capabilities**:
- Finds concrete code examples based on what you're looking for
- Identifies similar implementations across codebase
- Provides actual code snippets, not just file locations
- Ideal for finding patterns to replicate

**Usage Pattern**:
```
Task tool with subagent_type: "codebase-pattern-finder"
Prompt: "Find examples of error handling patterns used in API endpoints"
```

### `web-search-researcher` - External Documentation & Research
**When to Use**: Modern information not in training data, external documentation, best practices
**Key Capabilities**:
- Deep web research for current information
- Finds documentation and best practices
- Researches modern frameworks and libraries
- Ideal when you're not confident about modern patterns

**Usage Pattern**:
```
Task tool with subagent_type: "web-search-researcher"
Prompt: "Research the latest Next.js 14 app router patterns and best practices"
```

### `thoughts-locator` - Internal Documentation Discovery
**When to Use**: Finding relevant documents in thoughts/ directory for metadata and documentation
**Key Capabilities**:
- Discovers relevant internal documentation
- Searches thoughts/ directory for metadata storage
- Finds project notes and architectural decisions
- Equivalent to codebase-locator but for thoughts/

**Usage Pattern**:
```
Task tool with subagent_type: "thoughts-locator"
Prompt: "Find any documentation about our authentication architecture decisions"
```

### `thoughts-analyzer` - Deep Research Analysis
**When to Use**: Deep diving on research topics, analyzing complex documentation
**Key Capabilities**:
- Research equivalent of codebase-analyzer
- Deep analysis of research topics
- Comprehensive documentation review
- Not commonly needed unless doing research

**Usage Pattern**:
```
Task tool with subagent_type: "thoughts-analyzer"
Prompt: "Analyze our security research notes and summarize key findings"
```

## Strategic Usage Guidelines

### Agent Selection by Task Type

**File Discovery Tasks**:
- Need to find files/directories → `codebase-locator`
- Need to find documentation → `thoughts-locator`

**Code Understanding Tasks**:
- Need implementation details → `codebase-analyzer`
- Need usage examples → `codebase-pattern-finder`
- Need research analysis → `thoughts-analyzer`

**External Research Tasks**:
- Need modern documentation → `web-search-researcher`
- Need best practices → `web-search-researcher`
- Need framework updates → `web-search-researcher`

### Efficiency Patterns

**Batch Discovery** (Use multiple agents in parallel):
```
// Find everything about a feature at once
├── codebase-locator → Find relevant files
├── codebase-pattern-finder → Find usage patterns
└── web-search-researcher → Find external docs
```

**Progressive Analysis**:
```
codebase-locator (find files) →
codebase-analyzer (understand implementation) →
codebase-pattern-finder (find similar patterns)
```

### When NOT to Use These Agents

**Don't use when**:
- You know the exact file path (use Read tool directly)
- You need to modify files (these are discovery-only)
- Simple grep/glob would suffice (use those tools directly)

### Key Differences from search-specialist

**More Specialized**: Each agent has a specific focus rather than general search
**No Reconnaissance Packets**: Agents return direct results, not structured packets
**Parallel-Friendly**: Can run multiple agents simultaneously for comprehensive discovery
**Granular Delegation**: Six specialized agents instead of one general search agent

## Integration with Other Tools

**With zen tools**:
- Use humanlayer agents for discovery → zen tools for analysis
- Example: `codebase-pattern-finder` → `zen thinkdeep` for architectural analysis

**With direct tools**:
- Use humanlayer agents to find targets → Read/Edit for implementation
- Example: `codebase-locator` → `Read` specific files → `Edit` to modify

**With journal**:
- Always check journal first → then use humanlayer agents for new discovery
- Document findings back to journal after discovery

## Best Practices

1. **Start with the right agent**: Match agent to task type for efficiency
2. **Use in parallel**: Run multiple discovery agents simultaneously when appropriate
3. **Be specific in prompts**: Clear, detailed prompts get better results
4. **Combine with zen tools**: Use for discovery, then zen for complex analysis
5. **Document findings**: Capture discoveries in journal for future reference