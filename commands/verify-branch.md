---
name: verify-branch
description: Pre-merge gate — three concurrent auditors on claims, test discrimination, and scope. Any BLOCK stops the merge.
---

Verify a branch before it merges. Arguments: `${1}` = target branch (the merge-base side),
`${2}` = the qualified kata ref for the issue being worked (`kata#abc4` form), `${3}` = the
branch under audit.

**All three are required. Do not default `${1}` to `main`** — `/orchestrate-issues` already rules
that a merge target is named, never assumed. **Use the qualified `kata#` form for `${2}`**: from
inside a worktree an unbound workspace resolves to the enclosing git remote's basename rather
than failing, which silently targets another project.

**`${3}` is named explicitly and never inferred from `HEAD`.** This gate is invoked from two
places and `HEAD` means different things in each. Under `/super-do` the session sits on the
feature branch, so `HEAD` would work. Under `/orchestrate-issues` the orchestrator runs from the
repo root **where the target branch is checked out** — there `git merge-base <target> HEAD`
returns the target's own tip, the range is empty, every auditor audits nothing, and all three
return PASS. That is not a degraded gate; it is a gate that silently passes everything, which is
indistinguishable from a gate that never ran.

Measured 2026-08-30 on a fixture with `main` checked out and a 4-file `dirty-branch` pending:
`merge-base main HEAD` gave main's own tip, `<mb>..HEAD` held 0 commits and 0 files, while
`<mb>..dirty-branch` held 4. Passing the branch also frees the auditors from depending on their
own cwd, which matters because each runs under `isolation: "worktree"` and nothing guarantees the
harness parks that worktree on the ref you meant.

Invoking this command IS the user's request to task subagents. Dispatch the three below without
stopping to ask.

## The bar — what blocks, and what is only reported

Every auditor reports everything it finds. **Only some findings block**, and the split is fixed
here rather than left to each auditor's judgment, so the bar cannot drift between runs or
between auditors.

`/super-do`'s review gate already holds this shape — critical and high fail, medium and low do
not — and this gate inherits its mandatory-ness, so it inherits the calibration too. A gate
where every finding blocks is a gate that blocks on a regenerated lockfile, and one false BLOCK
in front of Jerry costs more credibility than the gate buys in a month.

**Blocking:**

- `UNSUPPORTED` or `STALE` — a claim that is not true, or no longer true.
- `OVERCLAIM` on a claim about behavior the code is relied on to guarantee — a safety property,
  an invariant, an error-handling boundary, anything a reader would act on.
- `NON-DISCRIMINATING` or `UNFALSIFIABLE` — a test that cannot fail.
- `SHOULD-NOT-BE-TRACKED` — a file that must not ship.
- `UNJUSTIFIED-DELETION` — a removed rule or doc line with no rationale in the commit message
  or the issue.
- `UNTRACEABLE` where the change is a behavior change: new logic, altered control flow, a
  changed default, a touched public signature.

**Reported, not blocking:**

- `OVERCLAIM` in text nothing is acted on — a test name, a scratch note, prose flourish in a
  commit body that the code around it does not depend on.
- `DUPLICATE` tests.
- `UNTRACEABLE` where the change is mechanical and self-evidently entailed by the work:
  a regenerated lockfile (`Cargo.lock`, `package-lock.json`, `uv.lock` — CLAUDE.md-adjacent
  practice *requires* regenerating these on a version or dependency change, so blocking on one
  would forbid a correct commit), formatter output, an import added for a symbol the change
  uses, a mechanical rename carried through call sites.

An auditor that is genuinely unsure which side a finding falls on marks it blocking and says so
in one line. Fail closed — but say it, so the calibration can be corrected rather than quietly
absorbed.

## What this gate is, and is not

This is **one pass, not a loop.** There is no fix-and-retry cycle inside it. It runs once; it
returns PASS or BLOCK; a BLOCK escalates.

It is **not a fourth code-review cycle.** `/super-do`'s review gate asks whether the code is
correct. This asks three different questions the correctness reviewer does not: are the claims
we wrote down true, do the tests actually discriminate, and is the diff traceable to the issue.
A branch that cleared three code reviews can still fail every one of them.

