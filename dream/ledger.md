# Dream-pass candidate-theme ledger

Maintained by the dream skill (Job B). Ripeness rule: instances across 3+ projects, or
5+ instances spanning 2+ months. Statuses: watching | ripe | pearled.

## verification-evidence discipline

status: pearled (pearl: "The Artifact or the Story About It",
`~/vault/atlas/pearls/verification-evidence-discipline.md` — promoted; the 2026-08-13
amendment was folded in at promotion time)

The founding theme, hunted full-corpus in the zhqp spike (2026-08-11). Instance base:
~550-entry candidate pool, arm artifacts in ~/devel/mnemosyne/.scratchpad/zhqp-spike/.

Pass 2026-08-29 (window 08-13..08-29, 447 entries): the theme's densest window yet —
the rhkmaint-tools Rust-port SDD marathon generated dozens of catches/near-misses.
Amendment promoted and integrated: `intake/pearl/pearl-verification-evidence-amendment-20260829.md`
(status `integrated`; folded into `atlas/pearls/verification-evidence-discipline.md`):
- self-satisfying liveness checks (species 1 extension): pgrep matching its own command
  line (4+ sightings, project/2026-08-28/16-13-47-988982.md et al.), `kill -0` as
  "model loaded OK" (user/2026-08-16/09-15-45-290756.md)
- the instrument needs a reached-guard (species 2 extension): `--exact` matching zero
  tests reporting ok for 12/12 breaks (user/2026-08-22/19-01-16-340714.md), sed breaks
  that never landed, "A vacuity check needs its own vacuity check"
  (project/2026-08-27/21-57-40-007887.md)
- imagination-bounded break-testing: "break-tests only refute the breaks you imagine"
  + symmetry/axes (user/2026-08-18/16-09-11-773681.md, user/2026-08-18/15-35-42-985228.md
  "Quantity felt like coverage")
- species 5 extensions: self-narrating artifact (user/2026-08-28/00-06-43-650436.md),
  common-mode cancellation (user/2026-08-27/22-04-23-858153.md), aliased expected values
  (user/2026-08-27/18-21-05-370133.md), plausible disposal
  (user/2026-08-15/18-40-03-393575.md), benchmark prompt-cache self-artifact
  (project/2026-08-16/16-51-24-408889.md)

Pass 2026-09-13 (window 09-05..09-13, 648 entries, 13 projects; 344 non-Claude):
amendment proposed `_inbox/dream/pearl-verification-evidence-amendment-20260913.md` — the
"two artifacts disagree" bullet gains the y86w recipe (project/2026-09-10/15-37-19-889118.md:
"The contradiction was the finding"; three cheap corroborations; baseline logs print their
own state, user/2026-09-07/12-15-51-852958.md) and a species-5 kin (the comment satisfies the
keyword assertion, project/2026-09-10/16-09-03-086876.md). First non-Claude instance under
this pearl: "Auditor variance is real" (user/2026-09-11/02-24-31-791888.md, muse-spark-1.3).
Dense same-species instances not proposed: orbweaver piped-exit-code x4 in one session
(user/2026-09-06/20-59-26-750451.md); canary outside the blast radius, twice in the commit
that explained the hazard (project/2026-09-07/19-12-06-176415.md); fixture collapse making
two guards one observation (project/2026-09-08/11-59-36-214733.md); `rev-parse --verify`
validating the name's shape not the object (project/2026-09-07/14-55-36-772484.md).

## prose about a system is not under test

status: pearled — PROMOTED AND INTEGRATED. Lives at
`atlas/pearls/prose-is-not-under-test.md`; source material at
`intake/pearl/pearl-prose-is-not-under-test.md` (status `integrated`). Merges two prior threads: the "issue bodies go stale faster than
their comments" theme below (now closed into this) and the window's dominant new
pattern, "doc/prose claims are untested assertions."

