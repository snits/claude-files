---
name: orchestrate-issues
description: loop for working kata issues by dispatching a fresh agent per issue
---

Work ready kata issues by dispatching one agent per issue. You are the orchestrator: you own
selection, claiming, the ledger, and the escalation batch. **You never implement and you never
review.** Both belong to the dispatched agent and to the review gate inside `/super-do`.

Use this instead of `/work-issue` when working more than two or three issues in a run.
`/work-issue` does the work in its own session, so by the fifth issue it is carrying five issues
of context and fighting compaction. Here each issue gets clean context and you hold only outcomes.

## Preconditions

Check before the first dispatch, and stop rather than work around either:

- **The working tree is clean** (`git status --porcelain` empty). A dirty tree usually means a
  live session in that repo. projstat does not report this.
- **A target branch is named.** Every dispatch passes it to `/super-do` as the merge target. Do
  not default to `main` silently — ask if it was not given.

## Selecting

```
kata next --unowned --no-label needsinfo --no-label needs-decision --no-label deferred
```

Filter data-side, not by reading labels off the result and deciding. A `needsinfo` issue is
waiting on `triage-issue` and a `needs-decision` issue is waiting on Jerry; neither is waiting on
you, and re-examining one every cycle buries it under identical comments. The filter belongs in
the query because that is the only version that cannot be forgotten mid-run.

## Claiming

Claim on the agent's behalf before dispatching, with an actor string unique **per issue**:

```
kata claim <ref> --as claude-orch-<run-suffix>-<ref>
```

Pick `<run-suffix>` once at loop start. Claiming is atomic per distinct actor string, and
`KATA_AUTHOR=claude` is set in the environment — so a same-owner claim is a silent no-op rather
than a conflict, and two runs sharing one string would each "successfully" claim issues the other
holds. Confirm once with `kata whoami --as <string>` (expect `source=flag`).

On a failed claim, move to the next issue. Never dispatch against an unclaimed issue.

## Dispatching

One agent per issue. Its task is `/super-do <ref> <target-branch>` — that command carries the size
gate, TDD, the review gate, and the merge, so do not restate any of it in the dispatch.

- **Each agent gets its own worktree.** They edit in parallel and would otherwise collide.
- **Concurrency defaults to 1.** Raise it only deliberately: parallel agents in one repo routinely
  touch the same files, and the conflicts surface at merge, where they are yours to resolve rather
  than the agent's. Concurrency multiplies the escalation rate without reducing the total, so it
  helps when the constraint is wall-clock and hurts when the constraint is Jerry's attention.
- **Model tier:** default to the session tier for the agent. Drop to a cheaper tier only for
  issues already fully specified and mechanical, and say why in the ledger.

## Merging — the agent delivers a branch, you land it

`/super-do` assigns itself the `--no-ff` merge, but a worktree-isolated agent cannot perform it:
the target branch is checked out in the primary worktree, and `git worktree add <path> <target>`
refuses a branch already checked out elsewhere. **Tell each agent in its dispatch to stop at a
reviewed branch and leave the merge to you.** Otherwise it burns its budget discovering this and
escalates on plumbing.

Landing is CLAUDE.md's worktree-merge sequence, and all three steps matter:

```
git -C <agent-worktree> rebase <target>          # rebase FROM INSIDE the worktree
git -C <repo-root> merge --no-ff <agent-branch>  # then merge from the root
git -C <repo-root> worktree remove <agent-worktree>
```

The rebase comes first so the merge cannot produce conflict state in the project root — that is
what CLAUDE.md's "NEVER run `git merge` from the main checkout **and resolve conflicts there**"
forbids. The merge itself from the root is prescribed, not forbidden; the rule reads as a
prohibition only when its second clause is dropped. If the rebase reports conflicts, resolve them
in the worktree or escalate — never carry them to the root.

Verify the landing rather than assuming it: `<target>..<agent-branch>` empty and
`git diff <target> <agent-branch>` empty. Cite the merge commit upstream-style in the ledger.

## Escalation — record it, do not resolve it

An agent returns escalated when `/super-do` hits its 3-cycle review cap, or when the issue is
missing a fact (`needsinfo`) or a ruling (`needs-decision`).

**Record the escalation and move to the next issue.** Do not adjudicate it, do not re-dispatch it,
do not fix it yourself. `/super-do` is explicit that an implementation three reviews could not
clear is a design question surfacing as a review failure, and it needs a person rather than a
fourth attempt. You reviewing it would be that fourth attempt, and it would make you both the
proposer and the acceptor of the same work.

What you *do* add is batching: hold every escalation until the run ends and deliver one
consolidated report. Five escalations as one review session is a materially different cost to
Jerry than five interruptions, and batching is the only part of the escalation path that is yours.

## Stopping

Stop at the issue cap, when every ready issue carries a skip label, or on the first
orchestrator-level failure — an unresolvable claim, a dirty tree, a merge you cannot complete.
An orchestrator that works around its own broken precondition is worse than one that stops.

Report a ledger: per issue, the outcome (merged / escalated / skipped) and one line of why.
Then the totals, the escalation rate, and the run cost. The escalation rate is the number that
decides what concurrency is worth using next time, so state it even when it is zero.

If nothing was ready, say "No ready kata issues for this project."
