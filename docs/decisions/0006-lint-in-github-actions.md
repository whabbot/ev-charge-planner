---
id: 6
title: Run scripts/lint.sh in GitHub Actions on every push to main and pull request
date: 2026-10-28
status: accepted
---

# Run scripts/lint.sh in GitHub Actions on every push to main and pull request

`.github/workflows/lint.yml` installs the locked dev dependencies with uv and runs `scripts/lint.sh`, so CI and local runs enforce the same checks from one script. Shellcheck comes from the `shellcheck-py` dev dependency, so CI never takes the script's "shellcheck not installed" skip.
