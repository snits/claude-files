#!/usr/bin/env bash
set -euo pipefail
SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/accept-partial.sh"

FAKE_HOME="$(mktemp -d)"
export HOME="$FAKE_HOME"
trap 'rm -rf "$FAKE_HOME"' EXIT
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

# Guard-rejection scenario: bad slugs must exit non-zero and create no vault dir.
# Use a vault-entry count invariant (robust to slugs containing path-navigation
# chars like ".." or "/", which would resolve to ancestor/sibling paths).
vault_count() { find "$VAULT" -mindepth 1 -maxdepth 1 -type d | wc -l; }
before="$(vault_count)"
for bad in "" ".." "foo/bar" "a.b"; do
    if "$SCRIPT" "$bad" 2>/dev/null; then
        echo "FAIL: guard let through '$bad'"; exit 1
    fi
done
[ "$(vault_count)" = "$before" ] || { echo "FAIL: guard rejection changed vault entry count"; exit 1; }

# No-attempts scenario: a valid slug with no matching dirs must exit 2 AND must
# NOT create a (stale, empty) vault entry. Guards the mkdir-after-guard fix.
NOSLUG="20260502-160000-no-attempts"
before_na="$(vault_count)"
if "$SCRIPT" "$NOSLUG" 2>/dev/null; then
    echo "FAIL: no-attempts slug did not exit non-zero"; exit 1
fi
[ ! -d "$VAULT/$NOSLUG" ] || { echo "FAIL: no-attempts slug left a stale vault dir"; exit 1; }
[ "$(vault_count)" = "$before_na" ] || { echo "FAIL: no-attempts slug changed vault entry count"; exit 1; }

# Partial-attempts scenario: only <slug> and <slug>-retry1 present (no -retry2).
# The LAST present attempt is retry1; top-level final-* must come from it.
PSLUG="20260502-150000-partial-task"
for i in "" "-retry1"; do
    mkdir -p "$RO/${PSLUG}${i}"
    echo "brief content $i" > "$RO/${PSLUG}${i}/brief.md"
    echo "{\"sources\":[],\"findings\":[\"$i\"]}" > "$RO/${PSLUG}${i}/machine-artifact.json"
    echo "evidence $i" > "$RO/${PSLUG}${i}/evidence-log.md"
    echo '{}' > "$RO/${PSLUG}${i}/fetch-log.jsonl"
    echo '{"verdict":"pass","checks":[],"reasons":[]}' > "$RO/${PSLUG}${i}/verdict.json"
    echo "{\"overall\":\"block\",\"reasons\":[\"reason$i\"]}" > "$RO/${PSLUG}${i}/final-verdict.json"
done

"$SCRIPT" "$PSLUG"

[ -d "$VAULT/$PSLUG/attempt-1" ] || { echo "FAIL: partial attempt-1 missing"; exit 1; }
[ -d "$VAULT/$PSLUG/attempt-2" ] || { echo "FAIL: partial attempt-2 missing"; exit 1; }
[ ! -d "$VAULT/$PSLUG/attempt-3" ] || { echo "FAIL: partial attempt-3 should not exist"; exit 1; }
[ -f "$VAULT/$PSLUG/final-verdict.json" ] || { echo "FAIL: partial final-verdict.json missing"; exit 1; }

# Top-level final-* must come from retry1 (the LAST present attempt).
grep -q '"-retry1"' "$VAULT/$PSLUG/final-machine-artifact.json" \
    || { echo "FAIL: partial final-machine-artifact not from retry1"; exit 1; }
grep -q "evidence -retry1" "$VAULT/$PSLUG/final-evidence-log.md" \
    || { echo "FAIL: partial final-evidence-log not from retry1"; exit 1; }
grep -q '"overall": "needs-review"' "$VAULT/$PSLUG/final-verdict.json" \
    || { echo "FAIL: partial final overall not needs-review"; exit 1; }
grep -q "reason-retry1" "$VAULT/$PSLUG/final-verdict.json" \
    || { echo "FAIL: partial final reason not from retry1"; exit 1; }

# Working dirs for the partial run must be cleaned up.
[ ! -d "$RO/$PSLUG" ] || { echo "FAIL: partial original not cleaned"; exit 1; }
[ ! -d "$RO/${PSLUG}-retry1" ] || { echo "FAIL: partial retry1 not cleaned"; exit 1; }

echo "PASS: accept-partial.sh"