## Establish the base first

```
git merge-base ${1} ${3}
git rev-parse --show-toplevel        # the PRIMARY checkout, not a worktree
```

Every auditor scopes to `<merge-base>..${3}` — the named branch, never `HEAD`. Compute it once, paste the SHA into all three
briefs, and never let an auditor recompute it — three auditors deriving their own base is three
chances to audit a different diff than the one being merged.

**Compute the artifact directory here too, as an absolute path in the primary checkout, and
paste that absolute path into each brief.** Do not write `${PROJECT_ROOT}/.scratchpad/` into a
brief and leave the agent to expand it. Each auditor runs with `isolation: "worktree"`, where
that expands to the *worktree* root — and a worktree the harness finds unchanged is auto-cleaned,
which for the two read-only auditors deletes the artifact along with it — silently, after the
auditor reported success. The write ladder below keeps a refused write from costing the report,
but nothing recovers an artifact that landed and was then cleaned away.

```
mkdir -p "$(git rev-parse --show-toplevel)/.scratchpad"
```

## The three auditors — dispatch concurrently, one message, three Agent calls

All three run in parallel. Each gets `isolation: "worktree"` — they read and (for the mutation
auditor) mutate independently, and a shared checkout makes that unsafe.

**The branch under audit is already checked out in the primary checkout**, and `git worktree add`
refuses a branch that is checked out elsewhere. So the mutation auditor's worktree must be
detached — `git worktree add --detach <path> <branch>` — or created on a throwaway branch. Say
this in its brief; otherwise it burns turns rediscovering it, exactly as `/orchestrate-issues`
warns about agents escalating on plumbing.

**Do not let an auditor place its worktree, or any scratch directory, under `.scratchpad`.**
Inside an agent worktree `.scratchpad` is a **symlink back to the primary checkout**, so a tree
created beneath it resolves outside the isolation sandbox and every subsequent write and
version-control command in it is refused. Say in each brief: put scratch directories at the
agent worktree *root*, which is a real directory. Observed 2026-09-07 (hs5n test-quality
auditor), which recovered by moving its tree to `<agent-worktree-root>/audit-<issue>`.

Every brief carries, verbatim:

- The merge-base SHA and the target branch.
- The kata ref and the issue body text (paste it — the agent cannot see this conversation, and
  handing it only a ref invites it to invent the scope it is auditing against).
- **The artifact path it must write, and the write ladder in full** (see "Artifacts" below).
  Paste the ladder into the brief rather than citing it — the agent cannot read this file.
- **Every input path the brief cites, resolved into the primary checkout first.** A brief that
  points an auditor at a matrix, fixture, or prior report living under a feature worktree cites
  something that dies when that tree is cleaned. The rule the "Establish the base" step applies
  to outputs applies to inputs: copy or resolve each one before dispatch, and cite the resolved
  path. Observed 2026-09-07 on rhkmaint-tools `ebbv`, where a cited matrix existed only inside
  the feature worktree and survived only because an auditor noticed and read it live.
- **`file:line` evidence for every finding, and "not found" rather than an inferred mechanism.**
- A `Deviations` section: when an edge case forces it off the brief, take the conservative
  option and record the deviation.

### 1. claim-verifier — Sonnet

**Role:** You are a claims auditor. You establish whether what this branch asserts is true.

**Do not restate the method — invoke the `verify-claims` skill and follow it.** It already
defines the extract / categorize (CODE_CITATION, COMMAND_RESULT, INFERENCE) / verify / table
procedure. This brief supplies only what is branch-specific:

**Extraction sources**, all scoped to `<merge-base>..${3}`:
- commit messages (`git log <merge-base>..${3}`) — subject and body
- comments added or changed in the diff (`git diff <merge-base>..${3}`)
- test names and docstrings for tests added or modified
- the kata issue body and comments pasted into this brief

**Overclaim scan.** Flag absolute or guarantee-shaped language wherever it appears in those
sources — `guaranteed`, `never`, `always`, `impossible`, `compiler-enforced`, `cannot`,
`ensures`, `all`, `every`. Each is OVERCLAIM unless the evidence supports the absolute *as
stated*: a test proving three cases does not support "never". Downgrade-in-place is not your
job — report it.

