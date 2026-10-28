---
id: 4
title: Remove the pre-plan rates CLI and rebuild milestone 1 from the build plan
date: 2026-10-28
status: accepted
supersedes: 2
---

# Remove the pre-plan rates CLI and rebuild milestone 1 from the build plan

Removed `quick_oneshots/rates_cli.py`. It was written before the build plan and fixed behavior the plan contradicts: the Agile price region ignored the postcode, energy was counted in whole half-hours (overstating kWh and £, and skipping a usable part slot before departure while crediting the part-gone current slot in full), and missing carbon data was summed as zero.

The build plan takes precedence. Milestone 1 will be rebuilt from it, planning by energy so a partial first or last slot is allowed.
