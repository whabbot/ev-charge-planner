# EV Charge Planner

A planner that picks the cheapest or lowest-carbon half-hours to charge an EV at home before departure. Nothing is built yet: a rates CLI that predated the build plan was removed, and milestone 1 is to be rebuilt from `smart-ev-charge-planner-build-plan.md`, which is the roadmap and takes precedence.

## Commands

- Lint everything: `scripts/lint.sh` (ruff check, ruff format check, doc-structure lint, shellcheck). CI runs the same script (`.github/workflows/lint.yml`).
- Format: `uv run ruff format .`
- Verify behavior end to end: use the `verify-ev-charge-planner` skill (`.agents/skills/verify-ev-charge-planner/SKILL.md`)

## Maintained docs

Keep these true in the same change that makes them stale:

| Doc | Update when |
| --- | --- |
| [Feature map](.agents/skills/verify-ev-charge-planner/features/README.md) and the verify skill | a user-facing flag, output, exit code, entry point or launch step changes |
| [docs/architecture.md](docs/architecture.md) | a component, data source, store or flow is added, moved or built |
| [docs/intent.md](docs/intent.md) | a goal, principle or non-goal changes |
| [docs/decisions/](docs/decisions/README.md) | a product or project decision is made (add a numbered file; supersede, don't rewrite) |
| [docs/tickets/](docs/tickets/README.md) | work on a milestone starts or finishes (`status`), or its scope or acceptance criteria change |
| `pyproject.toml`, `scripts/lint.sh`, `scripts/lint_docs.py` | new code falls outside lint coverage, or a doc's required structure changes |

A Stop hook (`.claude/hooks/doc-check.sh`) diffs each turn's changes and runs a headless doc-checking subagent. If a doc is stale, it blocks the stop and lists what to update. Set `DOC_CHECK_DISABLE=1` to skip it. Its last report is in `.claude/state/doc-check-last-<session>.json`.

## Conventions

- Python >= 3.12 via uv. The planner core is stdlib only.
- Times are compared in UTC. User input and output are Europe/London.
- Never mock the Octopus or Carbon Intensity APIs to prove behavior. Let callers pin the planning time ("now") so runs are reproducible.
