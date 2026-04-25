---
name: evidence-and-claims
description: Use when performing investigative work that produces reports or analysis for others to verify — root cause analysis, bug investigation, crash analysis, sosreport analysis, or any task making factual claims about system behavior. Also triggered by "investigate", "root cause", "analyze", "RCA", "figure out why", "what's causing", "track down", "write a report", "write up findings", "document what you found". Do NOT activate for quick lookups, code reviews, implementation tasks, or design work.
---

# Evidence and Claims

All factual claims in investigation reports must be backed by recorded evidence. No assertions from memory. No "it appears that." No unsourced conclusions.

## The Rule

**Every factual claim in an investigation report must trace back to a recorded evidence entry. If it's not in the ledger, it's not in the report.**

This applies to:

- Where code lives and what it does (structural claims)
- Why something happened and what caused it (causal claims)
- Prior art, known patterns, and external references (contextual claims)
- Whether a bug reproduces and under what conditions (reproducer claims)

If a claim appears in the report, a ledger entry supports it. If a conclusion connects multiple findings, each finding is independently evidenced and the reasoning chain is explicit.

## Claim Taxonomy

Claims are tiered by type. The tier determines what evidence is required and how the claim is cited.

| Tier | Type | Example | Required Evidence | Risk if Wrong |
|------|------|---------|-------------------|---------------|
| 1 | **Structural** — where, what, which version | "iommu_map() is defined in drivers/iommu/iommu.c:1847" | Command output or file read with path, line, tree, commit | Wastes reviewer's time on dead trail |
| 2 | **Causal** — why, what caused what | "The crash occurs because iommu_map() receives a NULL domain pointer after device detach" | Evidence chain — multiple entries linked with explicit reasoning | Sends entire investigation wrong direction |
| 3 | **Contextual** — prior art, external refs | "Same root cause as upstream commit 3f6d810" | External reference (URL, ticket, commit hash) with verification context | Misattributes root cause, incorrect backport decisions |
| 4 | **Reproducer** — does it trigger, under what conditions | "Bug reproduces within 30s on 2-socket EPYC under 98% fill" | Bundle: script, environment, config, output, exit status | Chases unreproducible conditions |

## The Evidence Ledger

Maintain an `evidence-log.md` (or `evidence-log-<ID>.md` when an investigation identifier exists) as a structured scratch file during investigation. This is the single source of truth. The report cites ledger entries; it does not contain raw evidence inline.

### Where the Ledger Lives

- Investigation has a dedicated directory (e.g., `investigations/RHEL-12345/`): ledger goes there
- Working in the current directory: ledger goes in the current directory
- Multiple investigations in the same directory: use `evidence-log-<ID>.md` to avoid collisions
- Investigation spans multiple repos: ledger lives in the primary working directory; entries note which repo/tree each piece of evidence came from

### Standard Entry Format

