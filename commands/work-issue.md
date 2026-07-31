---
name: work-issue
description: loop for working kata issues
---

Take the next ready kata issue (`kata next`) that does not carry a `needsinfo` label.

**Skip `needsinfo` issues.** They are waiting on `triage-issue` or on Jerry, not on you. Passing
over them is the whole point of the label — re-examining one and re-applying the label every cycle
is a loop that makes no progress and buries the issue under identical comments.

If the issue has the information needed to work it, claim it (`kata claim <ref>`) and then work it
using `/super-do`. Claiming is atomic and fails when another loop already owns the issue; on
failure, move to the next ready issue rather than proceeding unclaimed.

If the issue does not have the information needed, do not guess and do not fill the gap by
inventing a decision. Comment saying specifically what is missing and what would resolve it, add
the `needsinfo` label, and move to the next ready issue.

If there are no ready issues without a `needsinfo` label, say "All ready issues for this project
are completed."
