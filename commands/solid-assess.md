---
name: solid-assess
description: loop for performing SOLID principles assessment of project
---

Analyze the codebase through the lens of SOLID principles, keeping in mind the scope of the
project. For any violation found, create a kata issue using `kata create` if an issue does not
already exist for it. Read the open issues first so you file additions, not duplicates.

Title issues with a `solid:` prefix so the pass that found them stays identifiable later.

Scope matters more for this lens than the others. Several SOLID principles presuppose type
hierarchies and polymorphism; in a codebase that has none, they have nothing to say, and reaching
for a finding anyway produces a recommendation to add abstraction the project does not need.
Finding nothing is a valid outcome here — report it rather than lowering the bar to justify the
run.

If nothing is found, say "No SOLID violations found in this project"
