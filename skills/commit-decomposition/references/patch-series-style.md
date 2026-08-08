# Distilled Heuristics: How to Split a Large Change into a Patch Series

Source material: two Jason Gunthorpe-authored kernel patch series, both for the
"iommufd" subsystem (a Linux kernel facility that lets userspace programs safely
control hardware memory-translation tables). No kernel background is assumed below —
every kernel-specific term is translated inline. Read "patch" as "commit" throughout.

Series studied:
1. **"IOMMUFD Generic interface" v3** (15 patches + cover letter), Jason Gunthorpe,
   Oct 2022 — introduces a brand-new subsystem from scratch.
   https://lore.kernel.org/bpf/0-v3-402a7d6459de+24b-iommufd_jgg@nvidia.com/
   (readable via https://lkml.kernel.org/kvm/15-v3-402a7d6459de+24b-iommufd_jgg@nvidia.com/T/ —
   lore.kernel.org itself blocked automated fetches with an anti-bot wall)
2. **"Add iommufd physical device operations for replace and alloc hwpt" v3**
   (17 patches), Jason Gunthorpe, Mar 2023 — adds a substantial new capability
   (live-swapping a device's translation table without detaching it first) to
   the already-merged subsystem from series 1.
   https://lkml.kernel.org/kvm/ZBxioEDUtPMro+ew@nvidia.com/
3. Supporting comparison only, **not Gunthorpe's work** (flagging this because the
   dispatch brief suggested it as a Gunthorpe candidate and it isn't): Robin Murphy's
   "iommu: The early demise of bus ops" v2 (8 patches) — a mechanical-conversion-heavy
   series used below only to illustrate the "mechanical vs. behavioral" heuristic,
   attributed correctly.
   https://lkml.rescloud.iu.edu/2301.3/03721.html
4. Also checked and correctly ruled out as **not Gunthorpe's**: "iommu: Refactoring
   domain allocation interface" is authored by Lu Baolu, not Gunthorpe. Excluded from
   the study.

---

## 1. Preparatory refactors land before the new capability

**Rule:** Before adding the thing you actually want, land the patches that make room
for it — renames, new-but-unused helper functions, data-structure additions with no
behavior change yet — as their own patches, ordered first.

Landing the groundwork separately means a reviewer approves "this rename is safe" and
"this data structure is correct" as isolated, low-stakes claims, before ever having to
also judge whether the new behavior built on top of them is correct. If the new
behavior turns out to be wrong, the groundwork patches usually still stand and don't
need to be re-litigated.

Example: in the 17-patch "replace and alloc hwpt" series, patches 2–8 (`iommufd: Add
iommufd_group`, `iommufd: Replace the hwpt->devices list with iommufd_group`, `iommu:
Export iommu_get_resv_regions()`, `iommufd: Keep track of each device's reserved
regions instead of groups`, `iommufd: Use the iommufd_group to avoid duplicate MSI
setup`, `iommufd: Make sw_msi_start a group global`, `iommufd: Move putting a hwpt to
a helper function`) all restructure existing internal bookkeeping with no visible
behavior change, before patch 12 (`iommufd: Add iommufd_device_replace()`) introduces
the actual new capability the series is named for.

---

## 2. One concept per patch — a patch does exactly one thing a reviewer can approve or reject as a unit

**Rule:** If describing a patch in one sentence requires the word "and" joining two
unrelated ideas, split it. Each patch should correspond to one decision a reviewer
could accept or veto independently of the others.

This is the load-bearing rule underneath most of the others. A patch that both renames
a function *and* changes what it does forces a reviewer to accept or reject the rename
and the behavior change together — if they disagree with the behavior change, they
can't cleanly say so without also relitigating the rename. Splitting lets `git bisect`
and code review both point at exactly one cause when something breaks.

Example: `iommufd: Move putting a hwpt to a helper function` (patch 8/17) does
precisely one thing — extract a repeated code sequence into a named helper — and does
not change what that sequence does. It is followed, several patches later, by the
actual feature patches that call the new helper differently.

---

## 3. Every patch must leave the tree in a buildable, working state

**Rule:** After each individual patch is applied — not just after the whole series —
the code must compile and any tests that passed before must still pass. Never split a
change such that patch N introduces a caller of something patch N+1 defines.

This is what makes `git bisect` (binary-searching commit history to find which commit
introduced a bug) actually work, and what lets a reviewer or CI system check out any
single patch in the middle of the series and evaluate it on its own. A series that
only builds at the *end* is really one giant patch with checkpoints, not a series.

Example: in the "IOMMUFD Generic interface" series, patch 03/15 (`interval-tree: Add a
utility to iterate over spans in an interval tree`) adds a general-purpose data
structure utility with its own tests, fully working and unused by iommufd yet; only
later patches (07–09/15, the PFN storage and mapping patches) begin consuming it. The
utility patch stands on its own and doesn't reference anything not yet defined.

---

## 4. Separate mechanical, tool-checkable changes from changes that require human judgment

**Rule:** When a change has both a "convert every call site to a new pattern"
component and a "here's why the new pattern is better/necessary" component, split
them into a preparatory patch (the reasoning) and a follow-on mechanical patch (the
find-and-replace across all call sites) — or vice versa, reasoning-then-conversion.
Never interleave the two inside one patch.

A mechanical, repetitive change (the same transformation applied at every call site)
can be verified almost automatically — the reviewer scans for "did every site get
converted the same way, or did one get missed / done differently." A judgment change
(should we do this at all, does the new design handle an edge case correctly) needs
close reading. Mixing them means every mechanical hunk drags a reviewer back into
close-reading mode, which is slow and error-prone at scale, and it means one subtly
wrong conversion is easy to miss inside a wall of repetitive diff.

Example (Robin Murphy's bus-ops series, used here for illustration only — not
Gunthorpe's work, cited correctly above): `iommu: Factor out some helpers` extracts
shared logic as groundwork, and only in the later `iommu: Retire bus ops` patch is the
old registration mechanism actually removed — the removal patch is a comparatively
mechanical deletion once every caller has already been converted to the new mechanism
by the preceding patches.

---

## 5. The cover letter tells a story with a beginning, a problem, and a plan — not a table of contents

**Rule:** The patch 0 / cover letter should read as connected prose: what's broken or
missing today, why previous attempts weren't sufficient, what design was chosen and
why, and what's deliberately left out of scope (with a pointer to where that will be
addressed). It should let a reviewer decide whether to invest time in the series
*before* opening a single diff.

A bare list of patch titles ("adds struct X, adds ioctl Y, adds selftest") tells the
reviewer nothing about whether the design is right — only that things were added. The
narrative is where the author justifies the *shape* of the whole series, including why
it's split the way it is (which patches are foundational vs. incidental, what's
deferred to a follow-up series). This lets a reviewer triage: read the narrative,
decide whether the overall direction is sound, and only then descend into per-patch
review.

