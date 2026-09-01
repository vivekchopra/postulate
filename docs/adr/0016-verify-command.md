# 0016. verify command for mapped-test existence

- Status: Accepted
- Date: 2026-08-31
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

Structural `check` ensures every invariant has a `test_mapping` key but does not open test files ([0004](0004-structural-not-formal.md)). For Python consumers, the next failure mode is a mapping that points at a test that does not exist or was renamed.

Adding `--verify-tests` to `check` would change the meaning of an existing command for all consumers.

## Decision

Add a new CLI subcommand:

```text
postulate verify <spec-file> [--project-root PATH] [--pytest-args ...]
```

Behavior:

1. Run structural `check` on the loaded spec.
2. Collect pytest node IDs from `--project-root` (default `.`).
3. For every invariant (error) and BDD scenario name (warning) in `test_mapping`, resolve the locator against collected nodes.
4. Exit `1` if structural errors exist or any **invariant** mapping is unresolved.
5. Exit `1` on unresolved BDD mappings when `--fail-on-warnings` is set (mirrors `ci` semantics).
6. Exit `2` on spec load failure or pytest collection failure.

`check` and `ci` remain structural-only. `verify` is the Python adapter's bridge to pytest.

The TypeScript CLI may gain an analogous `verify` later (vitest/jest); it is not required for Milestone A.

## Consequences

- CI for Python projects should run `postulate verify` after `postulate check` or instead of `check` when pytest is available.
- Collection failures (broken test suite) block verify; that is intentional.
- Verify does not prove tests pass or cover the behavior; only that mapped node IDs exist.

## Alternatives considered

- Fold into `check` by default — breaks offline/structural-only workflows and the TS/Python parity story.
- Silent skip when pytest missing — hides misconfiguration; fail loudly instead.
- Parse test files with regex — brittle vs pytest's own collection.
