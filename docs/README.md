# Docs

Postulate separates current architecture, durable design decisions, change-specific plans, tasks, and acceptance criteria so each artifact has one job.

| Path | Purpose |
| --- | --- |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Current system architecture only |
| [`SPEC.md`](SPEC.md) | Product and technical source of truth |
| [`PLAN.md`](PLAN.md) | Project-level build order; not a change-specific implementation plan |
| [`TASKS.md`](TASKS.md) | Index of shipped, current, and future work |
| [`plans/`](plans/) | Change-specific plans, specs, tasks, acceptance criteria, and agent prompts |
| [`plans/python-adapter/`](plans/python-adapter/PLAN.md) | **Current:** Python adapter + pytest integration (webcheck-api pilot) |
| [`adr/`](adr/README.md) | Architecture Decision Records: why durable design choices were made |
| [`adr/template.md`](adr/template.md) | Copy this when recording a new decision |
| [`framework.md`](framework.md) | Short layer overview of the Postulate workflow |
| [`pr-template.md`](pr-template.md) | PR checklist for spec-backed changes |
| [`CURSOR_PROMPTS.md`](CURSOR_PROMPTS.md) | Earlier project-level Cursor prompts; new work should prefer plan-local prompts |

## Which document should change?

Use `ARCHITECTURE.md` when the current structure of the system changes.

Use an ADR when a durable architectural or product design choice is made and the reason needs to survive the implementation branch.

For a change larger than a small fix, create a folder under `plans/` containing:

```text
plans/<change>/
├── PLAN.md
├── SPEC.md
├── TASKS.md
├── ACCEPTANCE.md
└── CURSOR_PROMPTS.md
```

`PLAN.md` defines the scope and boundaries. `TASKS.md` contains only verifiable work items. `ACCEPTANCE.md` defines done independently of the implementation. Agent prompts should name the specific task to execute, what is out of scope, what checks to run, and where to stop.

The root [`ROADMAP.md`](../ROADMAP.md) remains the public planned-feature list.

New locked design changes belong in `docs/adr/` using the next available ADR id (**0020**).
