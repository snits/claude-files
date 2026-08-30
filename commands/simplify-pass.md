---
name: simplify-pass
description: loop for finding simplification candidates in hotspot code and inaccurate comments, filed as kata issues
---

Find simplification candidates in the codebase and file them as kata issues. This loop finds and
reports. It does not edit code — `work-issue` is the only loop that changes code. That separation
is what keeps a behavior-preserving-in-theory rewrite from reaching the repo without passing
triage. (The built-in `/simplify` command fixes in place, but it is diff-scoped; this pass is
repo-scoped, where fixes deserve the full review cycle.)

Read the open issues first so you file additions, not duplicates. Title issues with a
`simplify:` prefix so the pass that found them stays identifiable later.

## Phase 0 — Target selection (hotspots, not the whole repo)

Complexity in a file nobody touches is nearly free; complexity in a file touched weekly taxes
every change. Rank files by churn:

```
git log --format= --name-only --since=1year | sort | uniq -c | sort -rn | head -30
```

Cross that against size/complexity (line count, nesting depth — a quick read is fine; no need
for a metrics tool). Take the **top 5–10 files** that are both high-churn and complex as this
cycle's scope. Skip generated files, vendored code, and lockfiles. State the selected list and
the churn counts in your first issue or cycle note so the targeting is auditable.

If a previous `simplify-pass` cycle note exists (check open `simplify:` issues for one), start
from the next hotspots down the list rather than re-reviewing the same files.

## Phase 1 — Four angles per target file

Review each target file against the four angles below (same angles as the built-in `/simplify`,
applied to whole files instead of a diff). Every finding needs `file:line`, a one-line summary,
and the **concrete cost** — what is duplicated, wasted, or harder to maintain. No style
preferences, no vague "could be cleaner."

- **Reuse** — code that re-implements something the codebase already has. Grep shared/utility
  modules before claiming it; name the existing helper to call instead.
- **Simplification** — redundant or derivable state, copy-paste with slight variation, deep
  nesting, dead code. Name the simpler form that does the same job.
- **Efficiency** — redundant computation or repeated I/O, independent operations run
  sequentially, blocking work on startup or hot paths. Name the cheaper alternative.
- **Altitude** — special cases layered on shared infrastructure where generalizing the
  underlying mechanism would be the deeper fix.

**Altitude findings route differently.** "This is a bandaid; the mechanism should generalize" is
often a design ruling wearing a cleanup label. If two defensible depths exist, file it with the
options argued and label it `needs-decision` — do not file it as a plain fix for `work-issue`
to implement on its own judgment.

## Phase 2 — The coverage gate goes in the issue

Behavior-preserving is only verifiable where tests exist. For every finding, check whether the
code it touches has test coverage (a test that exercises the function is enough; a full coverage
run is not required). Record the answer in the issue body:

- **Covered** — name the test(s). The issue is workable as filed.
- **Uncovered** — the issue must say so, and its first task is *write a characterization test,
  then simplify*. An uncovered simplification with no test step is not workable; do not file it
  without one.

This line in the body is what stops a downstream implementer from "simplifying" untested code on
vibes.

## Phase 3 — Comment accuracy sweep (same target files)

Check each comment's claim against the code it describes. Four verdicts:

- **Stale** — asserts something the code no longer does. File it; quote the comment and cite the
  line that contradicts it.
- **Narrating** — restates what the adjacent code obviously does. File for deletion.
- **Historical** — describes old behavior or the change that landed. File for deletion; git owns
  history.
- **Load-bearing** — states a constraint the code cannot show (why a lock is held, why order
  matters). Keep. File only if the wording is wrong, never for terseness.

The default is asymmetric on purpose: **flagging a comment for deletion requires citing the code
that makes it redundant or wrong; keeping one requires nothing.** The failure mode this guards
against is deleting terse-but-load-bearing comments and adding polite noise.

Batch comment findings per file (one issue per file, listing each comment with its verdict and
citation) rather than one issue per comment.

## Evidence bar

A simplification claim is a claim like any other. "X duplicates Y" needs the grep that found Y;
"this state is derivable" needs the lines it derives from; "this comment is stale" needs the
contradicting line quoted. If you cannot produce the evidence, file it as a question saying what
would settle it, not as a finding.

If nothing is found, say "No simplification candidates in this cycle's hotspots."