**Stale** is its own verdict: the claim was true when written and the code has since moved. Cite
both the claim and the current `file:line` that contradicts it.

**A cited SHA that no longer resolves is not fabricated until the subject fails too.** Cites
are upstream-style, `sha ("subject")`; a rebase kills the SHA and keeps the subject. Before
calling one UNSUPPORTED, run `git log --all --grep='<subject>'` (fixed-string the subject). A
subject match is a NOTE (`rebased`), not a block. A bare SHA with no subject that fails to
resolve stays UNSUPPORTED — there is nothing left to check.

**Output** a table — `claim | source (file:line or commit) | evidence location | VERIFIED /
UNSUPPORTED / OVERCLAIM / STALE` — and a one-line verdict.

**Verdict rule:** apply the bar above. UNSUPPORTED and STALE always block; OVERCLAIM blocks
only on a claim about guaranteed behavior.

### 2. test-quality-auditor — Opus

Tier deviation, stated per CLAUDE.md: this is the one auditor above the Sonnet default.
Choosing a mutation that actually lands on the covered path, and classifying what came back, is
judgment rather than mechanics — and its failure mode (a mutation that misses, read as a passing
test) fails in the direction that makes a defect look absent.

**Role:** You are a test-quality auditor. You establish whether the tests on this branch can
fail.

For every test added or modified in `<merge-base>..${3}`:

1. Identify the code path the test covers.
2. Apply one targeted mutation to that path — invert a condition, change a boundary, return a
   constant, drop a call. The mutation must be one the test *claims* to catch. **Where the
   commit message or the issue records a mutation the maintainer already ran, the brief names
   it and says "pick a different one".** Re-running a mutation whose result is already written
   down spends an Opus run to reproduce a known answer; picking a fresh one is what surfaced
   the `ywpn` DesertRiparian coverage gap (orbweaver-rs, 2026-09-02).
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

**If the suite cannot run in the worktree**, say so rather than scoring tests you never
executed. A fresh worktree has no `node_modules`, `target/`, `.venv`, or build cache, and a cold
build may be slower than the audit. Two acceptable moves, in order: cold-build in your own
worktree — a few minutes is acceptable — or, if that is not workable, run the mutations in the
primary checkout instead.

**Never share a compiled-artifact directory across trees**: not `target/`, not
`CARGO_TARGET_DIR`, not a build cache keyed on source paths. Cargo's dep-info records
workspace-relative source paths, so an rlib your worktree compiled from **mutated** source is
accepted as fresh by the primary checkout whenever the primary's source mtime is older — the
mutation then survives the audit and lands in someone else's test run. Measured 2026-09-01
(orbweaver-rs `9mj0`): after a PASS and merge, the primary checkout reproduced the auditor's
exact mutation numbers (177/16) while a fresh worktree of the same commit passed (139/0);
`cargo clean -p <crate>` did not clear it because it is profile-scoped, `cargo clean --release`
did. Interpreted-language dependency trees (`node_modules`, `.venv`) cache no such
path-keyed compiled output and are safe to link. Choosing the second is exactly the case the inverse-Edit rule above
was written for, since the diff you would destroy is the real one. Record which you did under
`Deviations`. Reporting "could not run the suite" is a BLOCK, and an honest one; guessing is not.

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

**Verdict rule:** apply the bar above. NON-DISCRIMINATING and UNFALSIFIABLE block; DUPLICATE
does not.

### 3. scope-auditor — Sonnet

**Role:** You are a scope auditor. You establish whether this diff is the diff the issue asked
for.

Against `git diff <merge-base>..${3}`:

1. **Untraceable change.** Every hunk maps to something the pasted issue asks for, or it is
   reported. Incidental refactors, drive-by renames, and reformatting count — they may be fine,
   but they are Jerry's call, not yours. Report; do not judge them harmless.

