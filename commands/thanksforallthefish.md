---
name: thanksforallthefish
description: Use when session is ending to capture status, and lessons learned
---

This session is ending so do the following:

- mcp__mnemosyne__process_thoughts any feelings, thoughts about our process, and lessons learned in this session.
- Create `session_{slug}_{timestamp}.md` in .claude/scratchpad/sessions/ with a summary of our session. If
  `.claude/scratchpad/sessions` directory doesn't exist, create it. Include:
  - A brief recap of key actions
  - Efficiency insights
  - Possible process improvements
  - Total number of conversation turns
  - Any other interesting observations or insights.
- Update `session-handoff.md` with the current status of the project, and the next step to pursue.
- Verify the git repository state for the project, and that there are no uncommitted changes.
- Capture any issues or tasks that need to be dealt with in a bead if one doesn't exist for it
  already. See `bd create --help`
