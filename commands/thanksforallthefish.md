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
- Vault tree check: if this session wrote anything under `~/vault` — a stub from the sweep
  above, a promotion, an ingest — confirm `git -C ~/vault status --porcelain` is empty before
  handoff. An uncommitted change there is not merely untidy: a dirty tree is the *first*
  precondition `/manage-vault` stops on, so anything left behind silently halts every
  subsequent firing of the loop instead of being picked up by it. Commit deliberately —
  `promote.py` regenerates the tracked `_surface/index.html`, so stage that alongside whatever
  atlas or intake change produced it, and never sweep in another session's staged work.
- **Rewrite `session-handoff.md` — do not prepend a section to it.** The handoff answers one
  question for the next session: *what is in flight, and where do I look.* It is a pointer, not
  a ledger, and it should stay under roughly a hundred lines. It usually already exists from the
  prior session, so **Read it before you Write it** — a bare Write is blocked by the harness and
  costs a round-trip at the point in the session where context is thinnest.
  - Everything this session learned already has a home: a finding belongs on the kata issue it
    is about, the narrative belongs in the `.scratchpad/sessions/` record you just wrote, and a
    general lesson belongs in the vault or auto-memory. The handoff cites those; it does not
    restate them.
  - Preserving a prior session's section is never the reason to keep it. That content is in the
    session record and in kata, both of which outlive this file.
  - **Write no state the next session can derive.** No SHAs, no commit counts, no test counts,
    no ingest-backlog numbers, no lists of open issues copied out of kata. Write the *query*
    instead — `kata ready --no-label deferred`, `git -C <repo> status`. Every one of those
    numbers is stale the moment the session ends, and a stale number read as fresh is the
    failure mode: it is how a session declines to push work that is already pushed, or believes
    pushed work is safe when it is not.
  - If a live next-step has no kata issue, **file one and cite the ref** rather than describing
    the work in the handoff. An item that lives only in this file is an item that dies with it.
- Verify the git repository state for the project, and that there are no uncommitted changes.
  Record **what landed** — the branch and the commit list, cited upstream-style — in the
  `.scratchpad/sessions/` record, which is dated and never rewritten. It is the right home for a
  commit list; the handoff is not. Never write an absolute "N commits ahead of origin" count
  anywhere: the remote can advance from outside the session, so the next startup must derive the
  relationship itself (it does; see `/talktomegoose` step 2).
- Capture any issues or tasks that need to be dealt with in a kata issue if one doesn't exist
  for it already. See `kata create --help`
