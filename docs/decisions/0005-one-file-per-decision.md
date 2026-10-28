---
id: 5
title: Record decisions as one file each in docs/decisions
date: 2026-10-28
status: accepted
---

# Record decisions as one file each in docs/decisions

The decision log moved out of `docs/intent.md` into `docs/decisions/`, one file per decision with frontmatter (id, title, date, status, and supersedes or superseded_by links). Intent now holds only what must stay true. Decisions get their own history, can be superseded without rewriting, and are linted for structure.
