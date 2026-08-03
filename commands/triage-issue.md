---
name: triage-issue
description: loop for triaging kata issues for a codebase
---

Work the open kata issues carrying a `needsinfo` label. Each one is blocked because `work-issue`
could not proceed without an answer; your job is to find the answer, or to establish that no amount
of looking will produce one and route the issue to Jerry instead.

**Only `needsinfo`.** An issue labelled `needs-decision` *and not* `needsinfo` is waiting on Jerry
— re-examining one and re-stating its options is the no-progress loop the labels exist to prevent.
Leave it.

An issue carrying **both** is yours for the `needsinfo` half only: establish the fact, cite it,
remove `needsinfo`, and leave `needs-decision` in place. That is the point of the pair — the fact
often narrows the choice, and handing Jerry a decision with its facts already pinned is most of
the work.

## The gap is a fact you can establish

Add it to the issue as a comment, then remove the `needsinfo` label so `work-issue` picks it up on
its next pass. Cite where it came from — a file and line, a commit, an issue ref — so the next
reader can check it rather than trust it.

Prefer the authoritative lookup over a search. "Nothing in this package does X" from a proxy check
fails in the direction that makes absence look confirmed; query the thing that would contain the
answer and read its status.

## The gap is a choice only Jerry can make

Relabel in place. Do not create a second issue for the decision, and do not leave `needsinfo` on:

```bash
kata label rm <ref> needsinfo
kata label add <ref> needs-decision
kata comment <ref> --body "..."
```

The comment states the options and what each would imply, with a recommendation and the reason for
it. An issue whose entire content is the decision needs no second issue to hold it — copying the
body across to satisfy a protocol is duplication, and the ceremony is why this path used to get
skipped.

**Split into a separate decision issue only when the choice gates more than one issue.** That is
when a blocker link earns its cost, because the decision has to be discharged once and observed
from several places:

```bash
kata create "<the decision>" --body-file <options>
kata label add <new-ref> needs-decision
kata edit <blocked-ref> --blocked-by <new-ref>
```

Do not use `needs-review` for either case. It means work happened and should be looked at before
closing — a different state with a different consumer.

## The gap is a fact neither of us can reach from here

A capture from hardware we do not have, a measurement nobody has taken. This is not a decision, so
`needs-decision` is the wrong label, and it is not obtainable, so leaving `needsinfo` on invites
the next triage pass to re-derive the same dead end.

Prefer an event trigger over a label: if an existing issue would produce the missing fact when it
lands, `kata edit <ref> --blocked-by <that-issue>` and drop `needsinfo`. The issue then returns
exactly when the fact exists. File the producing issue first if there isn't one.

If no issue could produce it and none is worth filing, defer it —
`python3 ~/.claude/scripts/kata_defer.py --set <ref> --days N` — and say in a comment what would
bring it back. A bare `needsinfo` with nothing that could ever clear it is the worst outcome: it
reads as triageable forever.

If no issues carry a `needsinfo` label, say "No issues awaiting triage in this project"
