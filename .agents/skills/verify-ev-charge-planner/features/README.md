# EV Charge Planner verification map

This directory is the maintained source for verifying the user-facing behavior of the Smart EV Charge Planner. Read this index before driving the app, then use the matching feature file as the recipe.

## Baseline preconditions

- Run `eval "$(.agents/skills/verify-ev-charge-planner/scripts/launch.sh)"` once per run so `VERIFY_RUN_ID` is set.
- Require `.agents/skills/verify-ev-charge-planner/scripts/doctor.sh` to print only `ok:` lines, including both API reachability checks.
- Set `V=.agents/skills/verify-ev-charge-planner/scripts` in the shell. Recipes use `$V/drive.sh`.
- Network access to `api.octopus.energy` and `api.carbonintensity.org.uk` is required. There is no offline mode.

## Driving conventions

- Every action goes through `$V/drive.sh <feature-id>/<step> -- <command> [args...]`. Never import or call planner functions directly.
- Treat every command as literal. Keep quoted values and flags unchanged.
- Assert on the stable output handles a feature file names and on the recorded exit code, not on line positions.
- Live prices change daily. Assert on relationships (counts, ordering, cost plan cheaper than or equal to baseline), not on specific pence values, unless the planning time is pinned.

## Proof and skip reporting

- Proof is the `.cmd`, `.stdout`, `.stderr` and `.exit` files `drive.sh` writes, named by feature ID and step.
- Record the feature ID and entry point with every artifact. The `<feature-id>/<step>` label does this.
- Report an unreachable path with the attempted command and the unmet precondition, such as an API down or the Agile window not yet published.
- Do not report a skipped entry point as verified through a different path.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing the user-visible behavior. It then uses exactly four H2 sections in this order.

1. `Sub-features` lists short IDs with one line for each behavior.
2. `How to get to it (user POV)` lists every user entry point.
3. `Driving it with drive.sh` starts with `Preconditions:` and uses labeled bullets that pair each user action with an exact command and observable result.
4. `Gotchas` lists traps that can waste or invalidate a verification run.

Keep implementation details out of the map. Name only user paths, stable handles, required state, commands, and observable proof. `scripts/lint.sh` enforces this structure.

## Features

None yet. The pre-plan rates CLI was removed, and milestone 1 and `POST /plan` will add the first feature files. Link each new file from this section.
