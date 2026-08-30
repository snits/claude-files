---
name: verify-claims
description: Re-verify every factual claim in the pending issue/doc/commit before it lands.
---

For the artifact I am about to file or commit:

1. Extract every factual claim into a numbered list. Categorize each as:
   CODE_CITATION (file:line), COMMAND_RESULT, or INFERENCE.
2. For each CODE_CITATION: Read the exact lines. If they do not say what the claim says, mark WRONG.
3. For each COMMAND_RESULT: re-run the command and paste real output. Never trust memory of an earlier run.
4. For each INFERENCE (e.g. "cleanup ran", "nothing does X", "nothing was pushed"):
   either promote it to a COMMAND_RESULT by running the proving command, or delete it.
5. Print a table: claim | category | verdict | evidence.
6. Refuse to file/commit until every row is VERIFIED or removed.
