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
- Intake sweep: if this session consumed external **source material worth keeping** — an
  article, paper, transcript, or a research synthesis with lasting reference value — route it
  to the vault before handoff. This covers material **agents fetched as well as material you
  fetched yourself**: delegating the research does not delegate the capture, and a session
  whose lead made no WebFetch/WebSearch call of its own is not thereby a session with nothing
  to route.
  - **You consumed it directly** — write an intake stub per the **Intake item** contract in
    `~/vault/_system/schemas.md` to `~/vault/_inbox/session-lead/<source-slug>.md`
    (`agent_id: session-lead`, `provenance: agent-proposed`, `status: pending-promotion`).
  - **An agent consumed it** — `ls ~/vault/_inbox/<agent-id>/` and confirm the stub is on
    disk. Never assume it is: a read-only agent type has no Write tool and returns its stub
    inline for *you* to persist, and an agent dispatched without the intake block was never
    told to stub at all. Both look identical from here — like research that was handled. If
    the stub is missing, persist it yourself per the no-Write fallback in `consulting-agents`
    ("Routing Source Material to the Vault"): save the report, fill `source_url` and `sha256`,
    and write the stub keeping the *researcher's* `agent_id`, not yours.

  Read the existing atlas entry for the concept first, if any, so the stub adds rather than
  duplicates. Skip anything already stubbed this session, and skip entirely if nothing external
  was worth keeping.
- Update `session-handoff.md` with the current status of the project, and the next step to pursue.
  It usually already exists from the prior session, so **Read it before you Write it** — a bare
  Write is blocked by the harness and costs a round-trip at the point in the session where
  context is thinnest.
- Verify the git repository state for the project, and that there are no uncommitted changes.
  In the handoff, record **what landed** — the branch and the commit list — and do **not** write an
  absolute "N commits ahead of origin" count. That number is guaranteed stale by the time it is
  read: the remote can advance from outside the session, so the next startup must derive the
  relationship itself (it does; see `/wakey` step 2). A stale count read as fresh is how a session
  declines to push work that is already pushed, or believes pushed work is safe when it is not.
- Capture any issues or tasks that need to be dealt with in a kata issue if one doesn't exist
  for it already. See `kata create --help`
