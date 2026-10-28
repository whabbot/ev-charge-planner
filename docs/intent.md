# Intent

Why this project exists, who it is for, and the decisions that should hold as it grows. The [build plan](../smart-ev-charge-planner-build-plan.md) says what to build next. This file says what must stay true while building it. Update it when a goal, principle or non-goal changes. Decisions made along the way live in [decisions/](decisions/README.md), one file each.

## Purpose

Tell an EV driver on a UK half-hourly tariff when to charge at home so the car is ready by departure for the least money or the least carbon, and show how much better that is than plugging in and charging now.

It is also a portfolio piece. It should show that a simple, well-explained algorithm can be shipped first, and show where that algorithm breaks once real constraints arrive. Reaching for a solver on day one would not show that.

## Users

- **Primary:** one household with one EV and an Octopus Agile (or similar half-hourly) tariff, who knows their battery size, current state of charge and departure time.
- **Later:** the same household automating the plan through Home Assistant, possibly with two chargers on one supply.

## What success looks like

- Given battery size, current and target SoC, departure and postcode, the user gets a half-hour schedule that is optimal for the chosen objective under v1 assumptions.
- Every plan is shown next to the charge-now baseline in £ and gCO₂, so the value is visible.
- The output is honest about its limits: missing prices, a regional-to-national carbon fallback, or too little time before departure are stated, not hidden.

## Principles

1. **Sort before solve.** With a fixed charge rate and independent half-hours, picking the N best slots is optimal. Add a solver only when a constraint makes slots interdependent (taper, a shared fuse, export), and keep the sorted plan as the comparison baseline.
2. **Always show the baseline.** A plan without "versus charge now" is not useful.
3. **The user states their SoC.** Auto-fill from car data is a stretch goal. v1 never guesses the battery state.
4. **Live public data, no hidden mocks.** Prices and intensity come from the Octopus and NESO public APIs. Verification drives the real path. Pin the planning time for reproducibility, not stubs.
5. **Times are UTC inside, Europe/London at the edges.** Input and display are UK local time, and every comparison is in UTC.
6. **Ship milestones in order.** CLI, then `POST /plan` with tests, then UI, then webhook, then stretch work.

## Non-goals

- Manual plug swapping between cars.
- Vehicle-to-grid or export optimisation.
- Public route charging or booking.
- Billing, fleet or session-count features.
- Start/stop count limits in v1. Flaky chargers are an integration retry problem.

