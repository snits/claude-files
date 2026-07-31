---
name: document-assess
description: loop for assessing status of documentation in a project
---

Analyze the project's documentation for completeness and correctness, keeping in mind the scope of
the project. For any issue found, create a kata issue using `kata create` if an issue does not
already exist for it. Read the open issues first so you file additions, not duplicates.

Title issues with a `docs:` prefix so the pass that found them stays identifiable later.

Correctness before completeness: documentation that describes behavior the code no longer has is
worse than documentation that is missing, because it is trusted. Prefer filing a doc that contradicts
the code over a doc that does not exist yet.

If nothing is found, say "Documentation is up to date in this project"