2. **Files that should not be tracked.** The literal request was to catch files swept in by a
   broad `git add -A`. **That is not detectable from a diff — staging method leaves no trace in
   history.** This is the substitute, and the substitution is stated here so a later reader
   knows the literal check was impossible rather than forgotten. Check instead:
   - `git ls-files -i -c --exclude-standard` — every tracked file that .gitignore says should
     not be. Any hit is a force-added ignored file, which is the actual harm `add -A` causes.

     **Do not use a bare `git check-ignore` here. It skips tracked files by default**, so on
     exactly the force-added file you are hunting it exits 1 and prints nothing — failing in the
     direction that makes the problem look absent. Verified 2026-08-30 against a fixture with
     `.secrets.env` in `.gitignore` and force-added: `git check-ignore -v .secrets.env` exits 1,
     while `git check-ignore -v --no-index .secrets.env` and `git ls-files -i -c
     --exclude-standard` both report it. If you want the per-file form, it must carry
     `--no-index`.
   - Known-personal paths that must never ship: `.superpowers/`, `.devcontainer/`,
     `session-handoff.md`, `.scratchpad/` contents, editor and OS droppings, credentials,
     absolute paths under `/home/`.
   - Files whose type is unrelated to the issue — a lockfile, a binary, a generated artifact.

3. **Deletions of rules or docs without recorded rationale.** Any removed line from CLAUDE.md,
   AGENTS.md, README, a skill or command file, a design doc, or a comment stating an invariant
   — check whether the commit message or the kata issue records *why*. A deletion whose
   rationale is absent from both is a finding, even when the deletion looks obviously correct.
   Rationale lives in the record or it did not happen.

4. **Reference parity.** When the issue, plan, or brief names a reference — a design board,
   a prior implementation being ported, a screenshot, a doc section describing the behavior —
   the branch is checked against that reference, not only against the issue text. List each
   element of the reference (flags, help strings, layout, documented behavior) and mark it
   PRESENT / MISSING / CHANGED in the branch. Doc sections that describe changed behavior are
   in scope by default: a CLAUDE.md or README line the diff made false is a finding here, not
   at final review. History: a Python-to-Rust port dropped help text and flags nobody listed,
   a TUI shipped panes top/bottom against a side-by-side design board, and two doc sections
   went false and were caught only after every functional gate had passed.

**Output** a table — `change (file:line) | category | traceable to | UNTRACEABLE /
SHOULD-NOT-BE-TRACKED / UNJUSTIFIED-DELETION / OK` — and a one-line verdict.

**Verdict rule:** apply the bar above. SHOULD-NOT-BE-TRACKED and UNJUSTIFIED-DELETION always
block; UNTRACEABLE blocks only on a behavior change, not on mechanical fallout. A MISSING
reference element blocks; CHANGED blocks only when the change is not recorded in the issue.

## Artifacts — read the file, not the report

Each auditor writes its full table to
`<primary-checkout>/.scratchpad/{YYYYMMDD}-verify-branch-{auditor}-{branch}.md` — the absolute
path resolved above and pasted into its brief — **before** it returns.

**The last line of the artifact file must be exactly `VERDICT: PASS` or `VERDICT: BLOCK`, and
the auditor confirms it with `tail -1` before returning.** The returned report ends with the
same line. Both, not either: the line was previously specified against the returned message and
consumed from the file, so an auditor that complied exactly produced a verdict-less artifact and
the rule below read its own ambiguity as a BLOCK. Measured twice — rhkmaint-tools `3ykm`
(2026-09-04) and the `g45s` gate (2026-09-07), where `grep -o 'VERDICT: [A-Z]*'` on the
claim-verifier's artifact returned nothing while its inline report carried the line.
The aggregator **greps the file for that literal line**; it does not interpret a `## Verdict`
heading or read prose off the tail.

### The write ladder — paste it into every brief

The mandated write is refused for isolated auditors more often than it succeeds, and **no single
mechanism survives every refusal on record.** Three distinct guards refuse, independently:
the Write tool's canonical-path check (which refuses the primary-checkout path *and* the
worktree's own `.scratchpad`, since that is a symlink resolving to the same place); the
worktree command-shape guard (which refuses a heredoc whose *body* merely quotes a
version-control invocation); and a subagent rule against writing report files at all. A
Python script file worked six times of six on 2026-09-07 and was refused once as "too complex
to verify" on rhkmaint-tools `rmmg`; a heredoc through the symlink worked first-try on hexweave
`jbpt` and was refused on `ms79`. So this is a ladder, not a prescription. Each auditor tries in
order and stops at the first that lands:

