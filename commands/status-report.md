**Cross-Project Status Report**

Scan all beads-enabled projects and generate a prioritized status report.

## Step 1: Discover Projects

Find all directories with a `.beads/` subdirectory in these locations:
- `~/devel/*/`
- `~/dev/rhkmaint-tools`
- `~/claudes-home`
- `~/desert-island`

Use parallel bash calls to check for `.beads/` efficiently.

## Step 2: Gather Data Per Project

For each beads-enabled project, collect the following **in parallel** (use parallel tool calls across projects):

1. **Bead summary**: Run `bd stats` or `bd list` in the project directory to get:
   - Count of open, in_progress, closed beads
   - Count of blocked beads
   - The highest-priority unblocked bead (ID + title + priority)
2. **Last git activity**: Run `git -C <project-path> log -1 --format='%ci'` to get the most recent commit date
3. **Session handoff**: Check if `<project-path>/session-handoff.md` exists

## Step 3: Classify Into Tiers

- **Active**: Has git commits within the last 7 days OR has any `in_progress` beads
- **Simmering**: Has open beads but no git commits in the last 7 days and no in_progress beads
- **Dormant**: No open beads — just count these, don't detail them

## Step 4: Rank Within Tiers

Sort projects within each tier by:
1. Highest-priority unblocked bead (P0 first, then P1, P2, P3, P4)
2. Tie-break: most recent git commit date (more recent = higher rank)

## Step 5: Format Output

Present results in this format:

```
## Active Projects
1. **project-name** (P2 top priority | 3 open / 7 closed | 2 blocked)
   → Next: beads-xxx "Most important unblocked bead title"
   📋 Handoff: one-line summary from session-handoff.md if it exists

2. **project-name** ...

## Simmering Projects
1. **project-name** (P2 top priority | 1 open / 4 closed)
   → Next: beads-yyy "Bead title"

## Dormant (N projects with no open beads)

## Suggested Focus Order
1. project-name — reason (e.g., "P1 unblocked, only 2 tasks remaining")
2. project-name — reason
3. project-name — reason
```

## Step 6: Suggested Focus Order

Pick the top 3-5 projects to suggest working on. Rank by:
- Priority of the top unblocked bead
- Momentum (recent activity)
- Proximity to completion (low open/closed ratio means close to done — nudge these)

For each suggestion, write a short one-line rationale explaining WHY it's worth focusing on.

## Notes

- Use `bd` commands with `--db-path <project>/.beads/beads.db` or `cd` into the project to run `bd` scoped to that project
- Blocked beads are mentioned in summaries but never suggested as focus items
- Keep the report concise — this is a dashboard, not a deep dive
- If a project has a session-handoff.md, read the first few lines for context on where things left off
