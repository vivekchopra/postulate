# 0007. Policies are declarations until enforced

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

Authors want to say `no_network_calls` / `no_db_writes` next to the contract. Enforcing that requires language-specific analysis.

## Decision

`policies` is an array of free strings. v0.1 stores them, diffs removals as regressions, and does not enforce them.

Enforcement is Phase 10: semgrep/eslint first, optional OPA/Rego later.

## Consequences

A spec can declare `no_network_calls` while the implementation calls the network. Reviewers must not treat policies as guarantees until enforcement ships. Removing a policy from a later spec is still a `diff` regression.

## Alternatives considered

- Omit policies until enforcement exists — would lose the declaration and the diff signal.
- Enforce in v0.1 with ad-hoc regex — too weak and language-specific to ship as the real check.
