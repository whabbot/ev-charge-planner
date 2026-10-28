---
milestone: 2
title: POST /plan service on the planner core
status: todo
depends_on: [1]
---

# POST /plan service on the planner core

## Goal

Expose the milestone 1 planner core as a small HTTP service. It takes the product-shape inputs and returns a half-hour schedule with £ and gCO₂ totals against charging now.

## Scope

- `POST /plan` request: battery size (kWh), current SoC (required, the user states it each time), target SoC, departure time, postcode or DNO region, objective (`cost` | `carbon`), charge kW (or a vehicle id that supplies it) and an optional pinned "now".
- Energy need = `battery_kwh × (soc_target − soc_now) / 100`. The core and fetchers come from milestone 1 unchanged.
- Response: slots `[{start, end, kw, price, intensity}]` with times in Europe/London, plan totals and charge-now totals in £ and gCO₂, any shortfall in kWh, and warnings (missing data, national carbon fallback).
- Validation: SoC values outside 0 to 100, a departure in the past, or an unknown postcode or region return a 4xx with a clear message. An upstream API failure returns a 5xx that names the API.
- Data model from the build plan: `Vehicle` (id, name, battery_kwh, charge_kw), `PlanRequest`, `Plan` (id, request snapshot, slots, totals). Storage is optional at this milestone. If added, use SQLite.

## Out of scope

- UI (milestone 3), webhook and re-planning (milestone 4).
- Auth, multiple users, Postgres.

## Acceptance criteria

- [ ] Unit tests from the build plan, run against fixed series:
  - [ ] **Empty need**: target SoC ≤ current SoC returns no slots, zero totals and a 200.
  - [ ] **Already full**: current SoC at 100 returns no slots and says the car is already full.
  - [ ] **Not enough cheap slots before departure**: returns the best partial plan with the shortfall in kWh and a warning, not an error.
- [ ] Response slots and totals match what the milestone 1 CLI prints for the same inputs and pinned "now".
- [ ] Plan totals are never worse than the charge-now baseline for the chosen objective.
- [ ] Postcode and DNO region inputs that name the same region give the same plan.
- [ ] Invalid inputs return 4xx and API outages return 5xx. Neither returns a 200 with an empty plan.
- [ ] `scripts/lint.sh` passes, and CI runs the tests.

## Verification

Add a doctor check that the service starts and answers. Drive `POST /plan` with `curl` through `drive.sh` against the live APIs with a pinned "now": one cost plan, one carbon plan, the three edge cases above and one invalid request. Check energy delivered against the SoC delta.

## Docs to update

- New feature file for `POST /plan`, linked from the feature map README. Update the skill's launch, doctor and cleanup for a long-running service.
- [architecture.md](../architecture.md): plan service (and store, if added) from planned to built.
- A decision for the service framework, and for storage if one is chosen.

## Open questions

- Python stdlib `http.server` or a framework? The build plan allows "Python or Node". The core stays stdlib only either way.
- Is charging efficiency modelled? The build plan is silent, so v1 assumes none unless decided otherwise.
