# 0006. Every invariant must map to a test

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

A YAML list of invariants that nothing exercises is theater. The cheapest CI-detectable lie is "named in the spec, absent from tests."

## Decision

`check` errors if any entry in `invariants` is missing from `test_mapping`. BDD scenario names without a mapping are warnings, because some frameworks treat the scenario itself as the test.

`test_mapping` values are opaque strings. v0.1 does not parse them or run the referenced tests.

## Consequences

Authors must name a test for every invariant before `check` passes. Mapping to a test that does not exist or does not run is still possible; coverage measurement is later (Phase 11).

## Alternatives considered

- Warning for unmapped invariants — too easy to ignore; this is the core enforcement rule.
- Require opening/running the mapped test in v0.1 — couples Postulate to a test runner too early.
- Require mappings for BDD names as errors — too strict for v0.1; warning only.
