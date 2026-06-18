#!/usr/bin/env bash
# Print a concise view of the working-tree change so the executor can confirm
# the edit stayed within the scope named by the investigation report.
set -euo pipefail

echo "=== Files changed ==="
git diff --stat

echo
echo "=== Untracked files (new) ==="
git ls-files --others --exclude-standard

echo
echo "Confirm: do these files match the investigation report's scope? If not, revert the extras."
