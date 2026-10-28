#!/usr/bin/env bash
# Run one user-facing command exactly as a user would and capture proof.
# Usage: drive.sh <feature-id>/<step> -- <command> [args...]
# The command runs from the repo root. Writes
# <evidence>/<feature-id>/<step>.{cmd,stdout,stderr,exit} and echoes stdout,
# stderr and the exit code. Exits 0 even when the command fails so the caller
# can assert on the recorded exit code.
set -euo pipefail
# shellcheck source=_common.sh
source "$(dirname "$0")/_common.sh"
require_run_id

label="${1:?usage: drive.sh <feature-id>/<step> -- <command> [args...]}"; shift
[[ "${1:-}" == "--" ]] && shift
[[ $# -gt 0 ]] || { echo "drive.sh: no command given after --" >&2; exit 64; }
out="$EVIDENCE_ROOT/$VERIFY_RUN_ID/$label"
mkdir -p "$(dirname "$out")"

cd "$REPO_ROOT"
printf '%q' "$1" > "$out.cmd"
[[ $# -gt 1 ]] && printf ' %q' "${@:2}" >> "$out.cmd"
echo >> "$out.cmd"

set +e
"$@" > "$out.stdout" 2> "$out.stderr"
code=$?
set -e
echo "$code" > "$out.exit"

cat "$out.stdout"
[[ -s "$out.stderr" ]] && { echo "--- stderr"; cat "$out.stderr"; }
echo "--- exit $code; evidence: $out.{cmd,stdout,stderr,exit}"
