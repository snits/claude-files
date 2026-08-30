---
name: verify-branch
description: Pre-merge gate — three concurrent auditors on claims, test discrimination, and scope. Any BLOCK stops the merge.
---

Verify the current branch before it merges. Arguments: `${1}` = target branch (the merge base
side), `${2}` = the qualified kata ref for the issue being worked (`kata#abc4` form).

**Both arguments are required. Do not default `${1}` to `main`** — `/orchestrate-issues` already
rules that a merge target is named, never assumed. **Use the qualified `kata#` form for `${2}`**:
from inside a worktree an unbound workspace resolves to the enclosing git remote's basename
rather than failing, which silently targets another project.

Invoking this command IS the user's request to task subagents. Dispatch the three below without
stopping to ask.

## What this gate is, and is not

This is **one pass, not a loop.** There is no fix-and-retry cycle inside it. It runs once; it
returns PASS or BLOCK; a BLOCK escalates.

It is **not a fourth code-review cycle.** `/super-do`'s review gate asks whether the code is
correct. This asks three different questions the correctness reviewer does not: are the claims
we wrote down true, do the tests actually discriminate, and is the diff traceable to the issue.
A branch that cleared three code reviews can still fail every one of them.

## Establish the base first

```
git merge-base ${1} HEAD
```

Every auditor scopes to `<merge-base>..HEAD`. Compute it once, paste the SHA into all three
briefs, and never let an auditor recompute it — three auditors deriving their own base is three
chances to audit a different diff than the one being merged.

## The three auditors — dispatch concurrently, one message, three Agent calls

All three run in parallel. Each gets `isolation: "worktree"` — they read and (for the mutation
auditor) mutate independently, and a shared checkout makes that unsafe.

Every brief carries, verbatim:

- The merge-base SHA and the target branch.
- The kata ref and the issue body text (paste it — the agent cannot see this conversation, and
  handing it only a ref invites it to invent the scope it is auditing against).
- **The artifact path it must write** (see "Artifacts" below).
- **`file:line` evidence for every finding, and "not found" rather than an inferred mechanism.**
- A `Deviations` section: when an edge case forces it off the brief, take the conservative
  option and record the deviation.

### 1. claim-verifier — Sonnet

**Role:** You are a claims auditor. You establish whether what this branch asserts is true.

**Do not restate the method — invoke the `verify-claims` skill and follow it.** It already
defines the extract / categorize (CODE_CITATION, COMMAND_RESULT, INFERENCE) / verify / table
procedure. This brief supplies only what is branch-specific:

**Extraction sources**, all scoped to `<merge-base>..HEAD`:
- commit messages (`git log <merge-base>..HEAD`) — subject and body
- comments added or changed in the diff (`git diff <merge-base>..HEAD`)
- test names and docstrings for tests added or modified
- the kata issue body and comments pasted into this brief

**Overclaim scan.** Flag absolute or guarantee-shaped language wherever it appears in those
sources — `guaranteed`, `never`, `always`, `impossible`, `compiler-enforced`, `cannot`,
`ensures`, `all`, `every`. Each is OVERCLAIM unless the evidence supports the absolute *as
stated*: a test proving three cases does not support "never". Downgrade-in-place is not your
job — report it.

**Stale** is its own verdict: the claim was true when written and the code has since moved. Cite
both the claim and the current `file:line` that contradicts it.

**Output** a table — `claim | source (file:line or commit) | evidence location | VERIFIED /
UNSUPPORTED / OVERCLAIM / STALE` — and a one-line verdict.

**Verdict rule:** any UNSUPPORTED, OVERCLAIM, or STALE row is BLOCK.

### 2. test-quality-auditor — Opus

Tier deviation, stated per CLAUDE.md: this is the one auditor above the Sonnet default.
Choosing a mutation that actually lands on the covered path, and classifying what came back, is
judgment rather than mechanics — and its failure mode (a mutation that misses, read as a passing
test) fails in the direction that makes a defect look absent.

**Role:** You are a test-quality auditor. You establish whether the tests on this branch can
fail.

For every test added or modified in `<merge-base>..HEAD`:

1. Identify the code path the test covers.
2. Apply one targeted mutation to that path — invert a condition, change a boundary, return a
   constant, drop a call. The mutation must be one the test *claims* to catch.
3. Run the test. **Read the runner's actual exit reason, not the first error string.** A compile
   or import error is NOT evidence the test discriminates: a compile failure and an assertion
   failure look alike at a glance and mean opposite things. If the run did not compile, fix the
   mutation and re-run — do not score it.
