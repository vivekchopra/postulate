# 0015. Pytest locator grammar for test_mapping

- Status: Accepted
- Date: 2026-08-31
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

`test_mapping` values are opaque strings today ([0006](0006-test-mapping-enforcement.md)). A Python adapter that cannot resolve them adds no value over YAML linting.

The TypeScript example uses `"lateFee.test.ts > test_name"`. Python/pytest uses `path::nodeid` (for example `tests/test_safety.py::test_normalize_domain_from_url`).

## Decision

The Python adapter recognizes **pytest node IDs** as the canonical `test_mapping` target format.

Accepted forms:

```text
tests/test_safety.py::test_normalize_domain_from_url
tests/test_safety.py::TestSafety::test_normalize_domain_from_url
tests/test_safety.py::test_normalize_domain_from_url[param]
```

Rules:

- Path is relative to the **project root** passed to `verify` (default: current working directory).
- Separator is `::` (pytest convention).
- Optional parametrized suffix `[...]` is allowed.
- The TypeScript `file > name` form remains valid for TypeScript examples; the Python adapter does not require it.

Resolution uses **pytest collection only** (`pytest --collect-only`), not execution. Collection must succeed without network access when the project's tests are written to ADR/webcheck offline-test conventions.

## Consequences

- Authors must write locators pytest can collect.
- `verify` errors when a mapped node ID is missing from collection output.
- Parametrized tests map to the parametrized node ID or the base name per documented rules in the plan spec.
- TypeScript consumers keep their existing locator style until a future TS adapter adds vitest/jest resolution.

## Alternatives considered

- Keep locators fully opaque in Python too — does not unlock webcheck-api.
- Invent a Postulate-specific locator (`module:qualname`) — extra learning cost; pytest already has one.
- Execute tests during verify — slower, flaky, and mixes concerns; execution belongs in `pytest` + optional plugin.
