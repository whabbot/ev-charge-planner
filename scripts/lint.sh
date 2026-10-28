#!/usr/bin/env bash
# Every lint the repo enforces. Exits non-zero if any fails; runs them all first.
set -uo pipefail
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1

status=0
run() { echo "== $*"; "$@" || status=1; }

run uv run --frozen ruff check .
run uv run --frozen ruff format --check .
run uv run --frozen python scripts/lint_docs.py
if uv run --frozen shellcheck --version >/dev/null 2>&1; then
  run uv run --frozen shellcheck -x scripts/*.sh .claude/hooks/*.sh .agents/skills/*/scripts/*.sh
else
  echo "== shellcheck not installed; skipped (brew install shellcheck)"
fi
exit $status
