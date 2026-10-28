# Tickets

One ticket per milestone of the [build plan](../../smart-ev-charge-planner-build-plan.md). The build plan says what to build and takes precedence, and a ticket breaks one milestone into scope, acceptance criteria, verification and the docs it must update. When a ticket and the build plan disagree, fix the ticket.

Ship them in order (see [intent principle 6](../intent.md#principles)): each ticket depends on the one before it.

## Format

Name each file `mN-short-slug.md` and start it with this frontmatter:

```yaml
---
milestone: 1
title: One-line summary
status: todo          # todo | in-progress | done
depends_on: []        # milestone numbers that must be done first
---
```

Then an H1 matching `title` and these sections: Goal, Scope, Out of scope, Acceptance criteria, Verification, Docs to update. A ticket may add Open questions. Settle each one before or during the work, and record the answer in [decisions/](../decisions/README.md) if it is a product or project decision.

Update `status` in the same change that starts or finishes the work. When a large ticket is split, add the new files next to it as `mN-a-slug.md`, `mN-b-slug.md` and link them from the parent.
