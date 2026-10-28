# Decisions

One file per product or project decision, numbered in the order they were made. The files are the record; there is no index to keep in step. [intent.md](../intent.md) holds the goals, principles and non-goals that these decisions serve.

## Adding a decision

Copy the next number, `NNNN-short-slug.md`, and start it with this frontmatter:

```yaml
---
id: 5                 # matches the NNNN filename prefix
title: One-line summary
date: 2026-10-28      # YYYY-MM-DD, the day it was decided
status: accepted      # proposed | accepted | superseded
supersedes: 4         # optional, id of the decision this replaces
superseded_by: 6      # required when status is superseded
---
```

Then an H1 matching `title` and a short body: what was decided and why. Never rewrite an old decision to change it. Add a new one that supersedes it, and set the old one's `status` and `superseded_by`.

