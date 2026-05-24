#!/usr/bin/env bash
# gen-index.sh — render vault index.md from final-* artifacts.
#
# Usage:
#   gen-index.sh <vault-entry-dir> <slug> <attempt-count>
#
# Reads <vault-entry-dir>/{brief.md, final-machine-artifact.json, final-verdict.json}.
# Writes index.md to stdout.
set -euo pipefail

DIR="$1"
SLUG="$2"
ATTEMPTS="$3"

BRIEF="$DIR/brief.md"
ARTIFACT="$DIR/final-machine-artifact.json"
VERDICT="$DIR/final-verdict.json"

for f in "$BRIEF" "$ARTIFACT" "$VERDICT"; do
    [ -r "$f" ] || { echo "gen-index.sh: cannot read $f" >&2; exit 2; }
done

python3 <<PYEOF
import json
artifact = json.load(open("$ARTIFACT"))
verdict  = json.load(open("$VERDICT"))
brief    = open("$BRIEF").read()

sources_count = len(artifact.get("sources", []))
findings_count = len(artifact.get("findings", []))
overall = verdict["overall"]
created = verdict.get("composed_at", "")

# Frontmatter
print("---")
print(f"slug: $SLUG")
print(f"verdict: {overall}")
print(f"attempts: $ATTEMPTS")
print(f"created: {created}")
print(f"sources_count: {sources_count}")
print(f"findings_count: {findings_count}")
print("---")
print()

# Brief excerpt (first 500 chars)
excerpt = brief[:500]
if len(brief) > 500:
    excerpt += "..."
print("# Brief")
print(excerpt.rstrip())
print()

# Verdict summary
det_checks = verdict["deterministic"]["checks"]
det_pass = sum(1 for c in det_checks if c.get("status") == "pass")
det_total = sum(1 for c in det_checks if c.get("status") in ("pass", "fail"))
sem_checks = verdict["semantic"]["checks"]
if isinstance(sem_checks, dict) and sem_checks:
    sem_pass = sum(1 for c in sem_checks.values() if c.get("status") == "pass")
    sem_total = len(sem_checks)
    sem_summary = f"{verdict['semantic']['overall']} ({sem_pass}/{sem_total} checks)"
else:
    sem_summary = verdict['semantic']['overall']

print("# Verdict Summary")
print(f"- deterministic: {verdict['deterministic']['overall']} ({det_pass}/{det_total} checks)")
print(f"- semantic: {sem_summary}")
if verdict.get("reasons"):
    print()
    print("## Concerns")
    for r in verdict["reasons"]:
        print(f"- {r}")
print()

# Findings
print("# Findings")
for f in artifact.get("findings", []):
    sids = ", ".join(f.get("source_ids", []))
    # Real machine-artifact findings use \`summary\` (per machine-artifact-v1.json),
    # not \`claim\`. Fall back to \`claim\` only for legacy/test artifacts.
    text = f.get("summary", f.get("claim", ""))
    print(f"- [{sids}] {text}")
print()

# Files
print("# Files")
print("- \`final-verdict.json\` — combined verdict")
print("- \`final-machine-artifact.json\` — winning attempt's structured artifact")
print("- \`final-evidence-log.md\` — winning attempt's provenance ledger")
attempts = int("$ATTEMPTS")
for i in range(1, attempts + 1):
    print(f"- \`attempt-{i}/\` — full attempt artifacts")
PYEOF
