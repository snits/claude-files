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
which deletes the artifact along with it — silently, after the auditor reported success. The write ladder below keeps a refused write from costing the report,
but nothing recovers an artifact that landed and was then cleaned away.

```
mkdir -p "$(git rev-parse --show-toplevel)/.scratchpad"
```

**Invoke this gate from the primary checkout, not from inside a feature worktree.** Agent
worktrees are cut from the session's cwd, so a gate launched from within a worktree gives its
auditors a `.scratchpad` symlink pointing at *that* worktree rather than the primary checkout —
and the artifacts then die with it. This costs nothing to observe and removes a whole class of
path confusion before dispatch.

## The three auditors — dispatch concurrently, one message, three Agent calls

All three run in parallel. Each gets `isolation: "worktree"` — they read and (for the mutation
auditor) mutate independently, and a shared checkout makes that unsafe.

**The harness worktree an auditor receives is NOT parked on `${3}`.** It is cut from the
session's cwd, so it holds whatever that had checked out — under `/super-do` that is the target
branch, and the branch under audit is somewhere else entirely. An auditor that reads source files
from its own worktree is therefore reading the wrong tree, and one that tries to *run* the code
finds the files simply absent. Nothing in the harness announces this.

**So every brief states that fact, and every auditor that needs to execute or mutate code creates
its own detached worktree at `${3}` before doing so:**

```
git worktree add --detach <primary>/.claude/worktrees/audit-<issue>-<auditor> ${3}
```

`--detach` is unconditional, not a special case for the mutation auditor: `git worktree add`
refuses a branch that is checked out **anywhere** — the primary checkout, an implementer's agent
worktree, another auditor's tree — and which of those holds it varies by caller. Detaching side-steps
the question entirely.

**Place it as a sibling under the primary checkout's `.claude/worktrees/`, not inside the agent's
own worktree.** Nesting a git worktree within a git worktree is its own source of confusion, and
the auditor cannot clean it up afterwards — `git worktree remove` across trees is refused for an
isolated agent. **The lead prunes these after aggregating; they do not remove themselves.**
Observed 2026-09-07 (hexweave `enb2`), where the test-quality auditor deviated from an
earlier instruction to place it at the agent worktree root, for exactly this reason, and said so.

**Borrowing another tree is prohibited — say so in the brief.** Not the primary checkout, not an
implementer's worktree, not a sibling auditor's. The failure this closes: on hexweave `enb2` the
claim-verifier needed to run mutations, found its own worktree on `main` without the branch's
files, and ran them in the **implementer's live worktree** instead. It reverted correctly and the
lead verified the tree clean before merging — but a dropped revert there merges a mutation into
the target branch, and the auditor had no instruction telling it not to. An auditor that cannot
create its own worktree reports that as a Deviation and says what it could not verify; it does
not go looking for a tree that already has the files.

**Do not let an auditor place its worktree, or any scratch directory, under `.scratchpad`.**
Where `worktree.symlinkDirectories` lists it in settings — it is set for `.scratchpad` and
`.superpowers` in `~/.claude/settings.json`, and projects set it too — an agent worktree's
`.scratchpad` is a **symlink back to the checkout the worktree was cut from**, so a tree created
beneath it resolves outside the isolation sandbox and every subsequent write and version-control
command in it is refused. Where the setting is absent it is a real directory; `readlink -f` says
which, and the instruction is the same either way because the cost of being wrong is asymmetric.
Say in each brief: put scratch *files* at the agent worktree root, which is a real directory —
and put an audit *worktree* at the sibling path above, never at the agent worktree root and never
under `.scratchpad`. Observed 2026-09-07 (hs5n test-quality auditor), which recovered by moving
its tree out of `.scratchpad`.

Every brief carries, verbatim:

- The merge-base SHA and the target branch.
- The kata ref and the issue body text (paste it — the agent cannot see this conversation, and
  handing it only a ref invites it to invent the scope it is auditing against).
- **The artifact path it must write, the write ladder in full, and the verdict-line rule**
  (all three under "Artifacts" below). Paste them into the brief rather than citing them — the
  agent cannot read this file. Omitting the verdict-line rule is the specific mistake that
  reintroduces the defect this gate was fixed for: the auditor never learns the last line must
  be the literal string, and the aggregator's `tail -1` then finds no verdict and blocks.
- **For the test-quality auditor: the mutation the maintainer already ran**, taken from the
  commit message or the issue, with the instruction to pick a different one.