4. A test that still passes under a mutation it should catch is a **non-discriminating
   assertion**. Report it as a defect.
5. **Undo the mutation with the inverse Edit. Never `git checkout -- <file>`, never
   `git revert`, never `git checkout .`.** That discards *every* uncommitted change in the
   file, which under this workflow is the entire task diff — the commit comes after
   verification by design. CLAUDE.md records five recurrences of exactly this across four
   projects, each one journaled and each one repeated. The mutation is small and you know it;
   reverse it by hand.

Also report, without mutating:

- **Fakes and mocks that can never fail** — a mock asserting only that it was called, a stub
  whose return is the value under assertion, a test whose assertion holds on empty or absent
  input. Substitute the zero case by hand: if the assertion survives, the test is decoration.
- **Duplicated test blocks** — the same assertion repeated under different names, which inflates
  the count without adding discrimination.

**Output** a table — `test (file:line) | code path | mutation applied | test result | DISCRIMINATES
/ NON-DISCRIMINATING / UNFALSIFIABLE / DUPLICATE` — a confirmation that every mutation was
reversed by inverse Edit and `git status --porcelain` is back to its pre-audit state, and a
one-line verdict.

**Verdict rule:** any NON-DISCRIMINATING or UNFALSIFIABLE row is BLOCK. DUPLICATE alone is not.

### 3. scope-auditor — Sonnet

**Role:** You are a scope auditor. You establish whether this diff is the diff the issue asked
for.

Against `git diff <merge-base>..HEAD`:

1. **Untraceable change.** Every hunk maps to something the pasted issue asks for, or it is
   reported. Incidental refactors, drive-by renames, and reformatting count — they may be fine,
   but they are Jerry's call, not yours. Report; do not judge them harmless.

2. **Files that should not be tracked.** The literal request was to catch files swept in by a
   broad `git add -A`. **That is not detectable from a diff — staging method leaves no trace in
   history.** This is the substitute, and the substitution is stated here so a later reader
   knows the literal check was impossible rather than forgotten. Check instead:
   - `git diff --name-only <merge-base>..HEAD | xargs -r git check-ignore -v` — any hit is a
     force-added ignored file, which is the actual harm `add -A` causes.
   - Known-personal paths that must never ship: `.superpowers/`, `.devcontainer/`,
     `session-handoff.md`, `.scratchpad/` contents, editor and OS droppings, credentials,
     absolute paths under `/home/`.
   - Files whose type is unrelated to the issue — a lockfile, a binary, a generated artifact.

3. **Deletions of rules or docs without recorded rationale.** Any removed line from CLAUDE.md,
   AGENTS.md, README, a skill or command file, a design doc, or a comment stating an invariant
   — check whether the commit message or the kata issue records *why*. A deletion whose
   rationale is absent from both is a finding, even when the deletion looks obviously correct.
   Rationale lives in the record or it did not happen.

**Output** a table — `change (file:line) | category | traceable to | UNTRACEABLE /
SHOULD-NOT-BE-TRACKED / UNJUSTIFIED-DELETION / OK` — and a one-line verdict.

**Verdict rule:** any non-OK row is BLOCK.

## Artifacts — read the file, not the report

Each auditor writes its full table to
`${PROJECT_ROOT}/.scratchpad/{YYYYMMDD}-verify-branch-{auditor}-{branch}.md` **before** it
returns, and ends its report with a single line: `VERDICT: PASS` or `VERDICT: BLOCK`.

**Aggregate from the files, not from the returned reports.** The harness sometimes delivers only
an idle notification and drops an agent's final report; the artifact is what survives that. If a
report and its artifact disagree, the artifact is the evidence and the report is a summary of it.

**Fail closed.** A missing artifact, an unreadable one, or a report with no `VERDICT:` line is
**BLOCK** — recorded as "auditor did not return a verdict", never as a pass. An auditor that
crashed and one that found nothing are indistinguishable from silence, and only one of them is
safe.

## The verdict

Aggregate into one PASS or BLOCK and a single numbered defect list across all three auditors,
most severe first, each entry naming its auditor and its `file:line`.

**PASS requires all three to return PASS.** Any BLOCK is a BLOCK — there is no override, no
majority, and no "two of three is close enough."

**On PASS:** say so, name the merge base SHA and the three artifact paths, and proceed to the
merge.

**On BLOCK:** do not merge and do not close the issue. Take `/super-do`'s existing escalation
path rather than inventing one — comment the numbered defect list on the kata issue, label it
`needs-review`, and report to Jerry. Do not fix the defects and re-run: this gate is a single
pass, and an auditor's finding is input to a decision, not a work item you clear on your own
authority.