Verbatim example, from the cover letter of "IOMMUFD Generic interface" v3 (patch
00/15): *"The pre-v1 series proposed re-using the VFIO type 1 data structure, however
it was suggested that if we are doing this big update then we should also come with an
improved data structure that solves the limitations that VFIO type1 has."* — this one
sentence tells the reviewer the prior design was rejected, why, and what alternative
was chosen, before the reviewer looks at any code. The same cover letter states the
project's scope explicitly: *"iommufd intends to be general and consumable by any
driver that wants to DMA to userspace."*

---

## 6. A large mechanical sweep is kept reviewable by isolating the pattern once, then repeating it identically everywhere

**Rule:** When the same transformation must be applied across many call sites, do it
in two moves: (a) one patch establishes the *pattern* — the new helper, the new
calling convention, applied and proven at one or a small representative set of sites —
and (b) a separate patch (or small number of patches, grouped by natural boundary such
as "one per subsystem" or "one per driver") applies the now-proven pattern everywhere
else with no further design decisions being made. The second kind of patch should
contain no judgment calls at all — if a reviewer has to stop and think at any site
during the sweep, that site had a hidden special case and belongs in its own patch,
pulled out of the sweep.

This keeps a reviewer's job during the sweep patches down to "does every conversion
here look like the ones I already approved in the pattern-establishing patch" — a
skim-and-diff check — rather than re-deriving correctness at every site. It also means
that if one site really was special, it doesn't get silently swept into "looks the
same as the rest" and missed.

