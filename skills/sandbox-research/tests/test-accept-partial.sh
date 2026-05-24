#!/usr/bin/env bash
set -euo pipefail
SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/accept-partial.sh"

FAKE_HOME="$(mktemp -d)"
export HOME="$FAKE_HOME"
SLUG="20260502-143000-test-task"
RO="$HOME/research-out"
VAULT="$HOME/.claude/scratchpad/research-vault"

# Set up 3 attempt dirs (original + 2 retries).
for i in "" "-retry1" "-retry2"; do
    mkdir -p "$RO/${SLUG}${i}"
    echo "brief content" > "$RO/${SLUG}${i}/brief.md"
    echo '{"sources":[],"findings":[]}' > "$RO/${SLUG}${i}/machine-artifact.json"
    echo "evidence" > "$RO/${SLUG}${i}/evidence-log.md"
    echo '{}' > "$RO/${SLUG}${i}/fetch-log.jsonl"
    echo '{"verdict":"pass","checks":[],"reasons":[]}' > "$RO/${SLUG}${i}/verdict.json"
    echo '{"overall":"block","reasons":["last reason"]}' > "$RO/${SLUG}${i}/final-verdict.json"
done

"$SCRIPT" "$SLUG"

[ -d "$VAULT/$SLUG" ] || { echo "FAIL: vault entry not created"; exit 1; }
[ -d "$VAULT/$SLUG/attempt-1" ] || { echo "FAIL: attempt-1 missing"; exit 1; }
[ -d "$VAULT/$SLUG/attempt-2" ] || { echo "FAIL: attempt-2 missing"; exit 1; }
[ -d "$VAULT/$SLUG/attempt-3" ] || { echo "FAIL: attempt-3 missing"; exit 1; }
[ -f "$VAULT/$SLUG/final-verdict.json" ] || { echo "FAIL: top-level final-verdict.json missing"; exit 1; }

# Final verdict should be marked needs-review with the accepted-by-user reason.
grep -q '"overall": "needs-review"' "$VAULT/$SLUG/final-verdict.json" \
    || { echo "FAIL: final overall not needs-review"; exit 1; }
grep -q "accepted by user after 3 blocked attempts" "$VAULT/$SLUG/final-verdict.json" \
    || { echo "FAIL: accepted-by-user reason missing"; exit 1; }

# Cleanup should have removed ~/research-out attempts.
[ ! -d "$RO/$SLUG" ] || { echo "FAIL: original ~/research-out/$SLUG not cleaned"; exit 1; }
[ ! -d "$RO/${SLUG}-retry1" ] || { echo "FAIL: retry1 not cleaned"; exit 1; }
[ ! -d "$RO/${SLUG}-retry2" ] || { echo "FAIL: retry2 not cleaned"; exit 1; }

echo "PASS: accept-partial.sh"
