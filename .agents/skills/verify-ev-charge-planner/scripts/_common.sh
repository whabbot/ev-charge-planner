# shellcheck shell=bash disable=SC2034  # variables are used by the scripts that source this
# Sourced by the other helpers. Resolves paths; never changes state.
REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
VERIFY_ROOT="$REPO_ROOT/.verify"
EVIDENCE_ROOT="$VERIFY_ROOT/evidence"
SCRATCH_ROOT="$VERIFY_ROOT/tmp"

require_run_id() {
  if [[ -z "${VERIFY_RUN_ID:-}" ]]; then
    echo "VERIFY_RUN_ID is not set. Run: eval \"\$($REPO_ROOT/.agents/skills/verify-ev-charge-planner/scripts/launch.sh)\"" >&2
    exit 64
  fi
}
