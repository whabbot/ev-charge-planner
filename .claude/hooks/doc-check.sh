#!/usr/bin/env bash
# Stop: if this turn changed files, ask a headless doc-checking subagent whether
# the maintained docs need updating, and block the stop with its findings if so.
# Disable for a session with DOC_CHECK_DISABLE=1.
set -uo pipefail
[[ -n "${DOC_CHECK_SUBAGENT:-}" || -n "${DOC_CHECK_DISABLE:-}" ]] && exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0
source .claude/hooks/_snapshot.sh

input="$(cat)"
session_id="$(jq -r '.session_id // "default"' <<<"$input")"
# Already continuing because of a previous block: don't re-check, never loop.
[[ "$(jq -r '.stop_hook_active // false' <<<"$input")" == "true" ]] && exit 0

baseline_file=".claude/state/turn-baseline-$session_id"
[[ -f "$baseline_file" ]] || exit 0
baseline="$(cat "$baseline_file")"
current="$(snapshot_tree)"
[[ "$baseline" == "$current" ]] && exit 0

changed="$(git diff --name-status "$baseline" "$current")"
[[ -z "$changed" ]] && exit 0

state=".claude/state"
diff_file="$state/doc-check-diff-$session_id.patch"
git diff --stat "$baseline" "$current" > "$diff_file"
echo >> "$diff_file"
# Cap the patch so a large refactor can't blow the subagent's context.
git diff "$baseline" "$current" | head -c 120000 >> "$diff_file"

schema='{"type":"object","properties":{"needs_update":{"type":"boolean"},"updates":{"type":"array","items":{"type":"object","properties":{"doc":{"type":"string"},"why":{"type":"string"},"what":{"type":"string"}},"required":["doc","why","what"]}}},"required":["needs_update","updates"]}'
prompt="$(cat .claude/hooks/doc-check-prompt.md)

## Files changed this turn (name-status)

$changed

## Diff of this turn

The full diff (stat first, capped at 120 KB) is in \`$diff_file\`. Read it."

report="$state/doc-check-last-$session_id.json"
DOC_CHECK_SUBAGENT=1 claude -p \
  --setting-sources project \
  --strict-mcp-config \
  --no-session-persistence \
  --model sonnet \
  --tools Read,Grep,Glob \
  --max-budget-usd 0.50 \
  --output-format json \
  --json-schema "$schema" \
  "$prompt" < /dev/null > "$report" 2> "$report.stderr"
code=$?

if [[ $code -ne 0 ]] || ! jq -e '.structured_output.needs_update | type == "boolean"' "$report" >/dev/null 2>&1; then
  jq -n --arg m "doc-check: subagent failed (exit $code); docs not checked. See $report.stderr" '{systemMessage: $m}'
  exit 0
fi

if [[ "$(jq -r '.structured_output.needs_update' "$report")" == "true" ]]; then
  reason="$(jq -r '"The doc-check subagent found docs that this turn'"'"'s changes made stale. Update them now (keep edits minimal and factual), run scripts/lint.sh, then finish:\n" + ([.structured_output.updates[] | "- \(.doc): \(.why) → \(.what)"] | join("\n"))' "$report")"
  jq -n --arg r "$reason" '{decision: "block", reason: $r}'
else
  jq -n '{systemMessage: "doc-check: docs are up to date with this turn'"'"'s changes"}'
fi
