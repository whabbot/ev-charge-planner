---
id: 7
title: Drop the index table from docs/decisions/README.md
date: 2026-10-28
status: accepted
---

# Drop the index table from docs/decisions/README.md

The index repeated each file's id, date, status and title, which the frontmatter already holds, and had to be edited alongside every new or superseded decision. The numbered filenames already give the order, so the README now only explains the format and the lint no longer requires a row per file.
