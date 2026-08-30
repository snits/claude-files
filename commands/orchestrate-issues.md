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
kata next --unowned --no-label needsinfo --json
```

Then **read the selected issue's labels and skip it yourself** if it carries `needsinfo`,
`needs-decision`, or `deferred`. Say in the ledger that you skipped it and which label did it.

The check is redundant with the query on purpose, because the query cannot be trusted to do it.
**kata honors only the *first* `--no-label`; every later one is accepted without error and
ignored** (`1ycz` — huma decodes the param non-exploded, so it reads one occurrence and splits
that one on commas). Three flags filter one label. Do not "simplify" this back into a repeatable
filter, and do not reach for the quoted-CSV form that does currently work
(`--no-label '"a,b,c"'`) — it depends on shell quoting surviving into pflag, and it fails *open*
the day kata adds the `explode` tag, silently filtering nothing.

One flag is always honored because it is always first, so `needsinfo` stays in the query and the
other two live in the post-check. That split fails closed under either kata behavior: a label the
filter missed still stops the dispatch.

Skipping matters because none of these is waiting on you. A `needsinfo` issue is waiting on
`triage-issue` and a `needs-decision` issue is waiting on Jerry; re-examining one every cycle
buries it under identical comments. A `deferred` issue was snoozed deliberately and its date has
not arrived.

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
gate, TDD, and the review gate, so do not restate any of those in the dispatch.

**Two things it normally does are yours instead, and the dispatch must say so:** the `--no-ff`
merge and the `/verify-branch` gate. Both are covered under "Merging" below; name them as
exclusions in the brief so the agent stops at a reviewed branch rather than burning turns
discovering it cannot merge.

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

### The gate travels with the merge

**`/verify-branch` is mandatory here, and it is yours to run — not the agent's.**

`/super-do` places the gate before its own merge. Under orchestration the merge moves to you, so
the gate moves with it. **Tell each agent in its dispatch to skip `/verify-branch` along with the
merge**, for the same reason it skips the merge: it cannot do the thing the gate gates.

Run it **after the rebase and before the merge**, not earlier. The rebase rewrites the branch's
commits and can move the merge base, so a verdict produced before it was reached against a diff
that no longer exists. The gate has to see what actually lands. Concretely, the sequence below is
not reorderable:

```
git -C <agent-worktree> rebase <target>          # rebase FROM INSIDE the worktree
/verify-branch <target> <kata#ref>               # gate the post-rebase diff
git -C <repo-root> merge --no-ff <agent-branch>  # then merge from the root
git -C <repo-root> worktree remove <agent-worktree>
```

**This does not make you the reviewer.** Running the gate is not adjudicating it: you dispatch
three auditors, read their artifacts, and act on the verdict mechanically — PASS lands, BLOCK
escalates. You never decide whether a finding is really a defect, never fix one, and never
re-run the gate hoping for a better answer. That distinction is what keeps "you never implement
and you never review" true while the gate sits in your half of the flow. If you find yourself
weighing whether a finding matters, you have crossed into reviewing — stop and escalate instead.

**A BLOCK is an escalation like any other**: record it, batch it, move to the next issue. Do not
fix the defects and re-run, and do not merge past it. The branch stays unmerged and the worktree
stays put — tearing down a worktree whose branch never landed destroys the work. Label the issue
`needs-review` and carry the numbered defect list into the batch report.

**No verdict is a BLOCK.** A missing artifact or an auditor that returned nothing is recorded as
"gate returned no verdict", never as a pass.

That sequence is CLAUDE.md's worktree-merge order with the gate inserted, and every step matters.

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

### Recording Jerry's answer — a different actor than your claims

When Jerry rules on a batched escalation and you write that ruling into kata, the comment is his
decision and your transcription. Record both halves:

```
kata comment <ref> --as jerry-via-claude \
  --body "RULING (Jerry, <session id or context>): chose <option> because <reason>."
```

Not your `claude-orch-<run-suffix>` actor, which marks your own reasoning. The compound form is
greppable — `kata show <ref> --agent | grep author=` separates rulings from findings. Why this
actor and no other, the incident behind it, and the no-retro-attribution rule: CLAUDE.md,
"Transcribing Jerry-sourced content" — the canonical statement of the convention.

## Stopping

Stop at the issue cap, when every ready issue carries a skip label, or on the first
orchestrator-level failure — an unresolvable claim, a dirty tree, a merge you cannot complete.
An orchestrator that works around its own broken precondition is worse than one that stops.

Report a ledger: per issue, the outcome (merged / gate-blocked / escalated / skipped) and one
line of why. For every issue that reached the gate, record its verdict and the auditor that
blocked — a gate that silently passes everything looks exactly like a gate that never ran.
Then the totals, the escalation rate, and the run cost. The escalation rate is the number that
decides what concurrency is worth using next time, so state it even when it is zero.

If nothing was ready, say "No ready kata issues for this project."
