---
milestone: 1
title: Rates CLI over an importable planner core
status: todo
depends_on: []
---

# Rates CLI over an importable planner core

## Goal

Pull the next 24 to 48 hours of Octopus Agile prices and carbon intensity forecasts for a postcode, and print the best half-hours to charge for a given energy need. This rebuilds milestone 1 from the build plan after the pre-plan CLI was removed ([decision 4](../decisions/0004-remove-pre-plan-rates-cli.md)). The planner core written here is the one `POST /plan` (milestone 2) will reuse.

## Scope

- **Planner core**, stdlib only and importable, with no I/O in the planning function. It takes the price and intensity series as input, so tests can feed it fixed data without mocking an API.
  - Plans by energy, not by whole slots. Each slot can deliver at most `charge_kw × usable hours`. The current slot counts only from "now", and the departure slot only up to departure, so a partial first or last slot is usable and is credited only for the time it actually has.
  - Greedy fill: sort usable slots by the objective (p/kWh for `cost`, gCO₂/kWh for `carbon`) and fill the best first until the need is met. The last slot picked may be only partly used. This is optimal while the charge rate is fixed and slots are independent.
  - Charge-now baseline: fill slots in time order from now until the need is met, and report its £ and gCO₂ next to the plan ([intent principle 2](../intent.md#principles)).
  - Shortfall: if the usable slots before departure cannot deliver the need, return the best partial plan and state how many kWh are missing.
- **Data fetchers**:
  - Octopus Agile unit rates for the region of the postcode, using the public grid-supply-point lookup. Do not use a fixed region. Discover the current Agile product rather than hard-coding a product code.
  - NESO Carbon Intensity regional 48 h forecast by outward postcode. If the regional forecast is unavailable, fall back to the national forecast and say so in the output.
  - A slot with no price or no intensity is never treated as zero. It is excluded from the objective that needs it, and any total it would affect is marked partial, naming the missing slots.
- **CLI**: flags for postcode, energy need in kWh (the "dummy energy need"), charge kW, departure time, objective (`cost` | `carbon`, default `cost`) and a pinned planning time ("now") for reproducible runs. Input and output are Europe/London. All comparisons are in UTC.
- **Output**: the chosen slots (local start and end, kWh, p/kWh, gCO₂/kWh), sorted by the objective, then plan and charge-now totals in £ and gCO₂. Use stable labels that the feature map can assert on.
- **Exit codes**: success, bad input, upstream API failure and shortfall each get a defined code, documented in the feature file.

## Out of scope

- SoC and battery inputs (milestone 2 turns those into kWh).
- HTTP service, storage, UI.
- Taper, efficiency losses, start/stop limits ([non-goals](../intent.md#non-goals)).

## Acceptance criteria

- [ ] `charge_kw × hours` of energy is credited for a partial first slot (now mid-slot) and a partial last slot (departure mid-slot), never a full half-hour.
- [ ] Delivered kWh equals the need when enough slots exist, and never overshoots it.
- [ ] For `cost`, plan £ ≤ charge-now £. For `carbon`, plan gCO₂ ≤ charge-now gCO₂.
- [ ] Two postcodes in different DNO regions get different Agile prices for the same pinned time.
- [ ] A missing price or intensity is reported, never summed as zero. The regional-to-national carbon fallback is stated in the output.
- [ ] A departure beyond the published price window, or too close to now, gives a stated shortfall and its exit code.
- [ ] Datetimes are timezone-aware throughout (ruff `DTZ` passes), including across a BST/GMT change.
- [ ] Unit tests cover the core with fixed series: partial slots, exact fill, shortfall, missing data, ties.
- [ ] `scripts/lint.sh` passes, and CI runs the tests.

## Verification

Use the `verify-ev-charge-planner` skill against the live APIs with a pinned "now" and a departure inside the published window. Drive the CLI through `drive.sh` for both objectives, a shortfall case and an invalid postcode. Check the numbers (energy met, plan ≤ baseline), not just the labels.

## Docs to update

- New feature file under `.agents/skills/verify-ev-charge-planner/features/`, linked from its README, and the skill updated to say the CLI is the first surface. Add a doctor check that the CLI starts.
- `scripts/lint_docs.py` `CLI_SOURCES` lists the CLI, and the tests are added to `scripts/lint.sh` or CI.
- [architecture.md](../architecture.md): move the CLI and planner core from planned to built.
- A decision for the package layout and test runner (pytest is not yet a dev dependency).
