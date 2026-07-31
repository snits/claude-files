---
name: dead-code
description: loop for finding dead code, stale comments, and stale documentation in a project
---

Analyze the codebase for dead code, stale comments, and stale documentation, keeping in mind the
scope of the project. For anything found, create a kata issue using `kata create` if an issue does
not already exist for it. Read the open issues first so you file additions, not duplicates.

Title issues with a `dead-code:` prefix so the pass that found them stays identifiable later.

This loop finds and reports. It does not delete, and it does not implement — `work-issue` is the
only loop that changes code. That separation is what keeps a deletion from reaching the repo
without passing your triage.

**Deadness is a claim that needs evidence, not a reading impression.** Before filing, show the
check that establishes it: the grep that finds no callers, the coverage run that never enters the
branch, the build that still passes with the symbol removed. Say which check you ran in the issue
body. Things that look dead and are not: exported API used by other projects, code behind build
tags or platform guards, test-only helpers, symbols reached by reflection or interface
satisfaction, and functions whose only caller is generated or conditionally compiled. If you cannot
produce evidence, file it as a question rather than as a finding, and say what would settle it.

A stale comment or doc claim is the same kind of assertion: quote the line and cite what the code
actually does now, so the issue can be verified without re-deriving your reasoning.

If nothing is found, say "No dead code, or stale documentation in this project"
