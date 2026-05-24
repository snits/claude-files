#!/usr/bin/env bash
# accept-partial.sh — exhaustion path: force-archive last attempt as needs-review.
#
# Usage:
#   accept-partial.sh <slug>
#
# Reads ~/research-out/<slug>{,-retry1,-retry2}/, copies all attempts to
# ~/.claude/scratchpad/research-vault/<slug>/attempt-N/, sets the final-verdict
# to needs-review with reason "accepted by user after 3 blocked attempts: ...",
# then deletes the explicit <slug>{,-retry1,-retry2} directories (no glob).
set -euo pipefail

SLUG="$1"
[ -n "$SLUG" ] || { echo "usage: accept-partial.sh <slug>" >&2; exit 2; }

# Slugs are produced by gen-slug.sh and are always [a-z0-9-]. Reject anything
# else before any rm -rf — this subsumes ../ and / traversal and also blocks
# '.', glob metacharacters, and whitespace.
case "$SLUG" in
    *[^a-z0-9-]*) echo "accept-partial.sh: slug must contain only [a-z0-9-]" >&2; exit 2;;
esac

RO="$HOME/research-out"
VAULT="$HOME/.claude/scratchpad/research-vault/$SLUG"

# Find all attempt directories (in chronological order: <slug>, <slug>-retry1, <slug>-retry2).
ATTEMPTS=()
for suffix in "" "-retry1" "-retry2"; do
    if [ -d "$RO/${SLUG}${suffix}" ]; then
        ATTEMPTS+=("$RO/${SLUG}${suffix}")
    fi
done

[ "${#ATTEMPTS[@]}" -gt 0 ] || { echo "accept-partial.sh: no attempts found for $SLUG" >&2; exit 2; }

mkdir -p "$VAULT"

# Copy each attempt into attempt-N/ subdirs.
N=1
for src in "${ATTEMPTS[@]}"; do
    dst="$VAULT/attempt-$N"
    mkdir -p "$dst"
    for f in brief.md machine-artifact.json evidence-log.md fetch-log.jsonl verdict.json semantic-verdict.json final-verdict.json; do
        [ -f "$src/$f" ] && cp "$src/$f" "$dst/"
    done
    N=$((N + 1))
done

# Top-level final-* files come from the LAST attempt.
LAST="${ATTEMPTS[-1]}"
[ -f "$LAST/machine-artifact.json" ] && cp "$LAST/machine-artifact.json" "$VAULT/final-machine-artifact.json"
[ -f "$LAST/evidence-log.md" ]       && cp "$LAST/evidence-log.md"       "$VAULT/final-evidence-log.md"

# Construct an accept-partial final-verdict.json marked needs-review.
LAST_VERDICT="$LAST/final-verdict.json"
if [ -f "$LAST_VERDICT" ]; then
    # Unquoted PYEOF heredoc: the shell must expand $LAST_VERDICT into the python
    # source before python runs. Do NOT change to <<'PYEOF' — python would then
    # receive the literal string "$LAST_VERDICT". Path is slug-derived ([a-z0-9-]),
    # so the interpolation into the python literal is injection-safe.
    python3 <<PYEOF > "$VAULT/final-verdict.json"
import json
v = json.load(open("$LAST_VERDICT"))
last_reasons = v.get("reasons", [])
new_reasons = [
    f"accepted by user after 3 blocked attempts: {r}" for r in last_reasons
] or ["accepted by user after 3 blocked attempts: (no last reasons recorded)"]
v["overall"] = "needs-review"
v["reasons"] = new_reasons
print(json.dumps(v, indent=2))
PYEOF
fi

# Clean up working dirs.
for src in "${ATTEMPTS[@]}"; do
    rm -rf "$src"
done

echo "Accepted partial result for $SLUG. Vault entry: $VAULT"
