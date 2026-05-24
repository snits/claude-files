#!/usr/bin/env bash
# Test build-retry-brief.sh produces correct retry brief.
set -euo pipefail
SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/build-retry-brief.sh"

TMP="$(mktemp -d)"
trap "rm -rf $TMP" EXIT

# Set up: original brief + final-verdict.json with two failed reasons.
cat > "$TMP/brief.md" <<'EOF'
Research the impact of Tokio's work-stealing on tail latency.
EOF

cat > "$TMP/final-verdict.json" <<'EOF'
{
  "overall": "block",
  "reasons": [
    "semantic.claims_traceable (fail): Finding F2 cites src-002 but evidence-log src-002 doesn't support the throughput claim.",
    "semantic.brief_addressed (fail): Findings cover scheduler internals, not tail latency."
  ]
}
EOF

OUT="$TMP/retry-brief.md"
"$SCRIPT" "$TMP/brief.md" "$TMP/final-verdict.json" > "$OUT"

# Assertions
grep -q "Research the impact of Tokio's work-stealing" "$OUT" \
    || { echo "FAIL: original brief content missing"; exit 1; }
grep -q "Prior attempt was blocked by validator" "$OUT" \
    || { echo "FAIL: feedback header missing"; exit 1; }
grep -q "semantic.claims_traceable" "$OUT" \
    || { echo "FAIL: first reason missing"; exit 1; }
grep -q "semantic.brief_addressed" "$OUT" \
    || { echo "FAIL: second reason missing"; exit 1; }
grep -q "Address these in this attempt" "$OUT" \
    || { echo "FAIL: anchor footer missing"; exit 1; }

echo "PASS: build-retry-brief.sh"
