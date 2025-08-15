Jerry wants you to create new agent prompt files for agents being discussed in the current project. 

**AGENT CREATION PROCESS:**

1. **Identify the agents** mentioned in our discussion that need prompt files
2. **Use the agent template** - Start with `~/claudes-home/templates/agent-prompt.md` as the base template
3. **Create prompt files** in the project's `.claude/agents/` directory (not the global ~/.claude/agents/) with appropriate filenames

4. **Customize for domain** - Tailor the template to the specific agent's role and expertise (the template includes journal policy and persistent output requirements)
5. **Follow naming conventions** - Use consistent naming pattern for agent files
6. **Document the agents** - Note what agents were created and their purposes

**IMPORTANT**: Use the agent template file (`~/claudes-home/templates/agent-prompt.md`) as your starting point for consistent formatting and required sections. For agents you think need it, add "Use PROACTIVELY", or "MUST USE" to the beginning of their 'description:' in the frontmatter.

After creating the agents, report which ones were created and provide a brief summary of their intended roles.
