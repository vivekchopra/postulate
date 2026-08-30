# Roadmap

Planned features. Sequencing lives in [docs/PLAN.md](./docs/PLAN.md); checkboxes and Cursor task prompts live in [docs/TASKS.md](./docs/TASKS.md). Locked design choices live in [docs/adr/](./docs/adr/README.md).

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

The goal is to catch cases where a behavior exists in the spec but is no longer exercised by the test suite.

## Architectural drift detection

Compare the current codebase against structural expectations declared in the spec, so refactors that quietly move boundaries between modules, layers, or services show up as explicit drift rather than silently passing CI.

## Git-aware diff

`postulate diff` currently compares two file paths.

A future version will diff directly against `HEAD~1` or another git reference so CI jobs do not need a manual checkout of the previous spec.

## Multi-language adapters

The spec format is plain YAML, so any language can produce one.

The current implementation is TypeScript-first. The long-term plan is to keep the spec format language-neutral while adding language-specific adapters (for Python, Ruby, Go, Rust, and others) for test discovery, test generation, and policy checks.
