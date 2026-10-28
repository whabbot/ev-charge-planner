#!/usr/bin/env bash
# UserPromptSubmit: remember the working tree as it was when this turn began,
# so the Stop hook can diff exactly what the turn changed.
set -euo pipefail
[[ -n "${DOC_CHECK_SUBAGENT:-}" ]] && exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0
source .claude/hooks/_snapshot.sh

session_id="$(jq -r '.session_id // "default"')"
mkdir -p .claude/state
snapshot_tree > ".claude/state/turn-baseline-$session_id"