1. **`Write` to the pasted absolute path.** Often refused; costs one turn to find out.
2. **Write the report body to a script file, then execute that script as a plain command.** Not
   a heredoc — the heredoc form is refused when the report body quotes version-control shapes,
   which audit reports routinely do.
3. **Write the file at the agent worktree *root*** (a real directory — not under `.scratchpad`,
   see above) **and copy it to the absolute path.**
4. **Return the complete table inline, with the `VERDICT:` line last.** This rung cannot be
   refused. It is a legitimate terminus, not a failure — say so in `Deviations` and name the
   rungs that were refused.

An auditor that reaches rung 4 has complied with the brief. Four issues — `n8zs`, `wcs3`,
`4ky9`, `gsft` — converged on that terminus independently, and every lead who met it in
practice persisted the report by hand.

### Aggregation

**Aggregate from the files, not from the returned reports.** The harness sometimes delivers only
an idle notification and drops an agent's final report; the artifact is what survives that. If a
report and its artifact disagree, the artifact is the evidence and the report is a summary of it.

**Before declaring an artifact missing, look for it.** Auditors given an absolute path have
still written under their own worktree. Search for the basename under `.worktrees/` and
`.claude/worktrees/` — and do it *before* removing any agent worktree, because a worktree the
harness finds unchanged is auto-cleaned and takes the artifact with it.

**When an auditor returns inline at rung 4, the lead persists the report verbatim at the
expected path under a provenance header** naming the auditor, the rungs that were refused, and
that the lead transcribed it. That header is the evidentiary distinction the artifact rule
exists to preserve: it marks the file as a transcription rather than an auditor-written
artifact, so a later reader is not misled about which it is.

**Fail closed, scoped to what the rule is actually for.** The rule exists to keep a crashed
auditor distinguishable from a silent one, and it keeps its teeth:

- **BLOCK** — no report and no artifact; a report with no `VERDICT:` line; a truncated or
  partial table; an artifact that disagrees with its own report. Recorded as "auditor did not
  return a verdict", never as a pass.
- **Delivered** — a complete table plus a literal `VERDICT:` line, arriving inline and persisted
  under a provenance header. A sandbox that refused every write is not a dropped report, and
  reading it as one manufactures a BLOCK with nothing to do with the branch under audit.

The scoping is deliberate: the strict reading has a *measured* failure mode (false BLOCKs on
five of six auditors, 2026-09-07) and the bar section above already rules that one false BLOCK
in front of Jerry costs more than the gate buys in a month. Recorded on kata `bxeh`, which asked
for this call.

### Cleanup

Agents dispatched with `isolation: "worktree"` receive a full copy of the primary checkout's
untracked `.superpowers/` tree. Their worktrees then show `?? .superpowers` and refuse a plain
`git worktree remove`. **`--force` is expected for the read-only auditors** — the copies are
indistinguishable from the originals, so check that the canonical `.superpowers/sdd` is intact
afterwards rather than assuming the removal took the right one.

## The verdict

Aggregate into one PASS or BLOCK and a single numbered defect list across all three auditors,
most severe first, each entry naming its auditor, its `file:line`, and whether it is **blocking**
or **reported**. Non-blocking findings still appear in the list — suppressing them would make
this gate the only reviewer that saw them.

**PASS requires all three to return PASS.** Any BLOCK is a BLOCK — there is no override, no
majority, and no "two of three is close enough." A PASS carrying non-blocking findings is still
a PASS; report them and merge.

**On PASS:** say so, name the merge base SHA and the three artifact paths, and proceed to the
merge.

**On BLOCK:** do not merge and do not close the issue. Take `/super-do`'s existing escalation
path rather than inventing one — comment the numbered defect list on the kata issue, label it
`needs-review`, and report to Jerry. Do not fix the defects and re-run: this gate is a single
pass, and an auditor's finding is input to a decision, not a work item you clear on your own
authority.
