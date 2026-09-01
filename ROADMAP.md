# Roadmap

Planned features. Sequencing lives in [docs/PLAN.md](./docs/PLAN.md); checkboxes and Cursor task prompts live in [docs/TASKS.md](./docs/TASKS.md). Locked design choices live in [docs/adr/](./docs/adr/README.md).

## Python adapter (in progress)

Native Python package (`pip install postulate`) with CLI parity, `verify` (pytest collection resolves `test_mapping`), pytest plugin for exercised mappings, and `diff --git`. First consumer: webcheck-api.

Plan: [docs/plans/python-adapter/](./docs/plans/python-adapter/PLAN.md). ADRs: [0014](./docs/adr/0014-python-adapter-package.md)–[0018](./docs/adr/0018-pytest-plugin-exercised-mapping.md).

## Property tests from named invariants

Named invariants such as `does_not_mutate_input` should generate property tests automatically.

Instead of writing the property manually, authors declare the invariant in the spec and Postulate generates the corresponding test scaffold.

The implementation will likely build on libraries such as fast-check.

## Policy enforcement

Policies like `no_network_calls` are declarations only today.

The plan is to start with semgrep and eslint-based checks, then add optional OPA/Rego support for teams that want policy-as-code over structured analysis results.

The goal is for policy violations to fail CI before code is merged or deployed.

## Coverage measurement

Compare declared invariants and BDD scenarios against the tests that actually ran.

**Partially addressed by the Python adapter** ([pytest plugin](./docs/plans/python-adapter/SPEC.md), ADR [0018](./docs/adr/0018-pytest-plugin-exercised-mapping.md)): spec-to-test exercise, not line coverage.

Remaining: generalize beyond pytest; optional integration with coverage.py later.

## Architectural drift detection

Compare the current codebase against structural expectations declared in the spec, so refactors that quietly move boundaries between modules, layers, or services show up as explicit drift rather than silently passing CI.

## Git-aware diff

`postulate diff` currently compares two file paths.

**Planned in Python adapter Milestone B** ([ADR 0017](./docs/adr/0017-git-aware-diff.md)): `postulate diff --git <ref> <spec-file>`.

## Multi-language adapters

The spec format is plain YAML, so any language can produce one.

The current implementation is TypeScript-first. **Python is the first adapter** ([ADR 0014](./docs/adr/0014-python-adapter-package.md)). Ruby, Go, Rust, and others follow the same pattern after Python Milestones A–B land.
