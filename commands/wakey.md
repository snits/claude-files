**Session Startup Protocol:**

1. **Read Current Project Status:**
   - Read session-handoff.md if it exists to get the current project status
   - Look to see if there are any worktrees currently beyond the main repo location.

2. **Check Development Context:**
   - If there is a worktree, or multiple worktrees beyond the main repo, determine which one we are currently working in. Ask the user.
   - Look at the plan for work in the worktree's docs/plans/ directory.
   - Look at the current state of the git branch in the worktree location.

3. **Search Recent Memory:**
   - Use mcp__private-journal__search_journal to search for relevant insights from last few sessions
   - You can also use the episodic-memory plugin's mcp server to search previous conversations
   - Look for any blocking issues or important discoveries
   - Check for established patterns or decisions that affect current work

4. **System Status Check:**
   - Verify MCP connections and agent availability if relevant
   - Check for any pending todos or incomplete workflows

**Then let's discuss what we're going to do next, with full context of where we are and what we've learned.**
