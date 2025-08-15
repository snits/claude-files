Browse and discover agents in the ~/.claude/agent-reserves/ collection.

**If no arguments provided ($ARGUMENTS is empty):**
- List all agents categorized by domain:
  - 🎮 GAME DEVELOPMENT (game, rendering, simulation, engine)
  - 🏗️ SYSTEM ARCHITECTURE (architect, systems, infrastructure) 
  - 🔬 SCIENTIFIC/MATHEMATICAL (climate, physics, mathematical, computational, scientific)
  - 💾 DATA/DATABASE (data, database, ml-, ai-, vector)
  - ⚙️ ENGINEERING/DEVOPS (engineer, devops, specialist, debug)
  - 📋 PROCESS/MANAGEMENT (process, compliance, integration, workflow)
  - 🔧 LANGUAGE/TOOLS (rust, typescript, bytecode, compiler, dsl)
  - 📝 OTHER SPECIALISTS (remaining agents)

**If arguments provided ($ARGUMENTS contains search terms):**
- Search agent filenames for matches: "$ARGUMENTS"
- Search agent file contents for capability mentions
- Show relevant results with context

Use bash commands to:
1. Count total agents: `ls ~/.claude/agent-reserves/ | wc -l`
2. Filter by category: `ls ~/.claude/agent-reserves/ | grep -E "pattern" | sort`  
3. Search contents: `grep -l -i "$ARGUMENTS" ~/.claude/agent-reserves/*.md`

Always end with: "💡 Use '/agent-deploy AGENT_NAME' to add to current project"