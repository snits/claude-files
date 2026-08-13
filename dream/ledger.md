# Dream-pass candidate-theme ledger

Maintained by the dream skill (Job B). Ripeness rule: instances across 3+ projects, or
5+ instances spanning 2+ months. Statuses: watching | ripe | pearled.

## verification-evidence discipline

status: pearled (pearl: "The Artifact or the Story About It", stub in
~/vault/_inbox/dream/ pending promotion — update this pointer to its atlas path when
promoted)

The founding theme, hunted full-corpus in the zhqp spike (2026-08-11). Instance base:
~550-entry candidate pool, arm artifacts in ~/devel/mnemosyne/.scratchpad/zhqp-spike/.
New instances since the spike get appended here by Job A passes.

Pass 2026-08-13 (window 08-11..08-13): 30+ candidate instances in two days — theme
remains highly active. Four additions proposed in
`~/vault/_inbox/dream/pearl-verification-evidence-amendment-20260813.md`:
- production-fixture sub-species + census countermeasure (rhkmaint-tools,
  user/2026-08-12/22-06-47-546240.md, user/2026-08-13/06-12-55-184296.md)
- grammar-of-a-finding, 19-day unrendered claim (alexandria,
  project/2026-08-12/14-15-13-397501.md)
- exit-code-as-verdict near-miss (claudes-home, user/2026-08-13/12-49-23-627279.md)
- "what state does the check depend on that is not part of the claim" (rhkmaint-tools,
  project/2026-08-12/19-25-21-367373.md)

## compound-shell-commands are their own failure domain

status: ripe (3+ projects in one window; full-corpus hunt deferred to next pass —
editor's call, this pass was the wiring verification)

The shell decoration around a command becomes part of the instrument and corrupts the
measurement: trailing `; echo EXIT=$?` making a 4-failure run report 0 (rhkmaint-tools,
project/2026-08-11/00-43-03-411456.md); a zsh glob error in `cmd; echo ==X==; cmd`
silently aborting the whole line so "spot-checks pass" described a sed that never ran
(claudes-home, user/2026-08-11/15-14-45-749424.md); unconditional `&& echo "(status)"`
as a lie generator (vault, user/2026-08-11/17-26-12-971085.md); cwd persistence across
tool calls striking three times in one project (rhkmaint-tools, 8/12 sessions).
Distinct from the pearl's proxy-status species: this is the *instrument assembly*
failing, not the status being a proxy.

## worktree/environment artifact borrowing

status: watching (2 projects: rhkmaint-tools, alexandria)

Fresh worktrees silently borrow the main checkout's state — built binaries present in
both trees masking a dependency (rhkmaint-tools cnck,
project/2026-08-12/19-25-21-367373.md); `uv run pytest` falling through to an editable
install of main's src (alexandria am5v, project/2026-08-12/21-45-23-695470.md).
Overlaps the new pearl move ("state the check depends on that is not part of the
claim"); may belong there rather than as its own pearl.

## review-cycle convergence: finding identity over finding count

status: watching (2 projects: rhkmaint-tools, alexandria)

Iterated review converges when each cycle returns *different* findings with falling
severity; identical findings across cycles = stalled loop, escalate
(rhkmaint-tools f350, user/2026-08-12/22-06-47-546240.md; alexandria 4sqj/30yv
sessions, 8/12–8/13). Already partially codified in the super-do review cap.

## how Jerry steers: terse mid-turn course-corrections

status: watching (cross-project; needs more than two days of instances)

Terse redirects mid-turn are premise-challenges, not detail requests; one-word
confirmations expect momentum; acts-then-mentions phrased as questions ("merged", "I
thought…"). Readers surfaced this across rhkmaint-tools, kriegspiel, vault, alexandria
in this window alone (e.g. user/2026-08-11/14-46-50-924429.md). The "observations about
how Jerry functions" goal from zhqp's framing points here.

## issue bodies go stale faster than their comments

status: watching (already partially canonized — CLAUDE.md "Amending a stale body";
tracking whether the *pearl-shaped* story exceeds the rule)

The body is the first thing read and the stalest artifact on long-lived issues; the
19-day p20 claim and the f16t "awaiting ruling" misread are this window's instances
(alexandria, project/2026-08-12/14-15-13-397501.md; alexandria session close,
user/2026-08-13/12-51 entry).
