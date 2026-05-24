#!/usr/bin/env bash
# gen-slug.sh — generate <YYYYMMDD-HHMMSS>-<3-word-summary> slug for a task.
#
# Usage:
#   gen-slug.sh [--fallback-only] <task-text>
#
# Calls `claude -p` (or $CLAUDE_CMD for testing) to derive a 3-word summary,
# sanitizes it, and prepends a timestamp. Falls back to sha256-prefix(task)
# if the summary is empty or contains no usable characters.
#
# Output: single line with the slug, on stdout.
set -euo pipefail

FALLBACK_ONLY=0
if [ "${1:-}" = "--fallback-only" ]; then
    FALLBACK_ONLY=1
    shift
fi

TASK="${1:-}"
[ -n "$TASK" ] || { echo "usage: gen-slug.sh [--fallback-only] <task-text>" >&2; exit 2; }

TS="$(date +%Y%m%d-%H%M%S)"

fallback_slug() {
    local hash
    hash="$(printf '%s' "$TASK" | sha256sum | cut -c1-8)"
    echo "${TS}-${hash}"
}

if [ "$FALLBACK_ONLY" -eq 1 ]; then
    fallback_slug
    exit 0
fi

CLAUDE_CMD="${CLAUDE_CMD:-claude -p}"

# Ask claude for 3 lowercase hyphenated keywords summarizing the task.
PROMPT="Summarize this research task in exactly 3 lowercase hyphenated keywords. Output ONLY the keywords joined by hyphens, nothing else. Example: 'tokio-worker-stealing'. Task: $TASK"

SUMMARY="$(printf '%s\n' "$PROMPT" | $CLAUDE_CMD 2>/dev/null | head -1 | tr -d '\r' | tr 'A-Z' 'a-z' | tr ' ' '-' | tr -cd 'a-z0-9-' )"

# Trim to first 30 chars and strip leading/trailing hyphens.
SUMMARY="${SUMMARY:0:30}"
SUMMARY="${SUMMARY##-}"
SUMMARY="${SUMMARY%%-}"

# Validate: at least one alphanumeric. If empty after sanitize, fall back.
if [ -z "$SUMMARY" ] || ! echo "$SUMMARY" | grep -q '[a-z0-9]'; then
    fallback_slug
    exit 0
fi

echo "${TS}-${SUMMARY}"
