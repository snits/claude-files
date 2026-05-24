#!/usr/bin/env bash
# run-tests.sh — run all helper-script tests.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fail=0
for t in "$DIR"/test-*.sh; do
    if ! "$t"; then
        fail=$((fail + 1))
    fi
done
if [ "$fail" -gt 0 ]; then
    echo "$fail test file(s) failed" >&2
    exit 1
fi
echo "All helper-script tests passed."
