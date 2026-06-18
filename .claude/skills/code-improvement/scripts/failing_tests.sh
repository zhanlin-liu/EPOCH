#!/usr/bin/env bash
# Run the project's test command and surface the failures for an EPOCH
# code_improvement investigation. Pass the full test command as one argument.
#
#   bash failing_tests.sh "pytest projects/wine/tests/"
set -uo pipefail

if [ "$#" -lt 1 ]; then
  echo "usage: failing_tests.sh \"<test_cmd>\"" >&2
  exit 2
fi

CMD="$1"
echo "=== Running: $CMD ==="
OUT="$($CMD 2>&1)"
STATUS=$?

echo "$OUT"
echo
echo "=== Failure summary ==="
echo "$OUT" | grep -iE "fail|error" || echo "(no failure/error lines matched)"
echo
echo "exit status: $STATUS"
exit "$STATUS"
