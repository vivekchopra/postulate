# 0018. Pytest plugin for exercised spec mapping

- Status: Accepted
- Date: 2026-08-31
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

`verify` confirms mapped tests **exist** ([0016](0016-verify-command.md)). The next gap is mapped tests that exist but **never run** (skipped, deselected, or orphaned mappings after refactors). Roadmap "coverage measurement" means spec-to-test exercise, not line coverage.

## Decision

Ship a pytest entry point:

```text
pytest --postulate-spec path/to/postulate.yaml [--postulate-fail-on-warning]
```

After the test session:

1. Load the spec.
2. Read the set of node IDs that **ran** (passed, failed, or skipped — not deselected).
3. Compare against `test_mapping` for invariants (error) and BDD scenarios (warning).
4. Exit non-zero if required mappings were not exercised.

The plugin lives in the Python adapter package (`postulate_pytest` or `pytest11` entry point `postulate`).

This does not replace `verify`. Recommended CI order:

```text
postulate verify specs/foo/postulate.yaml
pytest --postulate-spec specs/foo/postulate.yaml
```

## Consequences

- Catches "test renamed but mapping left behind" only when the old ID is gone (verify) and "test exists but suite doesn't run it" (plugin).
- Full-suite runs may exercise mappings; targeted `pytest tests/test_foo.py` may not — document that CI should run the relevant test paths or the whole suite for spec-backed modules.
- Milestone B in [`plans/python-adapter/`](../plans/python-adapter/PLAN.md).

## Alternatives considered

- Fold exercised check into `verify` by running tests — slow, duplicates pytest, harder to compose.
- Parse coverage.py XML — indirect; node IDs are simpler.
- Require a Postulate-specific report file from pytest — extra plumbing for authors.
