---
milestone: 4
title: Home Assistant webhook for a single charger
status: todo
depends_on: [3]
---

# Home Assistant webhook for a single charger

## Goal

Let Home Assistant fetch or receive the current plan in a shape it can turn directly into scheduled switch or charge-rate actions for one charger.

## Scope

- `GET` returns the latest plan for a vehicle. `POST` creates a plan from HA-supplied inputs (SoC, departure) and returns it.
- Payload shaped for HA automations: an ordered list of `{start, end, action: on | off, kw}` windows in ISO 8601 with offsets. Contiguous chosen slots are merged into one window. The payload also carries plan id, objective, created-at and totals.
- Plans are stored so `GET` has something to return. This needs the `Vehicle`/`Plan` store if milestone 2 did not add it.
- Re-plan job: when next-day Agile prices land (around 16:00 UK), re-plan any pending departure and replace the stored plan, so HA picks up the better schedule. The build plan gives this no milestone. It sits here because a webhook plan goes stale without it.
- A shared-secret token on the webhook.
- An example HA automation (YAML) in the docs that consumes the payload.

## Out of scope

- Two chargers or a shared fuse (milestone 5).
- Start/stop count limits and charger retry logic. Flaky chargers are an integration retry problem ([non-goals](../intent.md#non-goals)).
- Reading SoC from the car (milestone 5).

## Acceptance criteria

- [ ] `GET` and `POST` return the same window list for the same stored plan.
- [ ] Merged windows cover exactly the chosen slots. A partly used slot carries its reduced kW or a shortened window, and the energy still sums to the need.
- [ ] The re-plan job, run with a pinned "now" after the next-day publish, produces a plan no worse than the one it replaces for the same objective.
- [ ] Requests without the token are rejected.
- [ ] The example automation is valid HA YAML and refers only to fields the payload has.

## Verification

Drive `GET` and `POST` through `drive.sh` against the live APIs with a pinned "now". Run the re-plan job once by hand and capture the before and after plans. Test against a real Home Assistant instance if one is available. Otherwise say that the HA side was not exercised.

## Docs to update

- New feature file for the webhook (and re-plan job), linked from the feature map README.
- [architecture.md](../architecture.md): webhook, store and re-plan job from planned to built.
- A decision for the payload shape, the auth method and how the re-plan job is scheduled.
