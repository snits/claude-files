---
name: maintain-assess
description: loop for assessing the maintainability of a codebase
---

Analyze the codebase through the lens of long-term evolution, keeping in mind the scope of the
project. Assess:

- **Change impact** — where a modification forces edits in more places than it should, and where a
  failure would be hard to debug because the code does not say what it assumed.
- **Technical debt** — design shortcuts, duplication, and complexity that has accumulated past
  what the problem warrants.
- **Knowledge dependencies** — behavior that is only correct because of something undocumented,
  where the next reader has to reconstruct the reasoning to change it safely.

For anything found, create a kata issue using `kata create` if an issue does not already exist for
it. Read the open issues first so you file additions, not duplicates.

Title issues with a `maintain:` prefix so the pass that found them stays identifiable later.

Assess the project in front of you, not a larger one. Extensibility mechanisms, plugin
architecture, configuration surfaces, and API-evolution strategy are maintainability concerns for
software that has external consumers and a compatibility promise; on a single-maintainer tool they
are the over-engineering this pass should be flagging, not recommending. A finding has to name a
change that is actually likely, not one that is merely conceivable.

If nothing is found, say "No maintainability issues found in this project"