Example: the "replace and alloc hwpt" series separates `iommu: Introduce a new
iommu_group_replace_domain() API` (patch 11/17, which defines the new operation and
its contract) from `iommufd: Add iommufd_device_replace()` (patch 12/17, which is the
first real consumer) and `iommufd/selftest: Test iommufd_device_replace()` (patch
14/17, which exercises it) — the capability, its first use, and its test are three
separate, individually reviewable steps rather than one patch that defines-and-uses-
and-tests the new operation simultaneously.

---

## 7. Tests for new behavior are their own patch, placed immediately after the behavior they test

**Rule:** When a patch adds new externally-observable behavior, add its test in the
next patch, not folded into the same one, and not deferred to the end of the series.

Splitting them means a reviewer can look at the behavior patch and ask "is this
correct" independently of "is this well-tested," and can look at the test patch and
confirm it actually exercises the new code path (a test folded into the same patch as
the feature is much easier to accidentally make trivially-passing, e.g. testing the
mock rather than the real path). Placing the test patch immediately after — not
batched with other tests at the series' end — keeps the causal link between a specific
capability and its verification visible in the history.

Example: `iommufd: Add IOMMU_HWPT_ALLOC` (patch 15/17) is directly followed by
`iommufd/selftest: Return the real idev id from selftest mock_domain` (patch 16/17,
adjusting test infrastructure to support it) and `iommufd/selftest: Add a selftest for
IOMMU_HWPT_ALLOC` (patch 17/17) — the feature and its dedicated test sit at the very
end of the series, adjacent to each other, not interleaved with unrelated patches.

---

## 8. Order patches so each one only depends on patches already applied earlier in the same series — never forward

**Rule:** A patch may only use structures, functions, or behavior introduced by an
earlier patch in the same series, never a later one. If patch B needs something from
patch A, A must come first; if two patches are mutually necessary, they were split
wrong and should be merged into one.

This is a direct consequence of rule 3 (buildable at every step) but is worth stating
as its own check because it's the concrete test you run against a proposed patch
order: for every patch, can you point to which earlier patch supplies everything it
references? If not, either reorder or re-split.

Example: across both series studied, foundational data-structure and infrastructure
patches (e.g. `interval-tree: Add a utility to iterate over spans in an interval
tree`, patch 03/15) consistently precede the patches that consume them (the PFN
storage and mapping patches, 07–09/15) — never the reverse.

---

## 9. What's deliberately out of scope gets named, not silently omitted

**Rule:** If an obvious next step or related capability is *not* included in this
series, say so explicitly in the cover letter (or the relevant patch's commit
message), along with why — future work, needs more discussion, blocked on something
else. Don't let a reviewer wonder whether an omission was an oversight.

This prevents review time being spent asking "why doesn't this handle case X" when the
author already knew and made a deliberate call — the answer should already be on the
page. It also documents, for whoever picks up the follow-on work later, exactly what
was deferred and why, instead of that reasoning existing only in the original author's
head.

Example: the "IOMMUFD Generic interface" cover letter explicitly lists the
capabilities the new subsystem is *designed to eventually support but does not yet
implement* — PASID/SSID binding, userspace page tables, dirty-page tracking, and
others — framing them as intentional future extensions of the architecture rather than
gaps discovered by the reviewer.

---

## Applying this to a non-kernel diff

None of the above is kernel-specific. Translated to an arbitrary large diff (e.g. a
big refactor or feature PR in application code):

- Split "make room for the change" (renames, new-but-unused helpers, data-structure
  changes with no behavior change) into their own commits, first.
- Each commit should be describable in one sentence with no "and."
- Every commit, checked out on its own, must build and pass existing tests.
- If you're both changing a pattern *and* applying it everywhere, that's two commits:
  establish-and-prove-the-pattern, then mechanically-apply-everywhere with no further
  judgment calls.
- New behavior gets its dedicated test in the very next commit.
- No commit may reference something a later commit introduces.
- The PR/series description is prose — problem, prior attempts and why they fell
  short, the chosen design, what's deliberately deferred — not a bullet list of commit
  titles.
- Deliberately-omitted scope gets a sentence explaining why, not silence.
