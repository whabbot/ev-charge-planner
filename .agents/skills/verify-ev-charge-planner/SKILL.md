---
name: verify-ev-charge-planner
description: Drive the Smart EV Charge Planner the way a user does and capture proof. There is no user-facing surface yet (the pre-plan rates CLI was removed); this skill holds the launch, doctor, drive and evidence conventions that milestone 1 and `POST /plan` will plug into. Use to prove a change to planning, slot picking, rate/carbon fetching or plan output actually works, before claiming it does.
---

# Verify EV Charge Planner

There is no user-facing surface to drive yet. The earlier rates CLI predated the build plan and was removed (see `docs/decisions/0004-remove-pre-plan-rates-cli.md`). Milestone 1 and then `POST /plan` will be the first surfaces (see `docs/architecture.md`). When one lands, add its feature files and extend this skill rather than writing a second one.

Until then you can launch, run doctor and clean up, but there is nothing to verify. Say so rather than claiming a behavior is verified.

All helpers live in `.agents/skills/verify-ev-charge-planner/scripts/` and run from any cwd. Below, `$V` means that directory.

## Launch

```bash
V=.agents/skills/verify-ev-charge-planner/scripts
eval "$($V/launch.sh)"        # uv sync once, exports VERIFY_RUN_ID
```

Ready when stderr prints `ready: run <id>, evidence in <path>`. Launch syncs the uv-managed Python (>= 3.12) and creates `.verify/evidence/$VERIFY_RUN_ID/` with a `REVISION` file (commit plus dirty files).

Runs are isolated by `VERIFY_RUN_ID`. Concurrent runs in the same checkout are safe as long as the surface under test is stateless.

## Doctor

```bash
$V/doctor.sh
```

Read-only. It checks uv, Python >= 3.12, the revision, that both the Octopus and Carbon Intensity APIs answer 200, and that the run's evidence dir exists. Run it first, and again whenever output looks wrong. If an API check fails, stop and report it. Do not paper over it with mocks. When a surface lands, add a check that it starts.

## Drive

```bash
$V/drive.sh <feature-id>/<step> -- <command> [args...]
```

This runs one command from the repo root exactly as a user would and records `.cmd`, `.stdout`, `.stderr` and `.exit` under `.verify/evidence/$VERIFY_RUN_ID/<feature-id>/<step>.*`. It always exits 0. Assert on the printed `--- exit N` line or the `.exit` file.

Pick the recipe from the feature map: [`features/README.md`](features/README.md). Drive every entry point the relevant feature lists, not just the convenient one. Assert on stable output handles named in the feature file, never on line numbers.

## Evidence

Evidence lives in `.verify/evidence/$VERIFY_RUN_ID/` (gitignored) and survives cleanup.

Proof standards:

- Exercise the real user path through `drive.sh`. Never import functions and call them, and never stub the network. The production boundary is the live API.
- A proof shows the command, stdout, stderr and exit code. `drive.sh` records all four.
- Prices and forecasts change every day. For a claim that must be reproducible (for example, a before/after comparison), pin the planning time to a past instant and use a departure inside the published window.
- Check the numbers, not only the labels. Delivered energy must meet the need without overshooting it, and the cost plan's £ must not exceed the charge-now baseline's.
- When a dry or partial path is the only option, say what it skipped.

## Cleanup

```bash
$V/cleanup.sh
```

This removes `.verify/tmp/$VERIFY_RUN_ID` only. Evidence is never deleted. Then `ls .verify/evidence/$VERIFY_RUN_ID` to confirm the proof is still there.

## Maintenance

The feature map is the maintained verification source. When a user-facing behavior, flag, output label or entry point changes, update the matching file in `features/` in the same change (run `/maintain-verification-skill` if available). `scripts/lint.sh` at the repo root checks the map's structure.
