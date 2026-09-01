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

## Current

- [ ] Test and schema hardening: [`plans/test-hardening/TASKS.md`](plans/test-hardening/TASKS.md)

The acceptance criteria for this work are intentionally separate: [`plans/test-hardening/ACCEPTANCE.md`](plans/test-hardening/ACCEPTANCE.md).

## Planned

The product roadmap remains in [`ROADMAP.md`](../ROADMAP.md). Create a plan folder before implementing a substantial roadmap item.

Current roadmap sequence after hardening:

- [ ] property tests from named invariants
- [ ] policy enforcement
- [ ] coverage measurement
- [ ] architectural drift detection
- [ ] git-aware diff
- [ ] multi-language adapters

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