- **Every input path the brief cites, resolved into the primary checkout first.** A brief that
  points an auditor at a matrix, fixture, or prior report living under a feature worktree cites
  something that dies when that tree is cleaned. The rule the "Establish the base" step applies
  to outputs applies to inputs: copy or resolve each one before dispatch, and cite the resolved
  path. Observed 2026-09-07 on rhkmaint-tools `ebbv`, where a cited matrix existed only inside
  the feature worktree and survived only because an auditor noticed and read it live.
- **The blocking / non-blocking bar, pasted in full** (the "what blocks, and what is only
  reported" section). Each auditor's Verdict rule says "apply the bar above" — an auditor that
  never receives it improvises the split, which is precisely the drift the bar was centralised
  to prevent.
- **That its harness worktree is not on `${3}`; that if it needs to execute or mutate code it
  creates its own detached worktree at `${3}` under the primary checkout's `.claude/worktrees/`,
  which the lead prunes; and that borrowing any other tree — the primary checkout, an
  implementer's worktree, a sibling auditor's — is prohibited.** All three auditors get this,
  not only the mutation auditor: the one that improvised into a live tree was the claim-verifier,
  which had not been told.
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
   constant, drop a call. The mutation must be one the test *claims* to catch. **Where the brief
   names a mutation the maintainer already ran, pick a different one** — and where it names
   none, check the commit message yourself before choosing. Re-running a mutation whose result
   is already written down spends an Opus run to reproduce a known answer; picking a fresh one
   is what surfaced the `ywpn` DesertRiparian coverage gap (orbweaver-rs, 2026-09-02).
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

**If the suite cannot run in your detached audit worktree**, say so rather than scoring tests you
never executed. A fresh worktree has no `node_modules`, `target/`, `.venv`, or build cache, and a
cold build may be slower than the audit — **cold-build it anyway; a few minutes is acceptable.**
That is the only acceptable move. Running the mutations in the primary checkout, in an
implementer's worktree, or in a sibling auditor's tree is prohibited: those trees hold work that
is not yours, and a mutation left behind by a dropped revert merges into the target branch. If
the cold build genuinely cannot be made to work, report that under `Deviations`, say which tests
you could not score, and let the verdict reflect what you actually verified.

**Never share a compiled-artifact directory across trees**: not `target/`, not
`CARGO_TARGET_DIR`, not a build cache keyed on source paths. Cargo's dep-info records
workspace-relative source paths, so an rlib your worktree compiled from **mutated** source is
accepted as fresh by the primary checkout whenever the primary's source mtime is older — the
mutation then survives the audit and lands in someone else's test run. Measured 2026-09-01
(orbweaver-rs `9mj0`): after a PASS and merge, the primary checkout reproduced the auditor's
exact mutation numbers (177/16) while a fresh worktree of the same commit passed (139/0);
`cargo clean -p <crate>` did not clear it because it is profile-scoped, `cargo clean --release`
did. Interpreted-language dependency trees (`node_modules`, `.venv`) cache no such
path-keyed compiled output and are safe to link.

Reporting "could not run the suite" is a BLOCK, and an honest one; guessing is not.

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
path resolved above and pasted into its brief — **before** it returns, or, when every rung of
the ladder below is refused, returns that table inline for the lead to persist. Either is
compliance. Neither happening is a real outcome with its own classification below, not an
impossibility.

**The last line of the artifact file must be exactly `VERDICT: PASS` or `VERDICT: BLOCK`**, and
an auditor that wrote a file confirms it with `tail -1` before returning. The returned report
ends with the same line. Both, not either: the line was previously specified against the returned
message and consumed from the file, so an auditor that complied exactly produced a verdict-less
artifact and the rule below read its own ambiguity as a BLOCK. Measured three times — orbweaver-rs
`37f3`/`ywpn` (2026-09-02, claim-verifier) and the `g45s` gate (2026-09-07, claim-verifier, where
`grep -o 'VERDICT: [A-Z]*'` on the artifact returned nothing while its inline report carried the
line), and rhkmaint-tools `3ykm` (2026-09-04, test-quality).

**The aggregator reads the artifact's LAST LINE — `tail -1` — not a grep of the whole file.** A
grep-anywhere check is weaker than the requirement it enforces: audit reports quote verdict lines
as evidence (this command file contains one), so an artifact truncated mid-write, having lost its
own final verdict, still matches a bare grep and is scored as delivered. Match on the last line or
the check does not discriminate. It does not interpret a `## Verdict` heading or read prose off
the tail. It does **not** fall back to the returned report's verdict
when the artifact has none — `z17a` raised that fallback as an option and it is deliberately not
taken, because it would restore exactly the ambiguity the two-place requirement removes. An
artifact with no verdict line blocks; the lead does not recover it by consulting the report.
**Returning inline with no artifact at all is different and is not a failure** — see rung 4. You
are never penalised for a write the sandbox refused, only for a table or a verdict you did not
produce.

### The write ladder — paste it into every brief

The mandated write is refused for isolated auditors more often than it succeeds, and **no single
mechanism survives every refusal on record.** Two guards are confirmed to refuse it,
independently: the Write tool's canonical-path check (which refuses the primary-checkout path
*and*, where `.scratchpad` is a symlink, the worktree's own copy of that path); and the worktree
command-shape guard, which refuses a Bash invocation whose *body* merely quotes a version-control
shape — something audit reports routinely contain as evidence. On 2026-09-07 all six artifacts
landed, each recovering through one of two fallbacks its brief supplied — a script file, or a
write-inside-the-worktree plus copy — and the script-file form has been refused elsewhere as "too
complex to verify" (`n8zs`); a heredoc through the symlink worked first-try on hexweave `zbzd`
and was refused on `ms79`. No rung is reliable alone, which is the whole reason this is a ladder.

**One reported mechanism is disproven and is recorded here so it is not re-derived:** an auditor
attributed its refusal to "a subagent rule against writing report files at all." No such rule is
in evidence — `wcs3`'s CORRECTION lists four isolated agents writing report `.md` files to that
exact directory in one batch. The refusal was real; the auditor's diagnosis of it was not. Treat
an agent's *explanation* of a refusal as a hypothesis, and the refusal itself as the datum.

So this is a ladder, not a prescription. Each auditor tries in order and stops at the first that
lands — **and "lands" means verified, not attempted**: after any rung that writes a file, confirm
with `wc -c` that it is non-empty and with `tail -1` that its last line is the verdict. A
`cat > file` heredoc has been recorded writing a **zero-byte file at exit 0 with no error**, so
an unchecked success is not a success.

**A rung that fails verification leaves residue — clear it before descending.** A half-landed
write (zero-byte, or truncated short of its verdict line) is not nothing: the lead reads it as an
empty or unreadable artifact and blocks, so leaving it behind turns a refused write into a block
the later rungs cannot undo, no matter how complete the table you go on to return. So whenever
the `wc -c` / `tail -1` check fails, delete the file at the path you just checked — `rm -f <that
path>` — and confirm it is gone before trying the next rung. Clear it at either location the lead
looks in: the destination, and your own worktree root, which the lead searches when the
destination holds nothing. If the
removal is itself refused, say so under `Deviations` and name the path — the lead is told below
to treat a path you named as residue as no artifact at all, so disclosing it is what keeps a file
you could not delete from being scored as your report.

1. **`Write` to the pasted absolute path.** Often refused; costs one turn to find out.
2. **Write the report body to a script file that does raw file I/O (`open` / `write`), then
   execute that script as a plain command.** Rung 1's refusal is *path*-scoped — the canonical-path
   guard rejects the destination, not the tool — so `Write` still works for a script placed
   **inside your own worktree**. Put a `python3` script there and have it `open()` the absolute
   destination and `write()` the body; invoke it as `python3 <path-to-script>`.
   No heredoc anywhere: not as the Bash invocation *and not inside the script*, since the guard
   fires on the report body's content wherever it appears, and the body is what carries the
   version-control shapes.
3. **Write the file at the agent worktree *root*** — a real directory. Never under
   `.scratchpad`, which in an agent worktree is often a symlink back to the checkout the
   worktree was cut from, so anything beneath it resolves outside your sandbox and is refused.
   **Then copy it to the absolute path. Verify the DESTINATION, not the copy you started from**
   — `wc -c` and `tail -1` against the absolute path, since a `cp` that reports success and leaves
   the file only in your worktree is indistinguishable from one that worked. **Report the
   in-worktree absolute path in your return message either way** — a copy that reports success
   and leaves the file only in the worktree is indistinguishable from one that worked, and the
   lead needs the path to recover the artifact before the worktree is auto-cleaned. **This rung
   writes in two places, so check both** — the file at your worktree root gets the same `wc -c` /
   `tail -1` check, and you report that path only if it passes. If the root file is what
   half-landed, it is residue at a location the lead recovers from: clear it too, and do not
   cite it.
4. **Return the complete table inline, with the `VERDICT:` line last.** This rung cannot be
   refused. It is a legitimate terminus, not a failure — say so in `Deviations` and name the
   rungs that were refused.

An auditor that reaches rung 4 has complied with the brief. Four issues — `n8zs`, `wcs3`,
`4ky9`, `gsft` — converged on that terminus independently, and every lead who met it in
practice persisted the report by hand.

### Aggregation

**Aggregate from the files, not from the returned reports.** The harness sometimes delivers only
an idle notification and drops an agent's final report; the artifact is what survives that.

**Where a report and its artifact disagree, the answer depends on what disagrees.** On findings,
tables, or detail, the artifact is the evidence and the report is a summary of it. **On the
`VERDICT:` line itself, the disagreement is a BLOCK** and neither side wins — one of the two was
produced by an auditor that did not know its own conclusion, and no rule for preferring one of
them recovers a verdict you can trust. This is stated as a precedence rule because the two
sentences were previously separate and gave opposite outcomes for the same input.

**A path the auditor named as residue under `Deviations` is not its artifact.** Ignore that file
entirely — it is the wreckage of a refused write, and the auditor said so precisely to stop you
reading it as a delivery. Then apply the rule below to what remains.

**Before declaring an artifact missing, look for it.** Auditors given an absolute path have
still written under their own worktree. **The destination is authoritative; consult the auditor's worktree only when the destination
holds nothing.** Search for the basename under `.worktrees/` and `.claude/worktrees/` — and do it *before* removing any agent worktree, because a worktree the
harness finds unchanged is auto-cleaned and takes the artifact with it.

**When an auditor returns inline at rung 4, the lead persists the report verbatim at the
expected path under a provenance header** naming the auditor, the rungs that were refused, and
that the lead transcribed it. That header is the evidentiary distinction the artifact rule
exists to preserve: it marks the file as a transcription rather than an auditor-written
artifact, so a later reader is not misled about which it is.

**Fail closed.** A missing artifact, an unreadable or empty one, or a report with no `VERDICT:`
line is **BLOCK** — recorded as "auditor did not return a verdict", never as a pass. An auditor
that crashed and one that found nothing are indistinguishable from silence, and only one of them
is safe. A zero-byte file at exit 0 is a recorded failure mode, which is why "empty" is named
alongside "unreadable": it is the one shape that looks like delivery from outside.

**One exception, and only one.** A complete table carrying a literal `VERDICT:` line that arrives
**inline** because the ladder above was refused at every rung, and which the lead persists
verbatim under a provenance header, counts as delivered. A sandbox that refused every write is
not a dropped report, and reading it as one manufactures a BLOCK with nothing to do with the
branch under audit. What the rule targets is a report that never arrived — not one the sandbox
would not let land.

This is deliberately a single rule with a single exception rather than a decision procedure over
outcomes. A three-step procedure was tried here and withdrawn: five independent review passes
each found a new gap or contradiction in it, two of them introduced by a careful fix to the
previous one, because the classification couples the artifact axis and the report axis tightly
enough that every repair perturbs it elsewhere. The write ladder is what actually prevents the
false BLOCKs this section was rewritten for — on its first live run rung 1 was refused for all
three auditors and all three artifacts landed anyway — so the classification does not have to
carry that weight. Reworking it is tracked as kata `claudes-home#eqgn`; do not extend this rule
in place without reading that issue first.

### Cleanup

Two kinds of tree need clearing, and only one of them cleans itself.

**The harness worktrees.** Agents dispatched with `isolation: "worktree"` receive a full copy of
the primary checkout's untracked `.superpowers/` tree. Their worktrees then show `?? .superpowers`
and refuse a plain `git worktree remove`. **`--force` is expected** — the copies are
indistinguishable from the originals, so check that the canonical `.superpowers/sdd` is intact
afterwards rather than assuming the removal took the right one.

**The `.superpowers` copy does NOT make an auditor's worktree count as *changed* for the
harness's auto-clean test** (Jerry ruling, 2026-09-07). So auto-clean does fire, and the warning
above is the common case rather than a rare one: **recover every artifact before removing or
allowing the removal of an auditor's worktree.** Rung 3's in-worktree path exists for exactly
this window.

**The audit worktrees the auditors created**, at
`<primary>/.claude/worktrees/audit-<issue>-<auditor>`. These do **not** auto-clean and their
creators cannot remove them — `git worktree remove` across trees is refused for an isolated
agent, so an auditor that made one says so in its report and leaves it. **The lead prunes them,
after aggregating the artifacts:**

```
git worktree list                       # every audit-* tree is yours to clear
git worktree remove --force <path>      # per audit tree
git worktree prune
git worktree list                       # confirm only the primary checkout remains
```

Left behind, they are detached checkouts of a branch that may since have been deleted — they
hold refs alive, they confuse the next `git worktree list`, and on the next gate run a stale
`audit-<issue>` path collides with the new one.

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
