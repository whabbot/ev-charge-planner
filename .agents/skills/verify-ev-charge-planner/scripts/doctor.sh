#!/usr/bin/env bash
# Read-only: is this checkout worth driving? Exits non-zero on the first failure.
set -euo pipefail
# shellcheck source=_common.sh
source "$(dirname "$0")/_common.sh"
cd "$REPO_ROOT"

ok() { echo "ok:   $*"; }
fail() { echo "FAIL: $*"; exit 1; }

command -v uv >/dev/null || fail "uv not on PATH"
ok "uv $(uv --version | cut -d' ' -f2)"
py="$(uv run --frozen python -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null)" \
  || fail "uv run python failed (run launch.sh first)"
[[ "$py" == 3.1[2-9] ]] || fail "python $py < 3.12"
ok "python $py"
ok "revision $(git rev-parse --short HEAD)$( [[ -n "$(git status --porcelain)" ]] && echo ' +dirty')"

code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 \
  'https://api.octopus.energy/v1/products/AGILE-24-10-01/')"
[[ "$code" == 200 ]] || fail "Octopus API returned $code"
ok "Octopus API reachable"
code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 \
  'https://api.carbonintensity.org.uk/intensity')"
[[ "$code" == 200 ]] || fail "Carbon Intensity API returned $code"
ok "Carbon Intensity API reachable"

if [[ -n "${VERIFY_RUN_ID:-}" ]]; then
  [[ -d "$EVIDENCE_ROOT/$VERIFY_RUN_ID" ]] || fail "VERIFY_RUN_ID=$VERIFY_RUN_ID has no evidence dir; rerun launch.sh"
  ok "evidence dir $EVIDENCE_ROOT/$VERIFY_RUN_ID"
else
  echo "note: VERIFY_RUN_ID unset; drive.sh needs it"
fi
