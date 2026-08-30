# 0004. Structural checks, not formal verification

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

The vocabulary (preconditions, postconditions, invariants) comes from correctness-oriented programming. Teams might expect Postulate to prove those claims.

## Decision

v0.1 checks structure, not semantics. Contract strings are not evaluated. `test_mapping` is not opened. Policies are not executed. Postulate is not a theorem prover and does not guarantee correctness.

It externalizes intent, enforces a minimum of discipline at CI time, and flags spec weakening.

## Consequences

A spec can pass `check` while the implementation is wrong. Reviewers and tests remain responsible for meaning. Formal verification tools are out of scope unless a later ADR supersedes this.

## Alternatives considered

- Embed a theorem prover — out of scope and would position the product dishonestly.
- Interpret contract strings as executable predicates — brittle, language-specific, and easy to get wrong in v0.1.
