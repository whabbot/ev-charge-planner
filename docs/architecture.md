# Architecture

What exists today and what is planned. Solid boxes are built. Dashed boxes are planned from the [build plan](../smart-ev-charge-planner-build-plan.md) and do not exist yet. Update this file whenever a component, data source, entry point or data flow is added, removed or renamed.

## Today: nothing built

There is no planner code yet. A rates CLI written before the build plan was removed because it disagreed with the plan (see [decision 4](decisions/0004-remove-pre-plan-rates-cli.md)). The repo holds only the build plan, these docs, the lint scripts (also run by the `Lint` GitHub Actions workflow in `.github/workflows/lint.yml` on pushes to main and pull requests), the doc-check hook and the verification skill shell.

## Planned: milestones 1 to 5

```mermaid
flowchart LR
    user([User])
    ha([Home Assistant])

    subgraph planned["Planned, not built"]
        cli["Rates CLI<br/>milestone 1"]
        core["Planner core<br/>energy-based sort of half-hours,<br/>partial first/last slot allowed"]
        ui["Next.js UI<br/>form + timeline chart,<br/>cost / carbon toggle"]
        api["Plan service<br/>POST /plan"]
        hook["Webhook<br/>GET/POST plan for HA"]
        db[("SQLite to Postgres<br/>Vehicle, PlanRequest, Plan")]
        cron["Re-plan job<br/>when next-day Agile lands ~16:00 UK"]
        solver["Solver (stretch)<br/>taper, shared fuse;<br/>sorted plan kept as baseline"]
    end

    octopus[("Octopus Agile API<br/>region from postcode")]
    neso[("Carbon Intensity API<br/>regional by outward postcode")]

    user --> cli --> core
    user --> ui --> api
    ha --> hook --> api
    api --> core
    cron --> api
    api --> db
    core --> octopus & neso
    core -.-> solver

    classDef todo stroke-dasharray: 5 5
    class cli,core,ui,api,hook,db,cron,solver todo
```

Planned order: the rates CLI over an importable planner core (milestone 1), `POST /plan` on the same core (2), the UI (3), the Home Assistant webhook (4), and only then the solver (5).
