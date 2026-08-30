# 0009. Diff compares two file paths

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

CI needs to know if a PR dropped an invariant or weakened risk. Git integration is useful but couples the tool to a repo layout.

## Decision

`postulate diff` takes two spec file paths. It compares risk, invariant names, postcondition strings, BDD scenario names, and policy names. Risk lowering is a regression; raising is an improvement.

Git refs (`HEAD~1`) are Phase 13.

## Consequences

CI jobs that want a before/after must materialize two files. Renaming a postcondition counts as remove + add.

## Alternatives considered

- Git-aware from day one — extra failure modes (no repo, missing history) before the core diff is proven.
- Deep-diff of BDD bodies — noisier; v0.1 diffs names only.
