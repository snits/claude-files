# Agent Management Commands

## COW Reflink Agent Workflow

The agent system now uses Copy-on-Write (COW) reflinks for efficient agent management:

- **Agent Reserves**: `~/.claude/agent-reserves/` contains 71+ specialist templates
- **Project Agents**: `.claude/agents/` contains project-specific agent instances
- **COW Reflinks**: Use `cp --reflink` to create efficient copies that only duplicate when modified

## Available Commands

### `/agent-browse [SEARCH_TERM]`
Discover and explore available agents in the reserves:
```bash
/agent-browse                    # List all agents by category
/agent-browse game-dev           # Filter by domain  
/agent-browse rust               # Search by technology
/agent-browse "database postgres" # Search capabilities
```

### `/agent-deploy AGENT_NAME [...]`
Deploy agents to current project using reflinks:
```bash
/agent-deploy rust-specialist                    # Deploy single agent
/agent-deploy "rust-specialist game-architect"   # Deploy multiple agents
/agent-deploy database-specialist --preview      # Preview deployment
```

### `/agent-search "SEARCH_TERMS"`
Deep search through agent capabilities and expertise:
```bash
/agent-search "rust performance"        # Find Rust + performance experts
/agent-search database                  # Find database specialists  
/agent-search "machine learning"        # Find ML experts
```

## Legacy: Creating New Agents

When you need a completely new agent type not in reserves:

1. **Check reserves first** - Use `/agent-browse` and `/agent-search` to see if suitable agent exists
2. **Use agent template** - Start with `~/claudes-home/templates/agent-prompt.md`
3. **Create in project** - Save to `.claude/agents/` directory
4. **Consider adding to reserves** - If agent could be useful for other projects

## Workflow Benefits

- **Efficient**: Reflinks save disk space and enable instant deployment
- **Flexible**: Modify project agents freely without affecting templates
- **Discoverable**: Commands help find the right specialist for each task
- **Scalable**: 71+ specialists available without project complexity
