---
milestone: 5
title: Stretch constraints, then a solver against the sorted baseline
status: todo
depends_on: [4]
---

# Stretch constraints, then a solver against the sorted baseline

## Goal

Add the constraints that make half-hours stop being independent, introduce a solver only at that point, and show where and by how much the sorted plan falls short. That comparison is the portfolio story ([intent principle 1](../intent.md#principles)).

This ticket is too large to ship as one change. Split it into the parts below (`m5-a-…` and so on) when work starts.

## Scope

In this order, from the build plan:

1. **Taper and learned charge curves.** Model the reduced charge rate above ~80% SoC. Then learn each car's real curve from charger power readings per session (starting SoC, energy delivered, battery size). Once slot capacity depends on SoC reached, slots are no longer independent.
2. **SoC auto-fill.** Read current SoC from the manufacturer cloud via Home Assistant, or from an aggregator API (Smartcar, Enode). Also offer "miles driven today" as an alternative to entering SoC. Manual entry stays available and wins when given.
3. **Blended cost–carbon objective.** A weight between £ and gCO₂, with the two pure objectives as its end points.
4. **Two chargers on one fuse.** An amperage cap shared across chargers. The webhook sends both chargers' commands.
5. **Solver.** Introduced with the first constraint the sort cannot handle optimally. The sorted plan is always computed too and reported as the baseline next to the solver's plan.

## Out of scope

- V2G or export, manual plug swapping, public-route charger booking, billing or fleet features ([non-goals](../intent.md#non-goals)).

## Acceptance criteria

- [ ] With no stretch constraints active, the solver's plan equals the sorted plan in £ or gCO₂. This is a regression guard on both.
- [ ] Each constraint has a case where the sorted plan is shown to be infeasible or worse, with the size of the gap reported.
- [ ] Every output still carries the charge-now baseline, and solver outputs also carry the sorted baseline.
- [ ] Auto-filled SoC is labelled with its source and age. The planner never silently invents a SoC.
- [ ] Under the dual-charger cap, the combined draw never exceeds the cap in any half-hour.

## Verification

Per part, with the verification skill and a pinned "now". For the solver, drive the same request with and without the constraint and capture both plans and the gap. Real SoC auto-fill and dual-charger runs need real hardware or accounts. Where those are missing, say which path was skipped.

## Docs to update

- [intent.md](../intent.md): principle 3 ("v1 never guesses the battery state") and the solver principle need revisiting once SoC auto-fill and the solver land.
- [architecture.md](../architecture.md): solver and any new data sources (car APIs, charger power readings) from planned to built.
- A decision for each part: taper model, SoC source, blend weighting, solver library.
- Feature files for every new input or output.
