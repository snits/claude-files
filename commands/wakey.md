---
name: wakey
description: Use this when a session is beginning to get context on the current project
---

We have started a new session. Please go through the following steps:

**Session Startup Protocol:**

1. **Read Current Project Status:**
   - Read session-handoff.md if it exists to get the current project status
   - Look to see if there are any worktrees currently beyond the main repo location.

2. **Check Development Context:**
   - Check the state of the git repository, and whether there are uncommitted changes.
   - If there is a worktree, or multiple worktrees beyond the main repo, determine which one we are currently working in. Ask the user.
   - Look at the plan for work in the worktree's docs/plans/ directory.
   - Look at the current state of the git branch in the worktree location.

3. **Search Recent Memory:**
   - Use mcp__mnemosyne__search_journal to search for relevant insights from last few sessions
   - You can also use the episodic-memory plugin's mcp server to search previous conversations
   - Look for any blocking issues or important discoveries
   - Check for established patterns or decisions that affect current work

4. **System Status Check:**
   - Verify MCP connections and agent availability if relevant
   - Check for any pending todos or incomplete workflows
   - Count pending knowledge-vault intake items awaiting promotion:
     `find ~/.claude/vault/_inbox -mindepth 2 -type f -not -name '.gitkeep' | wc -l`
     (files live in per-agent subdirs under `_inbox/`; the top-level `.gitkeep` is not an item).

5. **Propose the Session Plan:**
   - From the handoff, ready beads, and journal context, close with a one-line committed proposal naming the session goal and the first work item, e.g. "Goal: finish chunk streaming. First: bd-123."
   - If the vault intake count from Step 4 is non-zero, include "N intake items pending promotion" in the proposal so the pending items get reviewed within an existing session rhythm.
   - Ask Jerry to confirm or redirect before starting work.
   - Prefer scoping the session to a single bead. If context fills mid-task, write session-handoff.md and suggest a fresh session rather than compacting through the work.
