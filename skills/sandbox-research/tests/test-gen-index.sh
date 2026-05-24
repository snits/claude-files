#!/usr/bin/env bash
set -euo pipefail
SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/gen-index.sh"

TMP="$(mktemp -d)"
trap "rm -rf $TMP" EXIT

cat > "$TMP/brief.md" <<'EOF'
Research the basic mechanism of Tokio's work-stealing scheduler.
EOF

cat > "$TMP/final-machine-artifact.json" <<'EOF'
{
  "schema_version": "1.0",
  "task_id": "research-test-001",
  "task_type": "web-research",
  "started_at": "2026-05-02T14:00:00-05:00",
  "completed_at": "2026-05-02T14:05:00-05:00",
  "sources": [
    {"source_id": "src-001", "url": "https://tokio.rs/x", "fetch_timestamp": "2026-05-02T14:01:00-05:00", "content_hash": "sha256:abc"}
  ],
  "findings": [
    {"finding_id": "f-001", "summary": "Per-thread queues with work-stealing.", "claim_type": "structural", "source_ids": ["src-001"], "confidence": "high", "ledger_ref": "E1"}
  ],
  "suspicious_content": []
}
EOF

cat > "$TMP/final-verdict.json" <<'EOF'
{
  "schema_version": "1.0",
  "composed_at": "2026-05-02T14:05:30-05:00",
  "deterministic": {"version": "1.0", "overall": "pass", "checks": [{"name":"a","status":"pass"}]},
  "semantic": {"version": "1.0", "overall": "pass", "checks": {"claims_traceable":{"status":"pass","reason":"ok"}}},
  "overall": "pass",
  "reasons": []
}
EOF

# slug, attempts, vault path
"$SCRIPT" "$TMP" "20260502-140530-tokio-worker-stealing" 1 > "$TMP/index.md"

grep -q '^---$' "$TMP/index.md" || { echo "FAIL: frontmatter delimiters missing"; exit 1; }
grep -q '^slug: 20260502-140530-tokio-worker-stealing$' "$TMP/index.md" \
    || { echo "FAIL: slug not in frontmatter"; exit 1; }
grep -q '^verdict: pass$' "$TMP/index.md" \
    || { echo "FAIL: verdict not in frontmatter"; exit 1; }
grep -q '^attempts: 1$' "$TMP/index.md" \
    || { echo "FAIL: attempts not in frontmatter"; exit 1; }
grep -q '^sources_count: 1$' "$TMP/index.md" \
    || { echo "FAIL: sources_count not in frontmatter"; exit 1; }
grep -q '^findings_count: 1$' "$TMP/index.md" \
    || { echo "FAIL: findings_count not in frontmatter"; exit 1; }
grep -q "Tokio's work-stealing scheduler" "$TMP/index.md" \
    || { echo "FAIL: brief excerpt missing"; exit 1; }
grep -q "Per-thread queues with work-stealing." "$TMP/index.md" \
    || { echo "FAIL: finding text missing"; exit 1; }

echo "PASS: gen-index.sh"
