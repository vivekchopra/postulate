# 0011. Risk drives required invariants and correctness argument

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

Not every feature needs the same rigor. A thin spec for a low-risk helper is fine; a high-risk billing function without invariants is not.

## Decision

`risk` is `low | medium | high | critical`, default `medium`.

- `high` or `critical` **errors** if `invariants` is empty.
- `high` or `critical` **warns** if `correctness_argument` is missing.
- Thin contracts (preconditions + postconditions < 3) warn at every risk level.

## Consequences

Authors can ship a low-risk spec with no invariants. Raising risk later requires adding them. Weakening risk is a `diff` regression ([0009](0009-diff-two-files.md)).

## Alternatives considered

- Same rules for every spec — over-constrains low-risk work.
- Require correctness_argument as an error in v0.1 — too heavy; warning plus `--fail-on-warnings` is the strict gate.
