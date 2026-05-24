#!/usr/bin/env bash
# abandon.sh — exhaustion path: delete the explicit <slug>{,-retry1,-retry2}
# dirs (never a glob) with no vault entry.
#
# Usage:
#   abandon.sh <slug>
set -euo pipefail

SLUG="$1"
[ -n "$SLUG" ] || { echo "usage: abandon.sh <slug>" >&2; exit 2; }

# Refuse to glob if SLUG would resolve to root or be empty after expansion.
case "$SLUG" in
    *..*|*/*) echo "abandon.sh: slug must be a simple name" >&2; exit 2;;
esac

RO="$HOME/research-out"
removed=0
for d in "$RO/$SLUG" "$RO/${SLUG}-retry1" "$RO/${SLUG}-retry2"; do
    if [ -d "$d" ]; then
        rm -rf "$d"
        removed=$((removed + 1))
    fi
done

echo "Abandoned $removed attempt director$([ "$removed" = "1" ] && echo "y" || echo "ies") for $SLUG. No vault entry created."
