#!/usr/bin/env bash
set -euo pipefail
SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/abandon.sh"

FAKE_HOME="$(mktemp -d)"
export HOME="$FAKE_HOME"
trap 'rm -rf "$FAKE_HOME"' EXIT
SLUG="20260502-143000-abandon-test"
RO="$HOME/research-out"
VAULT="$HOME/.claude/scratchpad/research-vault"

mkdir -p "$RO/$SLUG" "$RO/${SLUG}-retry1" "$RO/${SLUG}-retry2"
touch "$RO/$SLUG/x" "$RO/${SLUG}-retry1/x" "$RO/${SLUG}-retry2/x"
mkdir -p "$VAULT"  # vault should not be touched

"$SCRIPT" "$SLUG"

[ ! -d "$RO/$SLUG" ] || { echo "FAIL: original not removed"; exit 1; }
[ ! -d "$RO/${SLUG}-retry1" ] || { echo "FAIL: retry1 not removed"; exit 1; }
[ ! -d "$RO/${SLUG}-retry2" ] || { echo "FAIL: retry2 not removed"; exit 1; }
[ ! -d "$VAULT/$SLUG" ] || { echo "FAIL: vault entry was created (should not be)"; exit 1; }

# Guard-rejection scenario: bad slugs must exit non-zero, must NOT delete a
# pre-existing legit dir, and must NOT create any vault entry. Use a sentinel
# dir plus a vault-entry count invariant (count is robust to slugs containing
# path-navigation chars like ".." or "/", which would otherwise resolve to
# ancestor/sibling paths and confuse a per-slug [ -d ] check).
SENTINEL="legit-sentinel-slug"
mkdir -p "$RO/$SENTINEL"
touch "$RO/$SENTINEL/keep"
vault_count() { find "$VAULT" -mindepth 1 -maxdepth 1 -type d | wc -l; }
before="$(vault_count)"
for bad in "" ".." "foo/bar" "a.b"; do
    if "$SCRIPT" "$bad" 2>/dev/null; then
        echo "FAIL: guard let through '$bad'"; exit 1
    fi
    [ -d "$RO/$SENTINEL" ] || { echo "FAIL: guard '$bad' deleted sentinel dir"; exit 1; }
    [ -f "$RO/$SENTINEL/keep" ] || { echo "FAIL: guard '$bad' deleted sentinel contents"; exit 1; }
done
[ "$(vault_count)" = "$before" ] || { echo "FAIL: guard rejection changed vault entry count"; exit 1; }

echo "PASS: abandon.sh"
