---
name: thanksforallthefish
description: Use when session is ending to capture status, and lessons learned
---

This session is ending so do the following:

- mcp__mnemosyne__process_thoughts any feelings, thoughts about our process, and lessons learned in this session.
- Create `session_{slug}_{timestamp}.md` in .scratchpad/sessions/ with a summary of our session. If
  `.scratchpad/sessions` directory doesn't exist, create it. Include:
  - A brief recap of key actions
  - Efficiency insights
  - Possible process improvements
  - Total number of conversation turns
  - Any other interesting observations or insights.
- Intake sweep: if you made WebFetch/WebSearch calls this session, ask which returned external
  **source material worth keeping** that *you* consumed directly (an article, transcript,
  paper) rather than via a research agent that already stubbed it — and route those to the
  vault before handoff. For each, write an intake stub per the **Intake item** contract in
  `~/.claude/vault/_system/schemas.md` to `~/.claude/vault/_inbox/session-lead/<source-slug>.md`
  (`agent_id: session-lead`, `provenance: agent-proposed`, `status: pending-promotion`); read
  the existing atlas entry for the concept first, if any, so the stub adds rather than
  duplicates. Skip anything already stubbed this session, and skip entirely if nothing external
  was worth keeping.
- Update `session-handoff.md` with the current status of the project, and the next step to pursue.
- Verify the git repository state for the project, and that there are no uncommitted changes.
- Capture any issues or tasks that need to be dealt with in a kata issue if one doesn't exist
  for it already. See `kata create --help`
