List all currently active agents for the current project (global + project-specific).

**Displays active agents in two categories:**

**🌐 GLOBAL AGENTS (from ~/.claude/agents/):**
- Always available across all projects
- Show agent name and brief capability summary

**📁 PROJECT AGENTS (from .claude/agents/ if exists):**  
- Only available in current project
- Show agent name and brief capability summary
- If no project agents directory: show helpful message

**Implementation:**
1. **Check global agents:**
   ```bash
   ls ~/.claude/agents/ | sed 's/\.md$//' | sort
   ```

2. **Check project agents:**
   ```bash
   if [ -d ".claude/agents" ]; then
     ls .claude/agents/ | sed 's/\.md$//' | sort
   else
     echo "No project-specific agents directory found"
   fi
   ```

3. **For each agent, show brief summary:**
   - Extract first line after "# " or "## " from agent file
   - Or show first line of agent description
   - Format: "agent-name: Brief description"

**Sample output format:**
```
🌐 GLOBAL AGENTS (5 active):
├── code-reviewer: Direct, honest feedback on code quality and architecture
├── copy-editor: Professional copy editing for communications
├── git-scm-master: Expert Git source control management
├── nomenclature-specialist: Expert naming strategy and terminology design  
└── ux-design-expert: User experience design guidance and optimization

📁 PROJECT AGENTS (2 active):
├── database-specialist: Database architecture and optimization expert
└── api-design-expert: Expert API design specialist for interface consistency

💡 Use '/agent-browse' to discover more agents
💡 Use '/agent-deploy AGENT_NAME' to add agents to current project
```

**Error handling:**
- If ~/.claude/agents/ doesn't exist: explain global agent setup
- Handle permission issues gracefully
- Show clear count totals for easy scanning