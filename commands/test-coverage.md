---
name: test-coverage
description: loop for finding test coverage gaps and weak tests in a project
---

Analyze the codebase for test problems, keeping in mind the scope of the project:

- Gaps in coverage, including missing edge cases and untested error paths.
- Tests that pass without asserting anything meaningful.
- Bugs in current tests.

If tooling exists for measuring coverage, and mutation testing in the
environment, utilize it. If the tooling exists for the environment,
but it isn't installed, request that it be installed.

For anything found, create a kata issue using `kata create` if an issue does not already exist for
it. Read the open issues first so you file additions, not duplicates.

Title issues with a `test-coverage:` prefix so the pass that found them stays identifiable later.

This loop finds and reports. It does not write tests and it does not implement — `work-issue` is
the only loop that changes code. That separation matters more here than anywhere else: a loop that
both judges test quality and writes the tests is grading its own work.

**Establish a gap by mutation, not by reading.** A branch that looks untested may be covered
incidentally, and a test that looks thorough may assert nothing. Break the thing under test —
delete the branch, invert the condition, remove the anchor — run the suite, and report what stayed
green. That output is the evidence; put it in the issue body. A gap you inferred from reading
coverage output is a hypothesis, so say so and say what you tried.

Watch specifically for tests that would survive deletion of the code they name, and for tests that
pass on empty or absent input, where substituting the zero case by hand leaves the assertion
intact. Those read as coverage and are not.

**Before accepting any artifact as evidence, ask: could this artifact look exactly like this if
my claim were false?** If yes, it is not evidence for the claim — find one that could not. See
the Verification section of the global CLAUDE.md for the corollaries; the one that bites hardest
here is that an artifact shared across runs cannot answer a per-run question, which is how a
suite aliasing built output back to source stays green against a stale build.

If nothing is found, say "test coverage is up to date in this project"
