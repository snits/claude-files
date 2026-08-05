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
   - **Derive the remote relationship; never quote it from the handoff.** A handoff's "N commits
     ahead of origin" is a dated snapshot, and the remote can move from outside the session:
     ```
     B=$(git branch --show-current)
     if [ -z "$B" ]; then echo "GIT: detached HEAD, no upstream relationship"
     elif ! git rev-parse --verify -q '@{upstream}' >/dev/null; then echo "GIT: branch $B has no upstream"
     else
       git fetch --quiet origin
       echo "GIT $B vs $(git rev-parse --abbrev-ref '@{upstream}'): ahead $(git rev-list --count '@{upstream}..HEAD'), behind $(git rev-list --count 'HEAD..@{upstream}')"
     fi
     ```
     The `git fetch` is load-bearing, not hygiene: `rev-list` reads `refs/remotes/origin/<branch>`,
     which is only as fresh as the last fetch and will happily report "in sync" against a remote
     that has advanced. Report the live numbers, and say so explicitly in the no-upstream and
     detached-HEAD cases rather than printing nothing — silence there reads as "in sync".
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
     `find ~/vault/_inbox -mindepth 2 -type f -not -name '.gitkeep' | wc -l`
     (files live in per-agent subdirs under `_inbox/`; the top-level `.gitkeep` is not an item).
   - Count promoted vault material still awaiting the ingest loop:
     `python3 ~/vault/_system/promote.py --backlog | wc -l`
     (source material that landed in `intake/` but has not yet been folded into an atlas
     entry — see the ingest loop in `~/vault/_system/routing.md`).
   - Refresh the vault reading surface so it cannot drift from the atlas unnoticed:
     `python3 ~/vault/_surface/generate.py --if-stale`
     Report its `SURFACE CURRENT` / `SURFACE REGENERATED` line next to the two counts above —
     together they say whether new material has reached the atlas yet. A current surface with
     a non-empty ingest backlog means promoted material is still stuck in `intake/`, which is
     work to do, not a stale page.
   - Surface deferred kata issues whose defer date has arrived:
     `python3 ~/.claude/scripts/kata_defer.py --due`
     Deferred issues are hidden from `kata ready` by the `deferred` label, so this is the only
     thing that brings them back. Report any `DEFERRED UNDATED` line too — a `deferred` label
     with no `defer_until` never resurfaces on its own.
   - Surface kata issues waiting on a ruling from Jerry:
     `kata list --label needs-decision --agent`
     These are blocked on a choice, not on work — `work-issue` and `triage-issue` both skip them
     by design, so nothing else brings them back. Report the count and the titles. If any are
     present, offer to walk them: each needs its options stated and a ruling recorded as a comment
     before the label comes off.
   - Check whether a retrospective is due:
     `S=~/.claude/retro/last-retro; if [ -f "$S" ]; then echo "RETRO last=$(cat $S) days_ago=$(( ( $(date +%s) - $(date -d "$(cat $S)" +%s) ) / 86400 ))"; else echo "RETRO never run"; fi`
     Report the line. There is no scheduler for the retro — this check is the only thing that
     surfaces it.
   - Check this project's memory index for orphans and truncation:
     ```
     M=~/.claude/projects/$(pwd | tr '/.' '--')/memory
     if [ ! -d "$M" ]; then echo "MEMORY: no memory dir for this project yet"; else (
       cd "$M" || exit
       N=$(find . -maxdepth 1 -name '*.md' ! -name MEMORY.md -printf '%f\n' | wc -l)
       if [ ! -f MEMORY.md ]; then
         echo "MEMORY.md absent, $N memory files"
         find . -maxdepth 1 -name '*.md' -printf '%f\n' | sort
       else
         echo "MEMORY.md $(wc -c < MEMORY.md) bytes (truncates near ~24986), $N files"
         comm -3 <(find . -maxdepth 1 -name '*.md' ! -name MEMORY.md -printf '%f\n' | sort) \
                 <(grep -oE '\]\([a-zA-Z0-9_.-]+\.md\)' MEMORY.md | tr -d '](' | sed 's/)//' | sort -u)
       fi
     ) fi
     ```
     Left column = a memory file no index line points at; it never loads, ever. Right column =
     an index line whose file is gone. Both print nothing when clean. An oversized `MEMORY.md`
     is silently truncated on load, which orphans whatever falls off the end. Report the size
     line and any orphans; fix them in this session rather than deferring — a memory that
     never loads is the same as one never written.

     A new project reports `no memory dir` or `MEMORY.md absent, 0 memory files` — that is the
     expected state, not a problem to fix. `MEMORY.md absent` with a nonzero count *is* a
     problem: every one of those files is orphaned, so the listing that follows is the full set.

5. **Propose the Session Plan:**
   - From the handoff, `kata ready --no-label deferred` output, and journal context, close with a one-line committed proposal naming the session goal and the first work item, e.g. "Goal: finish chunk streaming. First: kata 12gg."
   - Use `--no-label deferred` for the ready listing; drop the flag only when deliberately reviewing the deferred set.
   - If either vault count from Step 4 is non-zero, include it in the proposal so the work
     happens within an existing session rhythm: "N intake items pending promotion" and/or
     "N promoted items awaiting ingest". Promotion is not the last step — promoted material
     only pays off once it is folded into an atlas entry, so surface both.
   - If any deferred issues came due, name them in the proposal too — a defer that arrives
     and goes unmentioned is the same lost reminder that deferring was meant to prevent.
   - If the retro check reports never-run or more than 7 days ago, offer a retro (`/retro`)
     as an option in the proposal. Offer it; don't start one unasked.
   - Ask Jerry to confirm or redirect before starting work.
   - Prefer scoping the session to a single kata issue. If context fills mid-task, write session-handoff.md and suggest a fresh session rather than compacting through the work.
