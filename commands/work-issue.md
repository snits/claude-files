---
name: work-issue
description: loop for working kata issues
---

Take the next ready kata issue (`kata next --unowned`) that carries neither a `needsinfo` nor a
`needs-decision` label.

**Skip both.** A `needsinfo` issue is waiting on `triage-issue`; a `needs-decision` issue is
waiting on Jerry. Neither is waiting on you. Passing over them is the whole point of the labels —
re-examining one and re-applying the label every cycle is a loop that makes no progress and buries
the issue under identical comments.

If the issue has the information needed to work it, claim it and then work it using `/super-do`.
On a failed claim, move to the next ready issue rather than proceeding unclaimed.

**Claim with a per-instance actor: `kata claim <ref> --as claude-work-issue-<random-suffix>`.**
Pick the suffix once at loop start and reuse it for every claim in that run. Claiming is atomic
*per distinct actor string* — not per session, and not per loop type. `KATA_AUTHOR=claude` is set
in the environment, so every Claude agent that does not override it resolves to the same actor,
and a same-owner claim is a silent no-op rather than a conflict.

The suffix must be unique per *running instance*, not per loop name: two concurrent `/work-issue`
loops both passing `--as claude-work-issue` collide exactly as if neither had passed `--as` at
all. Confirm the actor resolved as intended with `kata whoami --as <string>` (expect
`source=flag`).

If the issue does not have what you need to work it, do not guess and do not fill the gap by
inventing a decision. Comment saying specifically what is missing and what would resolve it, label
it, and move to the next ready issue. **Which label depends on what kind of gap it is:**

- **`needsinfo` — a fact is missing, and someone could go get it.** It lives in the code, the git
  history, the design docs, another issue, or a capture. You are not the one to fetch it right
  now, but `triage-issue` can.
- **`needs-decision` — a choice is unmade, and only Jerry can make it.** Two or more defensible
  options exist and picking between them is not a research question. No amount of reading resolves
  it.

Judge the gap, not the phrasing. An issue can state its options in full, argue them to a
conclusion, and still be a `needs-decision` — a body that already contains the answer is not
missing information, it is missing a ruling. Do not reach for `needsinfo` because it is the
habitual label; if your own comment says "Jerry needs to decide", the label is `needs-decision`.

Some issues carry both: a fact is missing *and* a choice depends on how that fact lands. Label
both, and say in the comment which one has to resolve first.

If every ready issue carries one of the two labels, say "All ready issues for this project are
completed."

## Worktree teardown

When the issue was worked in a worktree, teardown has a precondition. Run it in order:

1. Rebase onto the target branch **from inside the worktree**, resolving conflicts there.
2. Merge into the target branch from the main checkout.
3. Verify: `git branch --merged <target>` lists the worktree branch.
4. Only then `ExitWorktree{action: "remove"}`.

If step 3 does not list the branch, **stop and report** — do not remove. `ExitWorktree` with
unmerged commits is a request to destroy finished work; the harness guard is currently the only
thing refusing it, and it has refused three times in one loop session with 1, 13, and 20
unmerged commits on the branch.
