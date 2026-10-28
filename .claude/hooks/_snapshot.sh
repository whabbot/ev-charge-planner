# shellcheck shell=bash
# Sourced. snapshot_tree prints a git tree hash of the whole working tree
# (tracked + untracked, .gitignore respected) without touching the real index.
snapshot_tree() {
  local real_index tmp_index
  real_index="$(git rev-parse --git-path index)"
  tmp_index="$(mktemp)"
  [[ -f "$real_index" ]] && cp "$real_index" "$tmp_index"
  GIT_INDEX_FILE="$tmp_index" git add -A >/dev/null 2>&1
  GIT_INDEX_FILE="$tmp_index" git write-tree
  rm -f "$tmp_index"
}
