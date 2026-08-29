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
Amendment proposed in `~/vault/_inbox/dream/pearl-verification-evidence-amendment-20260829.md`:
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

## prose about a system is not under test

status: pearled (draft: `~/vault/_inbox/dream/pearl-prose-is-not-under-test.md`,
pending promotion). Merges two prior threads: the "issue bodies go stale faster than
their comments" theme below (now closed into this) and the window's dominant new
pattern, "doc/prose claims are untested assertions."

Two mechanisms, one object: a declarative sentence about code is (1) untested at birth —
written from a mental model, with no red-green reflex ("Every error was a universal
quantifier I had not earned", user/2026-08-19/15-57-16-537213.md) — and (2) never re-run
as the tree moves (stale bodies, handoffs, titles, close messages, help text, docstrings).
Corpus span: 2025-08-19 (patch 0039 commit claiming absent fixes) → 2026-08-28; projects:
rhkmaint-tools, alexandria, vault, projstat, mnemosyne, claudes-home, orbweaver-rs.

## compound-shell-commands are their own failure domain

status: ripe (full-corpus hunt now deferred TWICE — 08-13 pass was wiring verification,
08-29 pass spent its pearl slot on prose-is-not-under-test. Next pass should either
draft it or demote it with a stated reason.)

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

## worktree/environment artifact borrowing

status: watching (still mostly rhkmaint-tools + alexandria; the conceptual core was
folded into the pearl's "state outside the claim" move at the 08-13 amendment)

New: editable-install `.pth` pointing worktree imports at main's src
(project/2026-08-18/14-40-30-544612.md, project/2026-08-19/16-53-19-491144.md — a
false refutation of a real bug); gitignored artifacts silently downgrading
verifications in fresh worktrees (project/2026-08-16/21-07-29-160947.md); three entry
points with three truth values (project/2026-08-21/19-08-07-027655.md); stale shared
`mutants/` tree as evidence (project/2026-08-18/20-24-33-693397.md).

## review-cycle convergence: finding identity over finding count

status: watching (rhkmaint-tools dominant; alexandria earlier)

New: convergence read from severity/category derivative, not count
(project/2026-08-18/15-25-01-356800.md, project/2026-08-27/21-57-40-007887.md — four
rounds, every blocking finding a false prose claim); opposite-direction findings in the
same area = a missing decision, escalate (project/2026-08-18/16-22-01-131609.md);
disjoint finding sets across independent reviewers as the argument FOR plurality
(project/2026-08-27/19-39-11-603139.md, user/2026-08-27/17-04-19-711616.md); fix-for-
finding-N creates finding-N+1 in invariant-dense code (project/2026-08-19/16-53-19-491144.md).

## how Jerry steers: terse mid-turn course-corrections

status: ripe (3+ projects across 3 windows: rhkmaint-tools, alexandria, claudes-home,
vault, kriegspiel; pearl drafting deferred — one pearl per pass, editor's call. This is
the "observations about how Jerry functions" thread from zhqp's framing and deserves
its own hunt with different arms — his messages, not agent reflections, are the raw
material.)

New instance families this window:
- mechanism-questions that dissolve symptom-treatment ("what is the process doing that
  requires more vram?", project/2026-08-16/16-51-24-408889.md; "What is sorting
  something by hash order?", project/2026-08-20/16-27-30-289344.md — four artifacts had
  agreed and none checked the premise)
- disjunctions containing the answer (project/2026-08-18/16-06-41-042314.md)
- incredulity as data ("wait the docling code is running tesseract??",
  user/2026-08-15/19-24-54-652294.md)
- pushback on ceremony, not caution ("I'm not sure it is a blocker",
  project/2026-08-15/22-53-56-201184.md); rejection of manufactured needs-decision
  balance ("why not just fix the dependency?", project/2026-08-21/20-02-58-885850.md)
- re-litigation shutdown ("That was the ruling that was already made before",
  project/2026-08-28/23-26-52-040846.md); directive-in-second-clause misread as
  consolation (project/2026-08-29/01-57-09-722849.md)
- hedge words as delegation ("perhaps" = the decision is yours,
  project/2026-08-19/11-01-25-719191.md)

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

## silent no-op configuration

status: watching (alexandria + claudes-home)

A flag/env/param that looks active, errors never, does nothing: four in one session
(user/2026-08-14/18-54-10-189246.md); llama-swap serving a stale config for two days on
a YAML indent error (project/2026-08-16/09-15-45-290027.md). Related to species 2 but
about configuration surface, not tests.

## subagent report delivery is unreliable; the filesystem is the deliverable

status: watching (rhkmaint-tools, projstat, claudes-home; already partially canonized
in memory `reference_subagent_report_relay_drop.md` — tracking whether the pearl-shaped
story exceeds the memory)

7+ sightings this window converging on a recipe: named absolute path, Write as last
action, probe path before dispatch, bounded monitor. "The message channel is
best-effort; the filesystem is not" (project/2026-08-18/22-45-52-125713.md); "A
background agent's dropped report is indistinguishable from a clean review"
(project/2026-08-15/15-49-11-856408.md).

## merge/rebase silently corrupts derived artifacts

status: watching (rhkmaint-tools only, 3 sightings)

Clean auto-merges as signal-free failures: stale line-number citation surviving a
rebase (project/2026-08-27/17-04-19-711616.md); duplicated selectinload invisible in
Python, compile error in Rust (project/2026-08-27/19-21-32-689210.md); goldens stale
per hunk, not per file (project/2026-08-27/21-57-40-007887.md). Countermeasure already
formulated in-corpus: "for derived artifacts the merge resolution is re-derive from the
merged source."
