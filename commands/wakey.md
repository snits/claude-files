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
   - If the project has been dormant (handoff date or last commit more than a few weeks old), diff the project framing embedded in `.claude/agents/` (and any other embedded-context surfaces) against CLAUDE.md and the most recent design decisions. Decisions made in the last sessions before dormancy often never got swept into agent prompts — surface any drift found and fix or file it before starting work.
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
   - Count promoted vault material still awaiting the ingest loop:
     `python3 ~/.claude/vault/_system/promote.py --backlog | wc -l`
     (source material that landed in `intake/` but has not yet been folded into an atlas
     entry — see the ingest loop in `~/.claude/vault/_system/routing.md`).

5. **Propose the Session Plan:**
   - From the handoff, `kata ready` output, and journal context, close with a one-line committed proposal naming the session goal and the first work item, e.g. "Goal: finish chunk streaming. First: kata 12gg."
   - If either vault count from Step 4 is non-zero, include it in the proposal so the work
     happens within an existing session rhythm: "N intake items pending promotion" and/or
     "N promoted items awaiting ingest". Promotion is not the last step — promoted material
     only pays off once it is folded into an atlas entry, so surface both.
   - Ask Jerry to confirm or redirect before starting work.
   - Prefer scoping the session to a single kata issue. If context fills mid-task, write session-handoff.md and suggest a fresh session rather than compacting through the work.
