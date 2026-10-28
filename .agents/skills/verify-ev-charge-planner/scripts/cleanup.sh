#!/usr/bin/env bash
# Remove this run's scratch state. Never touches evidence. Nothing is
# long-running yet, so there are no processes or ports to stop.
set -euo pipefail
# shellcheck source=_common.sh
source "$(dirname "$0")/_common.sh"
require_run_id
rm -rf "${SCRATCH_ROOT:?}/$VERIFY_RUN_ID"
echo "cleanup: done; evidence kept in $EVIDENCE_ROOT/$VERIFY_RUN_ID"
