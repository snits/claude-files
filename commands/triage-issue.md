---
name: triage-issue
description: loop for triaging kata issues for a codebase
---

Work the open kata issues carrying a `needsinfo` label. Each one is blocked because `work-issue`
could not proceed without an answer; your job is to find the answer or to make the question
durable and visible.

If you can establish the missing information from the code, the git history, the design docs, or
the other issues, add it to the issue as a comment, then remove the `needsinfo` label so
`work-issue` picks it up on its next pass. Cite where it came from — a file and line, a commit, an
issue ref — so the next reader can check it rather than trust it.

If the missing information is a decision only Jerry can make, or a fact neither of us can reach
from here, do not guess and do not remove the label. Instead:

- Create an issue for obtaining that information, stating the options and what each would imply.
- Wire it as a blocker: `kata edit <blocked-ref> --blocked-by <new-ref>`.
- Label the new issue `needs-review` so it surfaces as awaiting Jerry rather than awaiting work.

Leave the original `needsinfo` label in place in that case — it is what keeps `work-issue` from
picking the issue back up before the answer exists.

If no issues carry a `needsinfo` label, say "No issues awaiting triage in this project"
