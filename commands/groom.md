---
name: groom
description: loop for cleaning up stale kata issues
---

Work the open kata issues oldest first, checking each against the current state of the code to see
whether it still describes something real.

**Only consider issues older than 7 days.** Anything more recent was filed with knowledge of the
code as it stands and is not stale — a freshly filed issue that reads as redundant means you are
missing context the author had, not that the issue is obsolete.

If the issue is still relevant but its details have gone stale — a path that moved, a line number
that drifted, a fix that landed partway — update it with current information and say what changed.
That is this loop's main job, and it is the low-risk half.

Closing is the destructive half and this is the only loop that does it. Close an issue only when
you can show it: the commit that fixed it, the code that no longer exists, the decision that
superseded it. Put that evidence in the close message with the appropriate typed flag
(`--commit`, `--duplicate-of`, `--superseded-by`). Two things that are not evidence of staleness:
an issue being old, and an issue being hard to understand. If you believe an issue is obsolete but
cannot demonstrate it, comment your reasoning and label it `needs-review` instead of closing —
leaving a stale issue open costs a line in `kata ready`, while closing a live one loses the work.

If nothing is stale, say "No stale kata issues in this project"