```
### E1 — [structural] iommu_map function location
- **Claim:** iommu_map() is defined in drivers/iommu/iommu.c
- **Environment:** c10s kernel tree, commit abc123def, 2026-04-20
- **Command:** `grep -rn "^int iommu_map(" drivers/iommu/`
- **Output:**
  ```
  drivers/iommu/iommu.c:1847:int iommu_map(struct iommu_domain *domain,
  ```
- **Status:** confirmed
```

### Required Fields

| Field | Required | Purpose |
|-------|----------|---------|
| ID | yes | Sequential (E1, E2...), referenced in report citations |
| Claim type | yes | structural / causal / contextual / reproducer |
| Short title | yes | Scannable summary of what this evidence supports |
| Claim | yes | The factual statement this evidence supports |
| Environment | yes | Tree, commit, kernel version, host — enough to reproduce |
| Command / Source | yes | Exact command run, file path read, or URL visited |
| Output | yes | Raw output, trimmed if long with truncation note |
| Status | yes | confirmed / refuted / inconclusive / dead-end |
| Notes | no | Interpretation, why it matters, links to other entries |

### Reproducer Entry Format

Reproducer entries require additional fields:

```
### E14 — [reproducer] crash triggered on 2-socket EPYC
- **Claim:** Bug reproduces within 30s under memory pressure on 2-socket EPYC
- **Environment:** RHEL 10.0, kernel 6.12.0-55.el10.x86_64, 2-socket EPYC 7763, 512GB RAM
- **Script:** `./numa_pressure --target-free-mb=2048 --fill-percent=98`
- **Config:** Default kernel config, IOMMU enabled, SELinux enforcing
- **Output:**
  ```
  [  32.451] BUG: kernel NULL pointer dereference at 0000000000000028
  [  32.451] RIP: 0010:iommu_map+0x1a/0x350
  ```
- **Exit status:** 139 (SIGSEGV — kernel panic triggered)
- **Status:** confirmed
- **Notes:** Does NOT reproduce with IOMMU disabled (see E15)
```

### Ledger Rules

1. **Append-only during investigation.** Never delete or modify entries. If earlier finding is wrong, add a new entry that refutes it and update the old entry's status to `refuted`.
2. **Record before concluding.** The supporting evidence must be in the ledger before you write the finding.
3. **Dead ends get logged.** Mark them `dead-end` with a note about why abandoned. This answers "did they consider X?" for reviewers.
4. **Truncation rules.** Output exceeding ~30 lines: include the relevant portion and note "full output: N lines, showing lines M-P." Very large outputs: reference a separate file.
5. **Environment is mandatory.** Every entry specifies enough context to reproduce the lookup on a different machine. At minimum: repo/tree, commit or tag, date.

## Report Citation Protocol

The report draws from the ledger using a hybrid citation style.

### Inline Citations (structural claims)

```
The function `iommu_map()` is defined in `drivers/iommu/iommu.c:1847` [E1].
```

### Evidence Chain Citations (causal claims)

```
The crash occurs because `iommu_map()` receives a NULL domain pointer
after device detach. The call trace shows the fault at `iommu_map+0x1a`
[E3], which dereferences `domain->ops` [E5]. The device detach path
sets `domain` to NULL without holding the group mutex [E8], creating
a window where a concurrent DMA map can see the NULL [E8→E10].
```

The reasoning connecting evidence is part of the claim. Listing evidence IDs alone is not sufficient.

### External Reference Citations (contextual claims)

```
This is the same root cause as upstream commit 3f6d810 ("iommu: Hold
group mutex across detach/map") [E12], which was merged in v6.14-rc3
but has not been backported to the c10s tree as of 2026-04-20 [E13].
```

### Reproducer Citations

```
The bug reproduces within 30 seconds on a 2-socket EPYC 7763 with
512GB RAM under 98% memory fill [E14], but does NOT reproduce with
IOMMU disabled [E15], confirming the fault is in the IOMMU path.
```

### Unsupported Claims

If during report writing a claim has no ledger entry:
1. Stop writing the report.
2. Go gather the evidence — run the command, read the file, find the reference.
3. Add the ledger entry.
4. Then write the claim with its citation.

Never write "it is believed that..." or "it appears that..." as a workaround for missing evidence.

### Report Footer Convention

Every investigation report ends with:

```
## Evidence Log
See `evidence-log.md` for the complete evidence ledger supporting
this report. Key entries: E1, E3, E5, E8, E10, E12-E15.

Dead ends investigated: E6 (scheduler theory — ruled out),
E9 (memory corruption — ruled out).
```

## Process Discipline

Evidence is captured at discovery time, not reconstructed during report writing.

### The Investigation Loop

```
1. Form a question or hypothesis
2. Run a command / read a file / check a reference
3. Record the result in the evidence ledger (even if dead end)
4. THEN form your next question based on what you found
```

Step 3 is not optional and cannot be deferred.

### When to Create a Ledger Entry

| Situation | Action |
|-----------|--------|
| Command output informs your investigation | Log immediately |
| File read reveals something relevant | Log path, line range, commit |
| External reference found (commit, CVE, mail thread) | Log URL/ID and what it says |
| Reproducer executed | Log script, environment, output, exit status |
| Lead followed that went nowhere | Log as dead-end with why you abandoned it |
| Conclusion drawn from multiple entries | Log a causal entry linking the chain |
| Computation performed (calculations-and-math) | Both skills apply — compute AND log |

### When NOT to Create a Ledger Entry

- Exploratory commands for orientation (e.g., `ls` to find your way around)
- Re-running a command already logged (reference the existing entry)
- Reading documentation to understand a concept (unless citing it as a contextual reference)

## Interaction With Other Skills

### calculations-and-math

Complementary, not overlapping:
- **calculations-and-math** says: "Compute it with a tool, show the computation"
- **evidence-and-claims** says: "Log the computation as evidence, cite it in the report"

When both apply, compute per calculations-and-math rules AND log the result as a ledger entry.

### verification-before-completion

verification-before-completion governs the completion gate ("did you verify your claims?"). evidence-and-claims provides the mechanism for how claims are verified and recorded during the investigation.

### systematic-debugging

systematic-debugging governs how to find root causes (hypothesis formation, pattern analysis). evidence-and-claims governs how to record what you found so others can verify your work.

## Rationalization Prevention

| Thought | Reality |
|---------|---------|
| "I'll log this later" | You won't. Context gets compacted. Log now. |
| "This is obviously true, no citation needed" | Obvious to whom? The cross-team reader doesn't share your context. |
| "I already logged something similar" | Similar isn't the same. Different claim, different evidence entry. |
| "The output was too long to log" | Truncate with a note. Some evidence is better than none. |
| "I remember seeing this earlier" | Memory is not evidence. Re-run the command, log the result. |
| "This is just background context" | If it's in the report, it needs a source. If not, it doesn't belong in the report. |
| "The dead end isn't worth logging" | Dead ends answer "did you consider X?" — valuable for reviewers. |
| "I can reconstruct this from the conversation" | Conversations get compacted. The ledger doesn't. |
| "It's a well-known fact in the kernel community" | Link to the documentation, commit, or mail thread. Well-known to you is not well-known to everyone. |
| "I'll add citations during the writeup phase" | That requires re-running commands — the exact waste this skill prevents. |

## Edge Cases

- **Trivial common knowledge** (e.g., "Linux is written in C"): Does not need a citation. But "the IOMMU subsystem uses a two-level page table" does — specific enough to be wrong.
- **Claims from prior investigations:** Cite the prior report as a contextual reference. Do not claim its conclusions as your own evidence.
- **Agent-to-agent handoff:** Reference the first agent's ledger entries (e.g., "per investigation-1/evidence-log.md E7") rather than re-logging the same evidence.

## When Delegating to Subagents

When spawning subagents for investigation work, include this directive:

> **Evidence rule:** Maintain an `evidence-log.md` file. Every factual claim you discover must be logged with: an ID (E1, E2...), claim type (structural/causal/contextual/reproducer), the command or source, the output, and environment context (tree, commit, date). Log dead ends too. Never defer logging — do it immediately after each discovery. When writing findings, every claim must cite a ledger entry.
