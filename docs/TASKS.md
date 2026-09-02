# Postulate Task Index

This file is an index, not a combined plan and acceptance document. Change-specific implementation tasks live under `docs/plans/<change>/TASKS.md`; their definition of done lives separately in `ACCEPTANCE.md`.

## Shipped

Phases 0-7 of the original v0.1 build are complete:

- [x] project setup
- [x] spec schema and YAML loading
- [x] structural checks
- [x] codegen prompt
- [x] CI command
- [x] spec diff
- [x] known-invariant registry
- [x] worked TypeScript example and repository CI
- [x] test and schema hardening: [`plans/test-hardening/`](plans/test-hardening/)
- [x] python adapter milestones A–B: [`plans/python-adapter/`](plans/python-adapter/)

## Current

- [ ] Policy enforcement and init (Milestone C): [`plans/python-adapter/TASKS.md`](plans/python-adapter/TASKS.md)

Python adapter Milestones A–B are complete. Acceptance: [`plans/python-adapter/ACCEPTANCE.md`](plans/python-adapter/ACCEPTANCE.md).

## Planned

After Milestone C:

- [ ] property tests from named invariants
- [ ] architectural drift detection
- [ ] additional language adapters (Ruby, Go, Rust, …)

## Operating rules for coding agents

For every non-trivial implementation task:

```text
Read docs/ARCHITECTURE.md and the relevant plan folder before changing code.
Implement only the named task.
Do not add unrelated roadmap features.
Do not claim Postulate proves correctness.
Do not evaluate contract predicate strings as code unless a future approved design explicitly requires it.
Preserve the public CLI unless the plan explicitly changes it.
Add or update tests for changed behavior.
Run the acceptance checks named by the plan.
Stop when the named task and its acceptance checks are complete.
```