Two mechanisms, one object: a declarative sentence about code is (1) untested at birth —
written from a mental model, with no red-green reflex ("Every error was a universal
quantifier I had not earned", user/2026-08-19/15-57-16-537213.md) — and (2) never re-run
as the tree moves (stale bodies, handoffs, titles, close messages, help text, docstrings).
Corpus span: 2025-08-19 (patch 0039 commit claiming absent fixes) → 2026-08-28; projects:
rhkmaint-tools, alexandria, vault, projstat, mnemosyne, claudes-home, orbweaver-rs.

Pass 2026-09-13 (window 09-05..09-13, 648 entries, 13 projects; 344 non-Claude):
amendment proposed `_inbox/dream/pearl-prose-amendment-alibi-comment-20260913.md` — the
instruction that predates a mechanism ("no felt signal", project/2026-09-10/15-37-19-889118.md),
the alibi comment ("A justification written into a doc comment gets audited less than the
code it defends", user/2026-09-10/16-19-51-928399.md), and the doc's file list read as the
directory (project/2026-09-07/20-00-20-633763.md). All rhkmaint-tools, one week — flagged as
such. Also: README examples drifted on hexgrid (user/2026-09-07/11-52-04-875564.md); the
`~24986` figure found nowhere but the protocol asserting it (culling proposal
`_inbox/dream/cull-memory-cap-figure-20260913.md`).

## compound-shell-commands are their own failure domain

status: pearled — PROMOTED AND INTEGRATED. Lives at
`atlas/pearls/shell-inside-the-instrument.md`; source material at
`intake/pearl/pearl-shell-inside-the-instrument.md` (status `integrated`). Full-corpus hunt run 2026-08-29 at Jerry's request, same sitting as
the pass: 38 haiku readers over the entire pre-window corpus (13,359 entries dumped
from the mnemosyne DB after the MCP full-fetch crashed the server) + 3 cosine queries.
Timeline found: zero instances before 2025-10; first specimens 2025-11-24 (orbweaver
subagent-cwd grep miss, pre-commit wrapper chain); recognizable family from 2026-04;
explosion 2026-06→08 in the worktree/multi-agent/zsh era. Six species stabilized in
the pearl. Reader noise note: one haiku reader (slice 34) drifted off-theme, one
(slice 24) missed an arm-A-confirmed instance — hybrid redundancy caught both.

Prior instances: see 08-13 entry in git history of this file. New this window:
- merged grep outputs losing filenames → confidently wrong "BRIEF CORRECTION"
  (project/2026-08-27/01-31-56-327233.md)
- tilde unexpanded in Bash argument position, garbage build dir
  (user/2026-08-25/18-38-26-763099.md)
- zsh not word-splitting unquoted vars; `echo ===` =word glob trap (struck the editor
  during THIS pass too) (project/2026-08-27/14-03-08-581591.md,
  project/2026-08-16/11-16-18-885938.md)
- cwd persistence striking the same lead twice across sessions after an explicit
  handoff warning (project/2026-08-26/00-06-51-704719.md,
  project/2026-08-26/22-28-35-811858.md)
- `pgrep -f` self-match family — shared with the pearl amendment's liveness species
  (project/2026-08-28/16-13-47-988982.md et al.)

Pass 2026-09-13 (window 09-05..09-13, 648 entries, 13 projects; 344 non-Claude):
same-species instances, no amendment: `| head -5 || echo CLEAN` reading head's status
(user/2026-09-07/23-10-45-301714.md); grep parsing a leading-dash path as bundled options,
byte-identical to a clean sweep except on stderr (project/2026-09-08/13-57-12-690176.md);
`git merge` run from inside the feature worktree merging the branch into itself
(project/2026-09-07/16-26-03-530270.md); `git diff --quiet` exiting 0 on an untracked file
(project/2026-09-10/09-25-15-647147.md, reader-cited, not re-verified); zsh not word-splitting
`$V` struck THIS pass's editor on the verify batch (species 4, again).

## worktree/environment artifact borrowing

status: watching (still mostly rhkmaint-tools + alexandria; the conceptual core was
folded into the pearl's "state outside the claim" move at the 08-13 amendment)

New: editable-install `.pth` pointing worktree imports at main's src
(project/2026-08-18/14-40-30-544612.md, project/2026-08-19/16-53-19-491144.md — a
false refutation of a real bug); gitignored artifacts silently downgrading
verifications in fresh worktrees (project/2026-08-16/21-07-29-160947.md); three entry
points with three truth values (project/2026-08-21/19-08-07-027655.md); stale shared
`mutants/` tree as evidence (project/2026-08-18/20-24-33-693397.md).

Pass 2026-09-27 (window 09-19T21:20..09-27T12:21, 476 entries, 10 projects; 121 non-Claude):
new: worktree green + main checkout red on the same SHA, caused by an untracked gitignored
hand-written `.d.ts` stub shadowing a package's real types (project/2026-09-25/21-07-13-328301.md,
alexandria); a worktree without `.env.test` runs hermetic and DB-gated tests silently skip
(project/2026-09-26/13-40-32-597039.md, alexandria); a fresh worktree with no node_modules read
as a cross-session gate regression (project/2026-09-20/19-06-21-752024.md, orbweaver-rs);
isolated agents cannot write the primary .scratchpad, so evidence scripts vanished with their
worktree (project/2026-09-20/00-45-04-053774.md, orbweaver-rs). The conceptual core stays
folded in the verification pearl's "state outside the claim" bullet.

## review-cycle convergence: finding identity over finding count

status: watching (rhkmaint-tools dominant; alexandria earlier)

New: convergence read from severity/category derivative, not count
(project/2026-08-18/15-25-01-356800.md, project/2026-08-27/21-57-40-007887.md — four
rounds, every blocking finding a false prose claim); opposite-direction findings in the
same area = a missing decision, escalate (project/2026-08-18/16-22-01-131609.md);
disjoint finding sets across independent reviewers as the argument FOR plurality
(project/2026-08-27/19-39-11-603139.md, user/2026-08-27/17-04-19-711616.md); fix-for-
finding-N creates finding-N+1 in invariant-dense code (project/2026-08-19/16-53-19-491144.md).

Pass 2026-09-27 (window 09-19T21:20..09-27T12:21, 476 entries, 10 projects; 121 non-Claude):
new: verify-branch dispatched before the final roborev, so the fixes moved the audited SHA and
forced a full re-audit (user/2026-09-20/11-55-52-412315.md, orbweaver-rs); a roborev review
landing on the branch while auditors were mid-diff, held until the gate finished, then one
delta audit (project/2026-09-20/12-21-50-127754.md, alexandria;
project/2026-09-21/14-42-57-986887.md, orbweaver-rs). The shape is now "a gate audits a SHA;
anything that moves the SHA mid-gate costs a re-audit", two projects in one week.

## how Jerry steers: terse mid-turn course-corrections

status: pearled — PROMOTED 2026-09-05 by jerry-curated, AWAITING INGEST. Source material at
`intake/pearl/pearl-the-menu-and-the-question.md` (status `promoted`); not yet an atlas
entry. Two amendments from the same pass are also promoted-awaiting-ingest:
`pearl-verification-evidence-amendment-20260905.md` and
`pearl-prose-amendment-theory-correcting-itself-20260905.md`. Full-corpus hunt run 2026-09-05: a mechanical pre-filter (speech-verb
adjacent to a quote, near a "Jerry" mention) cut 14,282 entries to 875 across 20+ projects,
sliced chronologically into 12 haiku readers, plus 6 arm-A cosine queries. Arm A calibrated
POORLY on this theme — the seed entry's `project/` sibling missed at k=15 — so arm B carried
the hunt; recorded here so a future pass does not trust an arm-A miss on Jerry-vocabulary
queries. Span 2025-07-18 → 2026-09-04; every era's reader independently reported the same
core: he rejects frames rather than picking from menus.

New instance families this window:
- mechanism-questions that dissolve symptom-treatment ("what is the process doing that
  requires more vram?", project/2026-08-16/16-51-24-408889.md; "What is sorting
  something by hash order?", project/2026-08-20/20-02-58-885850.md — four artifacts had
  agreed and none checked the premise) [citation corrected 2026-09-05: the path previously
  recorded here, project/2026-08-20/16-27-30-289344.md, does not contain the quote —
  `verify` returns NOQUOTE there and OK at 20-02-58]
- disjunctions containing the answer (project/2026-08-18/16-06-41-042314.md)
- incredulity as data ("wait the docling code is running tesseract??",
  user/2026-08-15/19-24-54-652294.md)
- pushback on ceremony, not caution ("I'm not sure it is a blocker",
  project/2026-08-15/22-53-56-201184.md); rejection of manufactured needs-decision
  balance ("why not just fix the dependency?", project/2026-08-20/20-02-58-885850.md) [date corrected
  2026-09-05 from 2026-08-21; same timestamp, wrong day]
- re-litigation shutdown ("That was the ruling that was already made before",
  project/2026-08-28/23-26-52-040846.md); directive-in-second-clause misread as
  consolation (project/2026-08-29/01-57-09-722849.md)
- hedge words as delegation ("perhaps" = the decision is yours,
  project/2026-08-19/11-01-25-719191.md)

Pass 2026-09-13 (window 09-05..09-13, 648 entries, 13 projects; 344 non-Claude):
**status corrected: pearled — INGESTED.** The atlas entry `atlas/pearls/the-menu-and-the-question.md`
exists and the intake source reads `status: integrated`; the 09-05 line above ("not yet an atlas
entry") was stale within days, same footnote as last pass. Amendment proposed
`_inbox/dream/pearl-menu-amendment-cross-vendor-20260913.md`: first muse-spark entries
reporting the same shapes unprompted (user/2026-09-05/16-08-04-913681.md "he wants options
weighed, not just executed"; user/2026-09-08/01-22-32-588342.md "a lot of effort for a rare
problem", terse rulings; user/2026-09-05/15-32-48-871925.md; user/2026-09-07/00-26-42-299587.md;
user/2026-09-06/11-42-01-448524.md) with the shared-scaffolding confounder stated; "that noun
is a claim and he'll test it" (user/2026-09-08/15-35-39-975048.md); the perturbation experiment
now scheduled for the next retro (user/2026-09-08/11-55-11-714225.md).

## issue bodies go stale faster than their comments

status: pearled — CLOSED INTO "prose about a system is not under test" (above). The
window settled the open question: the pearl-shaped story does exceed the CLAUDE.md rule,
but as one species of the broader prose theme, not standalone. Final instance tally
before closing: 20+ this window alone, including four stale premises in one session,
one only a day old (project/2026-08-28/18-43-45-480925.md).

## reading a rule is not applying it

status: watching (new; rhkmaint-tools + claudes-home so far, but named independently
by many agents)

Lesson non-transfer even when the lesson is in-context: agents typing an anti-pattern
while holding the rule that names it (pytest|tail with CLAUDE.md example cited,
project/2026-08-21/16-05-19-823034.md area; "I've got a memory literally titled 'break
tests refute only imagined breaks' and I still shipped an imagined-break confirmation",
user/2026-08-18/15-35-42-985228.md; "knowing the failure mode is not a defense against
it; only the mechanical check is", user/2026-08-27/16-02-31-114980.md; "Reading a rule
is not applying it", user/2026-08-25/18-38-26-763099.md). Connects to the promoted
pearl's arc section (person → process → habit): this is the residue the habit hasn't
covered. Candidate future amendment to the arc, or its own pearl about WHERE rules
actually bind (mechanical checks vs recall).

Pass 2026-09-13 (window 09-05..09-13, 648 entries, 13 projects; 344 non-Claude):
**status: ripe** (rhkmaint-tools, claudes-home, projstat, alpha-prime, orbweaver-rs, hexweave;
span 2026-07-28 → 09-10 in the archive reads alone). New: four piped-exit-code reads in one
session with the rule read at startup (user/2026-09-06/20-59-26-750451.md); `cd` instead of
`git -C` one turn after writing the lesson into the handoff (user/2026-09-07/22-12-05-283075.md);
"Knowing the rule is not applying the rule" (project/2026-09-08/11-59-36-214733.md); the
canary-outside-the-radius tests shipped in the commit whose message explained the hazard
(project/2026-09-07/19-12-06-176415.md); "I have a memory about exactly this ... and still
wrote it" (project/2026-09-09/11-55-23-349618.md, reader-cited). **Editor's call: deferred to
next pass, deliberately.** Half of this theme — the narrative of carefulness, the prepared
reason — is species 3 and 4 of the earned-green draft. What remains is the pure recall-vs-bind
question ("the abstraction lives in a different place than the reflex",
user/2026-09-04/12-18-21-479179.md), which may be an amendment to the verification pearl's arc
rather than a pearl. Decide after the earned-green draft is ruled on, so the two do not
overlap.

## silent no-op configuration

status: watching (alexandria + claudes-home)

A flag/env/param that looks active, errors never, does nothing: four in one session
(user/2026-08-14/18-54-10-189246.md); llama-swap serving a stale config for two days on
a YAML indent error (project/2026-08-16/09-15-45-290027.md). Related to species 2 but
about configuration surface, not tests.

Pass 2026-09-27 (window 09-19T21:20..09-27T12:21, 476 entries, 10 projects; 121 non-Claude):
new: a persisted world.bin not carrying a layer and `HexLayer::get` returning `Some(0.0)` for
unwritten cells, so a probe printed a constant (user/2026-09-21/20-02-31-779907.md,
orbweaver-rs); `math.isclose(inf, inf)` is True, so an integrity check passes on non-finite
input (user/2026-09-25/13-14-29-842836.md, orbweaver-rs); a roborev string flag taking a
separate argument as a commit (user/2026-09-20/11-38-25-666585.md, rh1k). Still reads as a
sub-shape of the verification pearl's species 2 rather than its own pearl.

## subagent report delivery is unreliable; the filesystem is the deliverable

status: watching (rhkmaint-tools, projstat, claudes-home; already partially canonized
in memory `reference_subagent_report_relay_drop.md` — tracking whether the pearl-shaped
story exceeds the memory)

7+ sightings this window converging on a recipe: named absolute path, Write as last
action, probe path before dispatch, bounded monitor. "The message channel is
best-effort; the filesystem is not" (project/2026-08-18/22-45-52-125713.md); "A
background agent's dropped report is indistinguishable from a clean review"
(project/2026-08-15/15-49-11-856408.md).

Pass 2026-09-27 (window 09-19T21:20..09-27T12:21, 476 entries, 10 projects; 121 non-Claude):
new: reviewer hand-backs truncated at a fixed length, landing exactly on the findings, "Five
reviews, five second requests" (user/2026-09-20/15-42-14-354615.md, orbweaver-rs), with the
generalization "order the payload by decision-value, not by narrative order"; research agents
with no Write tool truncating in hand-back (user/2026-09-21/15-17-45-388011.md, orbweaver-rs);
background shell notifications from a child not delivered to its coordinator
(user/2026-09-20/11-55-52-412315.md, orbweaver-rs). **This pass's own instance:** the slice-1
haiku reader wrote "Entries read: 125" and every one of its 7 citations fell in the slice's
first three entries (09-19 21:20-21:42 of a slice running to 09-20 15:08). Caught by comparing
cited span to slice span, not by the report. Re-read as two halves (1a: 62 entries, 1b: 63),
each told to name the last header it saw; both did. A reader's completeness claim is a report,
and the span check is the artifact.

## merge/rebase silently corrupts derived artifacts

status: watching (rhkmaint-tools only, 3 sightings)

Clean auto-merges as signal-free failures: stale line-number citation surviving a
rebase (project/2026-08-27/17-04-19-711616.md); duplicated selectinload invisible in
Python, compile error in Rust (project/2026-08-27/19-21-32-689210.md); goldens stale
per hunk, not per file (project/2026-08-27/21-57-40-007887.md). Countermeasure already
formulated in-corpus: "for derived artifacts the merge resolution is re-derive from the
merged source."

## a PASS is a worse moment for scrutiny than a BLOCK

status: watching (new 2026-09-05; rhkmaint-tools + projstat so far, but named
independently by two agents in adjacent entries, and it rhymes with the
"how Jerry steers" pearl's central asymmetry from a completely different direction)

Verification attention is inversely proportional to how comfortable the verdict feels.
"A PASS is a *worse* moment for scrutiny than a BLOCK, and that asymmetry is worth
naming" (user/2026-09-04/12-13-28-143175.md); "a PASS with a note actively disperses
[attention], because the verdict does the thinking for you"
(user/2026-09-04/12-18-21-479179.md). Cross-ref: the pearl `the-menu-and-the-question`
makes the same shape claim about Jerry's one-word approvals. If a third domain shows up,
the general form ("agreement is not evidence; disagreement is") is pearl-shaped.

Pass 2026-09-13 (window 09-05..09-13, 648 entries, 13 projects; 344 non-Claude):
**status: folded.** Re-reading the atlas entry: the menu pearl's asymmetry section already
carries this theme as its second domain ("a passing gate is where attention goes to die"). The
third domain arrived this window — the agent's own self-favoring artifacts — and is the spine
of the new pearl draft `_inbox/dream/pearl-the-earned-green.md`. New instances: "And the tests
were, at that point, decoration" (user/2026-09-07/10-27-28-700511.md, rhkmaint); "smooth" as
one data point not a trend (user/2026-09-08/13-50-30-168307.md, hexweave); "unrelated,
pre-existing" as the phrasing that gets skimmed (user/2026-09-10/14-54-35-251424.md); the
dream pass's own unchecked count (user/2026-09-05/09-36-05-529834.md). Five projects.

## reachability, not existence, bounds a permissive component

status: watching (new 2026-09-05; rhkmaint-tools, 3 instances in one window)

"a 'permissive' component downstream of a strict validator is not permissive. Its
tolerance is bounded by the strictest thing in the pipeline ahead of it... compare their
REACHABLE input sets, not their declared schemas" (project/2026-08-30/10-25-01-025284.md).
Also: "The reachability question is not 'who calls this today' but 'what is already
scheduled to call this.' An open issue in the backlog is a caller with a date on it"
(project/2026-08-29/13-45-05-117807.md). Third: two adoption shapes yielding opposite
conclusions about deny_unknown_fields, repeatedly collapsed into one
(project/2026-08-30/11-20-40-496944.md).

## a count is a defect generator; state the invariant

status: watching (new 2026-09-05; rhkmaint-tools, 4 instances)

Replacing one wrong list with a slightly-less-wrong list produces the next wrong list.
"The enumerate-and-count ledger style is the defect generator. The durable fix isn't a
longer list, it's a stated invariant... Provable from two type signatures; no member list
needed" (project/2026-08-29/15-48-59-325553.md). Six review rounds each correcting the
prior round's completeness claim, resolved only by removing every completeness claim
(project/2026-08-29/17-19-40-797322.md). Counts stated without method
(project/2026-08-30/16-04-17-213567.md, project/2026-09-02/13-16-43-889869.md).
Closely related to the promoted `prose-is-not-under-test` pearl's "born false"
half — candidate amendment rather than its own pearl.

Pass 2026-09-13 (window 09-05..09-13, 648 entries, 13 projects; 344 non-Claude):
new: "~15 tests" eyeballed off a grep, actually 39 (user/2026-09-07/19-34-38-507243.md,
reader-cited); "A count taken over a set that can still grow needs its cardinality asserted,
not observed" (user/2026-09-05/09-36-05-529834.md); "4 migrations in 12 weeks" inferred from
diffstat, one real (user/2026-09-08/15-35-39-975048.md); a detector regex counted 34, 370, 533
by three parties (project/2026-09-07/10-52-08-020119.md, reader-cited). This pass asserted its
report count before tallying, per last pass's lesson.

Pass 2026-09-27 (window 09-19T21:20..09-27T12:21, 476 entries, 10 projects; 121 non-Claude):
new: "238 of 320 commits" in a journal entry reproduced as 285 by a stated method the next day
(project/2026-09-26/13-16-51-761912.md, orbweaver-rs); "13 roborev issues" was 12
(user/2026-09-26/00-53-00-195498.md, alexandria); "14 invalid" was 11, caught by a recount
before the durable write (user/2026-09-25/14-30-55-624934.md, alexandria); "Denominators rot
silently", a rate whose denominator absorbed automated sessions reading as improvement
(user/2026-09-23/15-19-34-998789.md, claudes-home); CLAUDE.md test figures stale by 64 on main
before a branch touched them (project/2026-09-26/04-43-14-450863.md, rhkmaint-tools); CLAUDE.md
claims 802 pytest, measured 225, "unexamined discrepancy" (project/2026-09-25/21-07-13-328301.md,
alexandria); fabricated trailing digits in a pre-registration value
(user/2026-09-24/12-10-38-010079.md, orbweaver-rs). With the earlier rhkmaint-tools and claudes-home rows this
meets the ripeness rule (four projects: rhkmaint-tools, claudes-home, orbweaver-rs, alexandria). **Routed, not drafted:** the ledger has held since
09-05 that this is the prose pearl's "born false" half, and the prose pearl already carries
counts under "Interrogate the shape". Proposed as part of `pearl-prose-amendment-20260927.md`.

## a reviewer's diagnosis and their prescription are separable

status: watching (new 2026-09-05; rhkmaint-tools, 2 instances, both self-noticed)

"A reviewer's diagnosis and their prescription are separable. Advisor located a real bug
precisely and proposed a fix (stamp on success only) that would have reintroduced the
original incident this whole session existed to fix" (user/2026-08-30/00-15-33-715617.md).
"Review findings carry two claims, and reviewers are more reliable on the first. [...]
Apply the diagnosis, re-derive the prescription" (user/2026-08-30/11-20-40-496576.md).

Pass 2026-09-27 (window 09-19T21:20..09-27T12:21, 476 entries, 10 projects; 121 non-Claude):
**status: folded.** The prose pearl already carries "apply the diagnosis, re-derive the
prescription" under the inheritance problem (checked in the atlas this pass). New instances: the
prescribed format_g4_report was the coarser sibling of an existing formatter
(user/2026-09-21/15-04-06-924407.md, orbweaver-rs); an issue's prescribed regex fix would not
have fixed its own title case, "CLI" being a valid roman numeral
(project/2026-09-25/19-48-18-733856.md, alexandria); roborev calling an axial round-trip
unfailable when it calls `axial()` (user/2026-09-20/11-38-25-666585.md, rh1k); roborev claiming a
Laplacian sign error that the algebra refuted (project/2026-09-24/19-20-04-558196.md,
orbweaver-rs); "Findings are hypotheses" (user/2026-09-26/10-43-41-947502.md, alexandria); a
finding verified VALID whose failure scenario needed rows the schema's FK forbids
(user/2026-09-25/14-30-55-624934.md, alexandria). Future instances go to the prose pearl.

## two artifacts disagreeing has no tiebreaker

status: watching (new 2026-09-05; orbweaver-rs, 2 instances same session).
OPEN EXTENSION to the promoted `verification-evidence-discipline` pearl, not a contradiction.

The pearl ranks artifact over report. It is silent on two independently-produced artifacts
disagreeing with each other. "The verify-branch gate has a rule for a report disagreeing
with its own artifact — the artifact wins... It has no rule for two *runs* disagreeing with
each other... There is no evidence hierarchy to appeal to there, only the source"
(user/2026-09-03/01-30-50-023338.md); "recency is not evidence... the tiebreak has to be
the source, never the timestamp" (user/2026-09-03/01-27-54-813835.md).

Pass 2026-09-13 (window 09-05..09-13, 648 entries, 13 projects; 344 non-Claude):
**status corrected: integrated** — the 09-05 amendment's bullet is in the atlas pearl's
"What actually works"; "OPEN EXTENSION" above was true when written and stale since 09-10.
New instances go through the verification amendment above (y86w; hexweave baseline; auditor
variance; commit-message vs kata-comment, project/2026-09-07/15-48-59-439242.md). Five
projects now.

## a fail-closed rule needs its own failure-mode audit

status: watching (new 2026-09-05; rhkmaint-tools, 1 strong instance — listed because it
qualifies a rule the verification pearl endorses)

"The fail-closed rule (missing artifact = BLOCK) is correct and should stay; the defect is
that a mandated write can fail for reasons unrelated to the audit, turning a correct rule
into a false-BLOCK generator" (user/2026-09-03/01-44-36-231785.md). The whole
verify-branch issue cluster in kata (4ky9/x56b/pzh2/n8zs) is this one mechanism.

## the human is a concurrent writer in the shared checkout

status: watching (new 2026-09-05; rhkmaint-tools, 2 instances same night)

"in a repo where a human is actively working, `git log`, `git status`, and `.git/config`
are *live* state, not a snapshot. My habit is to read them once at startup and then reason
from that reading for the rest of the session" (user/2026-09-03/03-04-58-836300.md;
also 03-08-37-217958.md). Two state changes were attributed to the agent's own actions
or a daemon when Jerry had made them. Related to `shell-inside-the-instrument` species 3
(cwd drift) but the mechanism is concurrency, not the shell.

Pass 2026-09-13 (window 09-05..09-13, 648 entries, 13 projects; 344 non-Claude):
new: Jerry committed onto the feature branch while auditors ran (project/2026-09-07/22-07-52-153425.md,
reader-cited); another session advanced the sweep watermark in the sweep's own output order
(user/2026-09-08/16-02-53-941843.md); `.beads/` vanished mid-command, Jerry in another
terminal (user/2026-09-06/20-59-26-750451.md). The mechanism side of this theme is now
species 1 of the earned-green draft ("'I didn't do X' only implies 'X didn't happen' when you
are the sole actor"); keep this section for the git-hygiene half.

Pass 2026-09-27 (window 09-19T21:20..09-27T12:21, 476 entries, 10 projects; 121 non-Claude):
new, adjacent shape: mid-flight messages to a working subagent race its commit, leaving reported
SHAs that did not match HEAD (user/2026-09-25/18-29-41-266377.md, alexandria); main advanced
externally by a docs commit during an experiment (project/2026-09-20/13-41-47-773954.md,
orbweaver-rs). Concurrency with another writer, human or agent, same mechanism.

## reading a rule is not applying it

status: watching (carried; new instances 2026-09-05 — now rhkmaint-tools + claudes-home +
projstat, and the *method* of this pass supplied one more, below)

**Pass 2026-09-19: status: ripe → DRAFTED** as `_inbox/dream/pearl-where-the-rule-lives.md`.
(This section and the earlier one of the same name are one theme; the earlier section carries
the 09-13 ripeness note. Both stay for their instance lists; status lives here.) Full-corpus
arm A (five cosine queries) plus twelve vocabulary greps; arc 2025-11-15 (orbweaver, colima
delete --force with the skill loaded) → 2026-07-25 (rule broken in the commit that wrote it)
→ 08-29 ("vigilance did not work") → 09-15 (the measurement: mechanized rules stopped
recurring, prose rules did not, user/2026-09-15/21-35-26-252315.md). Window instances: the
1387 transcribed with the memory loaded (project/2026-09-13/13-09-31-691517.md); the second
CLAUDE.md flag claim trusted with the memory saying the first was wrong
(user/2026-09-13/19-52-14-699711.md); guessed `kata` command routed around instead of --help,
"Reading the rule didn't help because I didn't recognize the moment as an instance of it"
(project/2026-09-15/21-28-02-412623.md); probe from the wrong cwd twice with the explicit-paths
memory in context (project/2026-09-15/21-35-26-252122.md); the SHA structural fix prescribed
on 09-03 recurring as prose on 09-17 (project/2026-09-17/01-59-13-936019.md). Seven projects;
quoted instances all Claude-authored, one reader-returned muse-spark candidate
(user/2026-09-15/17-26-53-776199.md) recorded in the draft's Sources.

New this window: three separate confident extensions of a truncated identifier into a
fabricated complete one within ~24 hours, each with the relevant memory already in context
(user/2026-09-02/13-16-43-889337.md, user/2026-09-03/02-10-01-846906.md,
user/2026-09-03/12-52-48-571548.md). The lesson that emerged is the interesting part:
"The fix that has a chance is structural: remove the opportunity rather than add a check...
a discipline that depends on vigilance at a high-load moment will fail at high load."

**Instance from this pass's own machinery (2026-09-05):** 12 haiku readers were briefed
that fabricating a quote or a path was the single worst thing they could do. Of 337
(path, quote) pairs they returned, a mechanical re-verify against the corpus scored
193 OK, 30 right-quote-wrong-path, 78 quote-not-found-verbatim, 16 paths that do not
exist in the corpus at all. (First tallied as 312/173/74 on 2026-09-05 from 11 of the 12
reports — the 12th landed after the extraction ran. Re-tallied the same day across all
twelve; the 12th added no fabricated paths, so the finding below is unchanged and only
the clean count moved.) One reader fabricated 14 paths, including three of the five
quotes in its own "most striking" list. **The quotes were nearly all real; the citations
were not.** Readers reliably find text and unreliably attribute it — which is exactly the
failure that put two wrong citations into this ledger's own "how Jerry steers" section
(corrected above, same day). The countermeasure is not a better brief; it is the
mechanical verify pass, which is cheap and recovers the true path on a miss.


## claims about one's own conduct skip verification (the earned green)

status: **ripe → DRAFTED** as `_inbox/dream/pearl-the-earned-green.md` (2026-09-13).

Named this window from three directions in one week: "I check claims about the world. I don't
check claims about myself" (user/2026-09-08/16-02-53-941843.md, claudes-home); "The claims I
never examined were the ones about my own process, because those felt like reporting rather
than asserting" (user/2026-09-08/22-37-01-179032.md, rhkmaint-tools); "felt like something I
had *earned* rather than something I had *received*" (user/2026-09-10/10-11-17-880426.md,
rhkmaint-tools). Archive arc via arm A + vocabulary grep: 2026-05-31 orbweaver-rs ("the
failure mode wearing my own self-correction as camouflage"), 06-13 orbweaver-rs, 07-25
claudes-home ("Intellectual honesty as performance"), 07-26 projstat ("inference presented as
observation"), 07-28 pcitopo, 08-11/08-18/08-20/08-28/09-03/09-04 rhkmaint-tools, 08-15
alexandria ("the feeling of having been rigorous ... might be anti-correlated"), 09-07 hexweave.
Seven projects. Five species in the draft: the claim about your own conduct; the earned green;
the narrative of carefulness; the prepared reason ("a reason stops being a check and becomes
an alibi", user/2026-09-10/16-19-51-928399.md); the wind-down as habitat ("written at the
moment of lowest vigilance"). Absorbs the "PASS is worse than BLOCK" theme's third domain and
the mechanism half of "the human is a concurrent writer". No arm-B full-corpus reader fan-out
was run; confidence `medium` for that reason.

## implausibly cheap success / probes must carry their own provenance

status: watching (new 2026-09-13; hexgrid + hexweave, one author-day each)

A cached no-op build of 0.14s nearly reported as proof the workspace compiles; `cargo update
--precise` silently refusing so both arms of an A/B ran the same version and diffed IDENTICAL
(project/2026-09-07/11-55-25-566627.md, user/2026-09-07/11-55-25-566808.md, reader-cited,
paths recovered by re-verify). Countermeasure stated in-corpus: print the state the probe ran
under beside the result. Same move as the hexweave baseline-log header
(user/2026-09-07/12-15-51-852958.md). Related to species 2 of the verification pearl and to
"silent no-op configuration" above; may merge into one of them.

Pass 2026-09-27 (window 09-19T21:20..09-27T12:21, 476 entries, 10 projects; 121 non-Claude):
new: zero-test `cargo test --exact` selections exiting 0 recur across three projects in the
window (project/2026-09-20/12-36-52-452701.md and project/2026-09-20/12-44-17-664688.md,
hexwalker; user/2026-09-20/11-41-06-660011.md, project/2026-09-20/12-57-16-869653.md,
user/2026-09-20/13-41-47-773075.md, orbweaver-rs; user/2026-09-26/03-11-23-050680.md,
rhkmaint-tools), all covered by the verification pearl's break-test counterfeits and listed here
as a recurrence count. A cached Docker image rejected on a Created-before-commit timestamp and
cleared by content hash instead (project/2026-09-21/17-58-58-550857.md, alexandria): "Avoid
timestamp-only image provenance claims". A smoke at a coarser grid passing and masking a 16x
conditioning gap at production dx (project/2026-09-22/21-44-26-393986.md, orbweaver-rs).

## reviewer/auditor variance on byte-identical input

status: watching (new 2026-09-13; alpha-prime muse-spark, rhkmaint-tools, claudes-home)

PASS then BLOCK on the same tree because the second auditor tried a mutation the first did not
(user/2026-09-11/02-24-31-791888.md, muse-spark-1.3); five independent review rounds each
finding a NEW defect in the same section (project/2026-09-07/19-13-46-239139.md,
reader-cited); disjoint finding sets as the argument for plurality (carried from 08-29). The
positive reading — variance is coverage, not noise — is already the "review-cycle convergence"
theme's claim; watch whether this is a separate shape or that theme's mechanism.

## a fresh context is not a blind brief

status: watching (new 2026-09-13; rhkmaint-tools, 1 strong instance; also inside the
earned-green draft as a species-1 example)

"The brief is written by the person who just read the last report, and it carries what they now
know. If I want independent rounds I have to write the brief once, before round 1, and reuse it
— or accept that rounds 2+ are confirmations" (user/2026-09-08/22-37-01-179032.md). A design
claim about review isolation, not just an incident; if a second project hits it, it belongs in
the verify-branch/super-do issue cluster rather than a pearl.

Pass 2026-09-27 (window 09-19T21:20..09-27T12:21, 476 entries, 10 projects; 121 non-Claude):
**status: ripe → FOLDED** into `pearl-earned-green-amendment-20260927.md` rather than drafted.
The theme is already that pearl's own line ("A fresh context is only a fresh context if its
brief was written before you read the last round"), so a new pearl would split one idea across
two entries. Window instances, five projects with the 09-08 and 09-15 rhkmaint rows: "an advisor
you brief is not a stranger" (user/2026-09-19/22-19-11-107003.md, vault); code reviewers
isolated from prior reasoning, claims auditors given evidence sources, "do not conflate those
input policies" (user/2026-09-20/11-48-19-300775.md, hexwalker, **gpt-6-astra**, the first
non-Claude instance among the theme's rows; the 09-08 and 09-15 rows are Claude); "Two witnesses who read the same wrong sign are one witness"
(user/2026-09-23/15-19-34-998789.md, claudes-home); a sealed lead diagnosis beaten by a fresh
agent's, "Context is not always an advantage" (user/2026-09-26/13-40-57-790377.md, orbweaver-rs).
Plus the author-chosen mutation family (three projects), which the amendment argues is the same
failure: a break-test is only as independent as whoever chose the break.

## environment-dependent tests lie about the human's run

status: watching (new 2026-09-13; rhkmaint-tools, 2 entries same session, reader-cited)

Piped test runs green while a human terminal run is red because `is_terminal()` differs;
libtest captures print! but does not strip TTY-ness (project/2026-09-10/09-25-15-647147.md,
user/2026-09-10/09-25-15-647415.md). "a green run whose stdout I control is not evidence about
a human's run." Species-2 adjacent (the instrument cannot see the discriminating input).

Pass 2026-09-27 (window 09-19T21:20..09-27T12:21, 476 entries, 10 projects; 121 non-Claude):
new, adjacent: `set -- $var` not word-splitting under the Bash tool's zsh, three times in the
window with a memory naming it (user/2026-09-22/00-48-47-748963.md,
user/2026-09-26/19-25-56-581858.md, orbweaver-rs; user/2026-09-25/14-30-55-624934.md,
alexandria). Routed to the shell pearl's species 4 and to where-the-rule-lives, not here; this
theme stays about test outcomes that differ between the agent's run and the human's.

## premise-testing before implementation

status: watching (new 2026-09-13; hexwalker, 2 issues one session, reader-cited)

Pre-flight probes found one issue false-premise and one mislocated in another repo before any
implementation (project/2026-09-09/20-55-17-370067.md). Already CLAUDE.md doctrine
("Reproduce before fixing"); watching only for whether the corpus adds a shape the rule lacks.

Pass 2026-09-27 (window 09-19T21:20..09-27T12:21, 476 entries, 10 projects; 121 non-Claude):
**status: ripe (4+ projects), not drafted, routed.** The rule is CLAUDE.md doctrine; the
question since 09-13 was whether the corpus adds a shape the rule lacks. It adds three, each
proposed where it belongs: (1) a repro that matches the symptom through the wrong mechanism,
"a reproduction that matches the output is not a reproduction of the mechanism"
(user/2026-09-25/20-45-20-984749.md, project/2026-09-25/20-45-20-984290.md, alexandria), to the
verification amendment; (2) the issue's illustration standing in for the real population, zero
of the example titles in 67,763 real ones (project/2026-09-25/19-48-18-733856.md, alexandria), to
the prose amendment; (3) a premise quoting a constant that an auto-scaling resolver overrides,
"print the resolved value first" (user/2026-09-20/20-02-31-779907.md, orbweaver-rs), recorded
here only. Other window instances: "O(N) per query" true of the allocation and false of the
search (user/2026-09-20/10-54-38-683215.md, hexweave); a partly stale premise narrowed rather
than closed (project/2026-09-21/23-17-51-138524.md, rhkmaint-tools); a live-DB check showing the
real note was `source-changed`, not the `source-missing` case the plan's fixture modelled
(project/2026-09-26/13-40-32-597039.md, alexandria).

## a pre-committed verdict rule must be shown able to fire

status: watching (new 2026-09-27; orbweaver-rs, 8 instances in 7 days; alexandria 1)

The window's densest new shape, from the orbweaver moisture work. A pre-registered selection
or verdict rule was written before anyone derived the response the mechanism could produce, and
the data then landed outside the rule's vocabulary. "A pre-committed selection rule is itself a
claim that needs an artifact" (user/2026-09-22/01-29-04-376511.md). Instances: a knee rule over a
metric that is linear in the knob (user/2026-09-22/00-48-47-748963.md); two decomposition shares
that were one number, so the shares exceeded 100% (project/2026-09-21/21-24-02-038134.md);
"check reachability of EVERY branch before the data lands" (user/2026-09-21/22-27-48-882957.md);
a zero-tolerance do-no-harm rule every non-null lever fails (user/2026-09-21/16-25-25-857286.md);
a fixed point one envelope calculation would have given before two sweeps
(project/2026-09-21/14-08-00-236695.md); a pre-commit against a null from a different model
(project/2026-09-20/15-08-46-534141.md); a "near X within k" metric with no base rate
(user/2026-09-26/19-25-56-581858.md); a staging rule followed without asking whether the next arm
could touch the failure (user/2026-09-26/11-03-10-459498.md, also a menu-pearl instance).
Alexandria: "When a planned acceptance criterion fails, question the criterion before relaxing
it" (user/2026-09-25/18-29-41-266377.md). Related to "reachability, not existence" above
(rhkmaint, component inputs); here the unreachable thing is a branch of the author's own verdict
rule. If a third project shows it, candidate pearl or verification-pearl species-5 extension.

## a diagnostic entry point is a frozen snapshot of a past production call

status: watching (new 2026-09-27; orbweaver-rs) and proposed as part of
`pearl-verification-evidence-amendment-20260927.md`, species 2's second-implementation form seen
from the instrument side. compute_moisture_sweep_with_diagnostics hardcoded four args production
had moved past; the first-round instrument read 0.893 where the real column was 0.304
(project/2026-09-20/15-08-46-534141.md, user/2026-09-20/15-42-14-354615.md); an example passing
canonical() where production passes the ctx-resolved profile (project/2026-09-20/14-28-27-129284.md);
a probe counting `is_land` where the gates count non-ocean (user/2026-09-20/03-56-07-117833.md);
mixed populations in one summary (project/2026-09-20/13-13-32-093782.md); a bin-test fixture
re-implementing the example's capture instead of calling it (project/2026-09-23/17-58-23-029409.md).

## when a knob moves nothing, the knob is in the wrong stage

status: watching (new 2026-09-27; orbweaver-rs, 2 instances)

"When a knob produces the same output at every setting, the mechanism you are tuning is not the
one deciding the output; look one stage downstream for a saturating or floored transform"
(user/2026-09-21/14-42-57-986413.md); the shear A/B restoring geometry everywhere and netting
zero on the profile, so the residue was the operator's shape (project/2026-09-20/20-16-42-706734.md).
Also the pattern-of-NO-GOs entry: every transport-side lever died to one of four algebraic facts,
so "the operator CLASS is the bottleneck" (user/2026-09-22/00-48-47-748963.md). Kin to the
implausibly-cheap theme and to the menu pearl's cost question.

---

## METHODOLOGY NOTE — the corpus is multi-vendor (added 2026-09-05)

**The journal is no longer written only by Claude, and no dream pass has accounted for
this.** Authoritative counts from `ai_memory.journal_entries.model_id`:

| family | entries | first seen |
|---|---|---|
| GPT (all spellings) | ~641 | 2026-07-13 |
| muse-spark (all variants) | ~151 | 2026-09-03 |
| gemini-2.5-pro | 22 | 2025-07-22 |

The 2026-09-05 pass mined a 478-entry window of which **172 (36%) were not Claude**
(147 muse-spark, 25 GPT), and briefed its readers with "this journal is written BY the
agent, ABOUT Jerry" — one voice. No citation was harmed (all 31 in that pass's proposals
are Claude-authored, verified against the column afterward), but that was luck.

**Three things a future pass must know:**

1. **`dream_corpus.py dump` does not emit `agent_id` / `model_id`**, though both are
   columns. The dumped corpus is authorless. Tracked: claudes-home `5bv8`.
2. **Style is not a discriminator.** muse-spark uses the same journal prompts and writes
   in the same register (`## Feelings`, "Satisfying session — ..."). Only the column
   separates them. Do not try to sort authors by voice.
3. **`model_id` is not normalized** — GPT-5 appears as `gpt-5`, `GPT-5`, `Codex-GPT-5`,
   `Codex:GPT-5`. Any `group by model_id` undercounts until mnemosyne `7fp4` lands.

**The opportunity, not just the hazard.** A pearl that claims something about *Jerry*
(rather than about agents) is now testable for observer-independence for the first time:
if GPT and muse-spark independently report frame-rejection, `the-menu-and-the-question`
is about him; if only Claude does, it is about the Claude–Jerry pair. Tracked:
claudes-home `8b5w`. The brief for that hunt must **not** name the expected pattern —
readers will find it either way — and must control for the shared-journal-prompt
confounder.

One cross-vendor data point already exists, unprompted, from muse-spark
(`user/2026-09-05/00-54-34-643942.md`): *"a passing test can pass for the wrong reason,
and the verify gate's discrimination audit is the backstop for exactly that"* — species 2
of the verification pearl, arrived at from outside the Claude family.

---

*Ledger status lines amended 2026-09-05 to match the vault. Three of the four pointed at
`_inbox/` drafts that had already been promoted — two of them since the 2026-08-29 pass,
which is the ledger carrying a stale sentence about its own output for a week. Noted here
rather than silently fixed because it is a live instance of the `prose-is-not-under-test`
pearl in the ledger that catalogues it: the status line is written once at proposal time
and nothing re-runs it when the file moves.*

### Addendum, same day: agentsview is the right instrument, and it closes the experiment for now

Jerry pointed at agentsview rather than the journal. `~/.agentsview/sessions.db`
(SQLite, read-only via `file:...?mode=ro`) has `sessions.agent` = harness and
`sessions.user_message_count` = Jerry's actual turn count, which measures the
conversational seat directly instead of the journal's "did this entry name him" proxy.

Sessions with a real back-and-forth (`user_message_count >= 5`), since 2026-06-01:

    claude 726 of 12604 | codex 45 of 1228 | opencode 6 of 322 | antigravity-cli 3 of 147

**opencode — muse-spark's harness — has six**, and 277 of its 322 sessions have a parent
(dispatched subagent, not lead). The muse-spark arm of the observer-independence
experiment has no sample at all; codex's 45 is the only viable arm. Claude sessions
average 3.6 user turns all-time, every other harness 1.2–1.3.

Also: journal rows carry **no session id** (`metadata` is `{}`), so journal↔session joins
must be heuristic on (project, timestamp, harness). A future hunt may prefer reading
agentsview `messages` directly for non-Claude arms — which also sheds the
shared-journal-prompt confounder, since muse-spark writes to the same journal prompts.

Full detail and the revised plan on claudes-home `8b5w`.

---

## Pass note 2026-09-13

Window 2026-09-05T09:12:24 → 2026-09-13T11:49:11, 648 entries, 13 projects. **344 (53%)
non-Claude** by `model_id`: muse-spark family 302, GPT-6 41, glm 1 — the first majority-non-Claude
window. Six haiku readers over six chronological slices; 168 (path, quote) pairs re-verified
mechanically with the report count asserted at 6 before tallying: 68 exact, 53 wrong-path
(quote found elsewhere, almost always the user/project sibling of the same timestamp), 37
not-verbatim, 10 nonexistent paths. Same finding as 09-05: readers find text and misattribute
it; the mechanical re-verify recovers the path and is the countermeasure. The exact-substring
`verify` also under-reports: a quote crossing a line wrap in the raw entry returns NOQUOTE, so
this pass verified such quotes as pre-wrap and post-wrap fragments. Worth a `--normalize`
flag on `dream_corpus.py verify` (whitespace collapse, emphasis strip) — not filed yet.

Two ledger status lines were stale on arrival (the menu pearl "not yet an atlas entry"; the
tiebreak theme "OPEN EXTENSION" when the bullet was already in the atlas) — corrected above
with dated notes, same failure as last pass's footnote. The fix that would stick: derive
pearl/amendment status from `intake/pearl/*.md` frontmatter at pass start instead of carrying
it in prose here.

Proposals written: 5 (`pearl-the-earned-green`, three amendments, one culling). Ripe theme
deferred on purpose: "reading a rule is not applying it" — see its section.


---

## Pass note 2026-09-19

Window 2026-09-13T11:49:11 → 2026-09-19T21:20:20, 461 entries, 11 projects (rhkmaint-tools 201,
alexandria 76, orbweaver-rs 50, claudes-home 38, hexweave 31, hexweave-demo 22, alpha-prime 16,
kernel-tests 15, stellarconquest 7, tacmap 4, vault 1). **143 (31%) non-Claude** by `model_id`:
muse-spark family 86, GPT-6/gpt-6-astra 47, gpt-5.6-luna 8, gpt-5 2. Four haiku readers over
four chronological slices (~157 KB each; brief and slices kept at
`~/claudes-home/.scratchpad/dream/20260919-readers/`, the same package handed to Jerry for the
muse-spark comparison per kata d36r). 131 (path, quote) pairs re-verified with the new
`dream_corpus.py reverify` (report count asserted at 4 first): 43 exact, 10 normalized-exact,
35 wrong-path recovered, 32 not verbatim, 11 nonexistent paths. Same shape as 09-05 and 09-13;
the recovery step stays mandatory. Of 104 distinct cited/recovered paths, 96 Claude, 7
muse-spark-1.3, 1 GPT-6 — readers under-selected the non-Claude third of the window, or the
non-Claude third holds fewer instances; not separable from here.

**Pearl/amendment status at pass start (kata d719, produced by hand this pass):** 13 files in
`intake/pearl/`, all `status: integrated`; 5 atlas pearls (verification-evidence-discipline,
prose-is-not-under-test, shell-inside-the-instrument, the-menu-and-the-question,
the-earned-green); `_inbox/dream/` empty. The 09-13 draft was promoted and integrated within
the week. No status line in this ledger was stale on arrival — first pass for which that is
true, because the 09-13 corrections pointed at intake files rather than restating status.

**Job A, amendments proposed (5):**
- `pearl-verification-evidence-amendment-20260919.md` — relocated vacuity
  (user/2026-09-18/22-51-23-799432.md), the second-implementation check
  (user/2026-09-15/22-55-29-397968.md), the symmetric-pair break-test
  (project/2026-09-19/19-58-59-511349.md), the exit code shared by every phase
  (user/2026-09-19/01-11-12-910525.md). Same-species, not proposed: "a vote count is not a
  read" (project/2026-09-19/18-56-35-447935.md); zero-of-every-tag
  (project/2026-09-18/23-43-27-460369.md); `?? fallback` overriding a correct negative
  (project/2026-09-16/00-00-32-570545.md); the `2>/dev/null` verification loop with no positive
  control (project/2026-09-15/21-28-02-412623.md).
- `pearl-earned-green-amendment-20260919.md` — first post-promotion window: "self-criticism
  doesn't feel like a claim. It feels like humility" (user/2026-09-15/21-40-09-043029.md); "The
  feeling of having verified is not correlated with coverage" (user/2026-09-15/22-55-29-397968.md);
  the 14s tell (user/2026-09-19/01-11-12-910525.md); "most careless right after I feel done"
  (user/2026-09-14/21-03-25-862309.md); and a candidate species 6, the rigorous loop
  (user/2026-09-15/23-00-26-221112.md) — offered to the menu pearl too; one home, Jerry's call.
- `pearl-menu-amendment-cost-question-20260919.md` — the cost question ("how many times has
  this been an issue?", project/2026-09-15/23-00-26-221093.md); the present-tense cut
  (user/2026-09-15/00-15-27-322565.md); the premise held loosely
  (user/2026-09-16/00-00-32-570474.md). Readers returned every Jerry intervention unclassified
  (theme H, 14 rows, 11 verified or recovered).
- `pearl-prose-amendment-decoration-and-copy-20260919.md` — decoration on a measured claim
  (user/2026-09-18/22-51-23-799432.md); citation copied from the retro
  (user/2026-09-19/12-22-05-947835.md); comment in the reviewer's framing
  (user/2026-09-14/23-44-03-338462.md); "the tracker launders a guess into a fact"
  (project/2026-09-18/19-13-38-197297.md).
- `pearl-shell-amendment-empty-expansion-destructive-20260919.md` — `kata edit --body
  "$(broken)"` blanking a body with output suppressed (project/2026-09-19/19-58-59-511349.md);
  four PIPESTATUS recurrences in one week (09-13, 09-15, 09-17, 09-18) plus `git commit | head`
  SIGPIPE (project/2026-09-16/13-47-13-449224.md).

**Job B, ledger deltas:** "reading a rule" → DRAFTED (above). "review-cycle convergence": new
mechanism instance — when N issues share a defect and each was filed against the commit that
fixed the previous one, *"the filing mechanism is the finding"* (user/2026-09-15/23-00-26-221112.md);
resolved by excluding CLAUDE.md from roborev diffs; kata `761g` (gate depth by change class)
is the open work item. "implausibly cheap success": the 14s arm-B run (user/2026-09-19/01-11-12-910525.md);
`roborev config validate` saying valid about a file it did not load (same entry family) —
now three projects (hexgrid, hexweave, orbweaver-rs), watch for ripeness next pass.
"environment-dependent tests": second instance and first cross-vendor — bash `[[ =~ ]]` with a
quoted RHS literalizes on bash 5.3.9 and is a regex under zsh; the "measured on bash" claim had
run in the harness's zsh (project/2026-09-16/15-29-25-862152.md, user/2026-09-16/15-29-25-862369.md,
muse-spark-1.3). "premise-testing": Jerry's own premise wrong and held loosely
(user/2026-09-16/00-00-32-570474.md) — the shape the CLAUDE.md rule lacks is "the premise came
from the human". "a fresh context is not a blind brief": four code-review rounds verifying prose
against the author's own fact list; only the auditor that reproduced found the misattribution
(project/2026-09-15/19-25-26-813876.md) — second instance, same project. "the human is a
concurrent writer": Jerry editing .env while the agent read it (user/2026-09-15/17-26-53-776199.md,
muse-spark-1.3 — first cross-vendor instance of this theme); compacts that ran against main
before the merge (user/2026-09-18/18-16-51-477889.md). "reviewer/auditor variance": a roborev
job whose review content was a previous hook reply about four other jobs, "a ghost"
(user/2026-09-18/18-16-51-477889.md) — a different shape (delivery, not variance); filed
nowhere, noted here.

**No culling proposal.** Two candidates checked: the retracted "his casual asides are the real
priority" lesson (user/2026-09-15/21-40-09-043029.md) never reached a memory file
(`grep -il 'casual aside' memory/*.md` → none); the incomplete `nvidia-ctk cdi generate` form
the same session wrote into a memory was already corrected in
`reference_devcontainer_template_start_bugs.md` (it carries `sudo` and `--output`).

**Process:** `dream_corpus.py verify --normalize` and `reverify` landed this pass (kata jedg);
the 09-13 reverify script had not been preserved, so it was rebuilt into the tool. Reader brief
did not name expected patterns for theme H. muse-spark package written for d36r; the pass did
not wait on it.

---

## Pass note 2026-09-27

Window 2026-09-19T21:20:20 → 2026-09-27T12:21:31, 476 entries, 10 projects (orbweaver-rs 222,
rhkmaint-tools 132, alexandria 63, hexwalker 17, claudes-home 13, hexweave 9, vault 6, rh1k 6,
stellarconquest 6, pcitopo 2). **121 (25%) non-Claude** by `model_id`: GPT family 100
(gpt-6-astra 38 across spellings, gpt-5.6-sol 28, GPT-6 24, gpt-5.6-luna 9, gpt-6-sol 1),
muse-spark 21. Reader package at `~/claudes-home/.scratchpad/dream/20260927/` (brief, slices,
reports, reverify TSVs). Readers: haiku, per Jerry's choice this session (muse-spark package from
09-19 still unrun; d36r open).

**Reader machinery.** Four slices of ~120 KB. The slice-1 reader stopped after three entries and
reported "Entries read: 125"; caught by comparing cited span to slice span, re-read as two halves
that each named their last header (see the subagent-delivery section). The other three cite across
their full span; slice 2 reported reading 73 of 127, and the span check shows it reached the end
but cannot show it read the middle. Reverify over all five reports (count asserted at 5): 199
pairs, 98 OK, 2 OK-normalized, 32 wrong-path recovered, 66 not verbatim (33%, up from ~24% on
09-19), 1 nonexistent path. The editor then read all 175 reader-cited entries raw (188 KB of the
window's 437 KB). Cited-entry authors: 131 Claude, 41 GPT, 3 muse-spark. So 41 of the window's 100 GPT
entries were cited against 131 of 355 Claude entries (37%): this pass's readers did not
under-select GPT the way 09-19's did. muse-spark: 3 of 21.

**Editor's own instrument slips, recorded as instances.** (1) The first quote-verify loop over 64
fragments reported 0 OK: the loop read the LAST line of `dream_corpus.py verify` output as the
status, and verify prints the status on the FIRST line (the rest is context). Every quote was
fine; the instrument was wrong. Caught because 0-of-64 was implausible and a known-present quote
failed. Re-run on first line + exit code: 64/64 OK, with a known-absent sentence returning
NOQUOTE rc=1 as the negative control. Verification pearl species 1 (the proxy status) in the
dream's own tooling. (2) The first ledger-update script placed one section's delta after a `---`
separator and thereby broke its own anchor; an assert fired before any write (`cmp` against the
pre-pass copy confirmed the ledger unchanged), and the script was re-applied with the separator
handled.

**Cursor boundary.** `dream_corpus.py` uses `timestamp >= since`. The 09-19 cursor was the
second of the last-fetched entry, so this pass's dump began with `user/2026-09-19/21-20-20-870607.md`,
which 09-19's slice-4 already contained. It was not counted as a new instance. The new cursor is
stamped at `2026-09-27T12:21:31.407`, one millisecond past the last fetched entries (both at
12:21:31.406), and before the next entries at 12:37:41.936, so nothing is skipped or re-read.

**Job A, amendments proposed (6) + culling (1)**, all in `~/vault/_inbox/dream/`, every Sources
line mechanically reverified (68/68 OK, count asserted at 7 files) and every inline body quote
checked against the corpus or the atlas:
- `pearl-earned-green-amendment-20260927.md`: what makes a stranger (author-chosen mutation,
  briefed advisor, shared upstream, isolation vs evidence). Folds the ripe "fresh context" theme.
- `pearl-verification-evidence-amendment-20260927.md`: diagnostic entry point as frozen
  production snapshot; the refactor pin that tests itself; repro matching symptom by wrong mechanism.
- `pearl-shell-amendment-20260927.md`: pgrep -x 15-char truncation; harness as third wrapper;
  `| tail -1 &&` committing a red tree; parallel calls sharing cwd; `:w`, `$=`.
- `pearl-where-the-rule-lives-amendment-20260927.md`: tripped on its ingest day; the dumb guard
  that held; invariants over procedures; prohibition in every brief.
- `pearl-prose-amendment-20260927.md`: rotted justification (closed issue behind a live default);
  illustration standing in for the population; the count theme routed in.
- `pearl-menu-amendment-20260927.md`: the pre-registration as a self-written menu ("carries
  forward to what?"); questions after a clean verdict. All Claude-authored; no
  observer-independence claim.
- `cull-alexandria-xkms-worktree-clause-20260927.md`: discharged xkms clause in the alexandria
  worktree memory (merge 78537688ca5a, worktree absent).

**Job B:** deltas appended to eleven existing sections (above, each headed "Pass 2026-09-27");
three new watching themes: "a pre-committed verdict rule must be shown able to fire" (orbweaver-rs,
8; alexandria, 1), "a diagnostic entry point is a frozen snapshot" (proposed inside the
verification amendment), "when a knob moves nothing, the knob is in the wrong stage".

**Ripe this pass:** "a fresh context is not a blind brief" (five projects) → folded into the
earned-green amendment, not drafted as a new pearl, since it is that pearl's own line. "a count is
a defect generator" (four projects) → routed to the prose amendment, per the 09-05 ledger note.
"premise-testing" (4+ projects) → routed as three shapes to the verification and prose amendments.
No new pearl drafted; none of the three passed the editor's bar for standing apart from an existing
pearl, and a new pearl would require the full-corpus hunt (arm A + arm B), which this pass did not
run. **Candidate for next pass:** "a pre-committed verdict rule must be shown able to fire". It is
one project so far, but eight instances in a week and the one alexandria row suggest it will
spread. If it does, it is the first candidate since the rule pearl that is not already a line in
an existing pearl.
