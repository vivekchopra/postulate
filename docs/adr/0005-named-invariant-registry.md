# 0005. Named invariant registry; custom names allowed

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

Some properties recur (`does_not_mutate_input`, `pure`, `idempotent`). Domain properties do not. A closed list would reject real specs; an unrecognized list would never grow generators.

## Decision

Ship a small registry of well-known names in `src/invariants.ts`. Custom names are valid. `check` reports recognised vs custom as info only. Both kinds require `test_mapping` ([0006](0006-test-mapping-enforcement.md)).

`deterministic_output` and `deterministic_for_same_input` are both recognised and mean the same thing.

v0.1 does not attach executable semantics or generate tests.

## Consequences

The registry can grow and later pair with property-test generators without changing the YAML shape. Custom invariants stay author-owned.

## Alternatives considered

- Closed enum of invariant names — rejects domain rules.
- No registry — loses a hook for later generation and shared vocabulary.
- Generate tests in v0.1 — skipped; that is Phase 9.
