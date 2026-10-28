---
milestone: 3
title: Next.js UI with one form, one timeline chart and a cost/carbon toggle
status: todo
depends_on: [2]
---

# Next.js UI with one form, one timeline chart and a cost/carbon toggle

## Goal

Give the household a single page: enter the car and departure, see when the car will charge, and see what that saves against plugging in now.

## Scope

- One form with the `POST /plan` inputs: battery kWh, charge kW, current SoC (always typed by the user, never prefilled from a guess), target SoC, departure (Europe/London), postcode and objective.
- One timeline chart from now to departure. It shows price and carbon intensity per half-hour and highlights the chosen slots, including partly used ones.
- A cost/carbon toggle that re-plans and redraws.
- Totals panel: plan vs charge now in £ and gCO₂, with the saving.
- Shortfall, missing data and the national carbon fallback are shown on the page, not only in the console ([intent: what success looks like](../intent.md#what-success-looks-like)).
- The UI calls the milestone 2 service and does no planning of its own.

## Out of scope

- Saved vehicles and plan history (unless milestone 2 added storage).
- Accounts, auth, mobile apps.
- Webhook and automation (milestone 4).

## Acceptance criteria

- [ ] A valid form submission draws the schedule and totals, and they match the `POST /plan` response for the same inputs.
- [ ] Switching the toggle changes the objective and the highlighted slots without re-entering the form.
- [ ] Times on the chart are Europe/London and correct across a BST/GMT change.
- [ ] Validation errors from the service appear next to the right field.
- [ ] Shortfall and data warnings are visible.
- [ ] Usable at phone width.
- [ ] JS/TS lint and format checks run in `scripts/lint.sh` and CI.

## Verification

Extend the verification skill to launch the service and the UI, and add a doctor check for both. Drive the page in a real browser: submit the form, toggle the objective and capture screenshots of the chart and totals as evidence. Cross-check the totals against a `POST /plan` call with the same pinned "now".

## Docs to update

- New feature file for the UI, linked from the feature map README.
- [architecture.md](../architecture.md): UI from planned to built.
- `scripts/lint.sh` and `.github/workflows/lint.yml` for the new language. Ruff does not cover it.
- A decision for the chart library and how the UI reaches the service (proxy or CORS).
