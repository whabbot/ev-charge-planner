# Smart EV Charge Planner — MVP build plan

Scoped from the 8 Oct 2026 design thread. Goal: cheapest or lowest-carbon home charge plan by departure time, with a Home Assistant webhook later.

## Product shape (locked for v1)

- Input: battery size (kWh), current SoC (required, entered by the user each time), target SoC, departure time, postcode (or DNO region), objective (cost | carbon).
- Output: half-hour on/off (or kW) schedule until departure, plus £ and gCO₂ totals vs “charge now”.
- Algorithm for v1: fetch Agile half-hourly prices and/or carbon forecast, compute energy still needed at a fixed charge rate, take the best N independent slots. No LP/MILP yet.
- Cut from v1: start/stop count limits (users don’t care; flaky chargers are an integration retry problem).
- Stretch (not v1):
  - Tapering above ~80% SoC
  - Learn each car's real charge curve from charger power readings per session (starting SoC + energy delivered + battery size)
  - Auto-fill current SoC from car data (manufacturer cloud via Home Assistant, or an aggregator API like Smartcar/Enode)
  - "Miles driven today" as an alternative to entering SoC
  - Blended cost–carbon objective
  - Two chargers sharing one household fuse (amperage cap)

## Why sort is enough for v1

With fixed kW and independent slots, sorting by £/kWh or gCO₂/kWh and picking the cheapest N half-hours is optimal. A solver only earns its keep once slots stop being independent (taper, shared supply, export). Ship the sort, then show where it breaks when you add the next constraint — better portfolio story than “I used OR-Tools”.

## Suggested stack

- Next.js app (inputs + schedule chart)
- Small Python or Node service: fetch rates, compute plan, expose `POST /plan`
- Postgres optional at first (store saved vehicles / plans); SQLite fine for solo use
- Cron or queue later: re-plan when next-day Agile prices land (~16:00 UK)

## APIs (already verified live on 8 Oct)

- Octopus Energy Agile unit rates (public product/unit-rates; no auth for prices)
- Carbon Intensity API (NESO; regional 48h by postcode outward code)
- Open Charge Map only if you add “chargers on a route” later

## Data model (minimal)

- `Vehicle`: id, name, battery_kwh, charge_kw
- `PlanRequest`: vehicle_id, soc_now, soc_target, depart_at, objective (`cost` | `carbon`), postcode
- `Plan`: id, request snapshot, slots[{start, end, kw, price, intensity}], totals

## Milestones

1. **Rates CLI** — pull next 24–48h Agile + carbon for a postcode; print sorted cheapest N slots for a dummy energy need.
2. **`POST /plan`** — accept the inputs above; return slots + totals; unit tests for “empty need”, “already full”, “not enough cheap slots before departure”.
3. **UI** — one form, one timeline chart, cost vs carbon toggle.
4. **Webhook** — `GET/POST` plan in a shape Home Assistant can turn into scheduled switch/charge-rate actions (single charger first).
5. **Stretch** — taper curve and learned charge curves, SoC auto-fill, blended objective, then dual-charger amperage cap; introduce a solver only at that point and keep the sorted plan as the baseline comparison.

## Out of scope for the portfolio cut

- Manual plug swapping (not the product; dual chargers share the fuse, automation sends both commands)
- V2G / export
- Public-route charger booking
- Billing or fleet session counts
