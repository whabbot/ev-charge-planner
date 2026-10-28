#!/usr/bin/env bash
# Prepare a verification run: sync deps once, create an evidence dir.
# Usage: eval "$(.agents/skills/verify-ev-charge-planner/scripts/launch.sh)"
# stdout is only `export` lines; progress goes to stderr.
set -euo pipefail
# shellcheck source=_common.sh
source "$(dirname "$0")/_common.sh"

command -v uv >/dev/null || { echo "uv not found on PATH" >&2; exit 1; }
(cd "$REPO_ROOT" && uv sync --quiet) >&2

run_id="${VERIFY_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
mkdir -p "$EVIDENCE_ROOT/$run_id" "$SCRATCH_ROOT/$run_id"
git -C "$REPO_ROOT" rev-parse --short HEAD > "$EVIDENCE_ROOT/$run_id/REVISION"
git -C "$REPO_ROOT" status --porcelain >> "$EVIDENCE_ROOT/$run_id/REVISION"

echo "ready: run $run_id, evidence in $EVIDENCE_ROOT/$run_id" >&2
echo "export VERIFY_RUN_ID=$run_id"
