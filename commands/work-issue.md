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
Its pre-flight (premise, already-landed, blockers, sibling claim) runs before any edit; a failed
check closes or skips the issue and you take the next one.
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

**If Jerry rules on the spot rather than leaving it labelled, transcribe it under a different
actor than your claims:**

```
kata comment <ref> --as jerry-via-claude \
  --body "RULING (Jerry, <session id or context>): chose <option> because <reason>."
```

Your `claude-work-issue-<suffix>` actor marks your own reasoning, not his ruling. Why this actor
and no other: CLAUDE.md, "Transcribing Jerry-sourced content" — the canonical statement of the
convention, including the `CORRECTION`/`CONTEXT` prefixes for Jerry-sourced facts that are not
rulings.

If every ready issue carries one of the two labels, say "All ready issues for this project are
completed."

## The pre-merge gate is mandatory

**No branch this loop produces merges without `/verify-branch <target-branch> <kata#ref>`
returning PASS.** The gate itself lives in `/super-do`, between the last completed task and
`finishing-a-development-branch`, because that is where the merge actually happens — this loop
delegates the work and never merges on its own. Read the gate's terms there; they are not
restated here, so there is one place they can drift out of date.

What this loop owns is refusing to route around it. If `/super-do` returns without a recorded
gate verdict, treat the branch as unmerged and BLOCK — do not merge it yourself, do not close
the issue, and do not re-run the gate to get a second answer. A BLOCK becomes a `needs-review`
label plus the defect list on the issue, and the loop moves to the next ready issue. That is a
normal outcome, not a loop failure.

## Worktree teardown

When the issue was worked in a worktree, teardown has a precondition. Run it in order:

0. Confirm the `/verify-branch` gate returned PASS. No PASS, no merge, no teardown.
1. Rebase onto the target branch **from inside the worktree**, resolving conflicts there.
2. Merge into the target branch from the main checkout.
3. Verify **both**, and stop on either:
   - `git branch --merged <target>` lists the worktree branch — the commits are on the target.
   - `git -C <worktree> status --porcelain` is empty — nothing uncommitted, untracked scratch
     included. Commit it or explicitly stash it; do not leave it to the guard.
4. Only then `ExitWorktree{action: "remove", discard_changes: true}`.

If either check in step 3 fails, **stop and report** — do not remove. Step 3 is the only thing
standing between you and destroying finished work. It is never skippable.

**Step 3 is the safety property, not the harness guard.** The two checks exist because
`discard_changes: true` deletes the branch *and* the working tree, while the guard that would
otherwise stop you is unreliable in one direction and silent in the other:

- Its commit count is commits not reachable from `origin/<default-branch>` — divergence from the
  *remote*, not unmerged work. Local merges never clear it; only a push does. So it fires on
  branches that are fully merged and safe, and its message ("Removing will discard this work
  permanently") is wrong in exactly that case. The `branch --merged` check is what tells you the
  commits are safe.
- Its uncommitted-files clause is accurate, and it is the clause you are overriding when you
  pass the flag. Nothing else will warn you. The `status --porcelain` check is what makes the
  override harmless.

Never pass `discard_changes: true` to skip step 3, or because the guard fired and you want past
it. Verify both, then pass it; the flag is what you use *after* verifying, not instead of.

Measured 2026-08-16 over every session transcript (kata claudes-home `qcqb`): 118 refusals —
93 cited commits alone, 22 cited commits plus uncommitted files, 3 cited uncommitted files
alone. Two of them were checked against `git rev-list --count origin/<default>..<branch tip>`
and matched exactly (32 and 34, hexwalker session `10988fbb`); the rest were classified from
the refusal text, not individually re-derived. This is why "just commit or stash before
teardown" is not the fix: it addresses 3 of 118.
