# Git diff hardening tasks

All work is pending. Acceptance IDs refer to [ACCEPTANCE.md](ACCEPTANCE.md).

## G0. Establish baseline

- [x] Read ADRs 0009/0017 and proposed 0021; inspect both loaders and CLI handlers.
- [x] Run existing Python and TypeScript diff tests; record environment/results.
- [x] Add regressions for missing Git and missing working-tree file; document the current Python/TypeScript difference.
- [x] Confirm current comparator classifications; do not change them.

## G1. Harden Python Git loading

- [ ] Discover repository from invocation cwd and validate file containment/type.
- [ ] Resolve one commit revision before loading the blob; keep the resolved object ID stable across operations.
- [ ] Normalize subprocess, path, read, and parse failures into readable CLI exit 2 diagnostics.
- [ ] Remove reliance on English Git stderr for top-level error classification.
- [ ] Test no-regression, dropped invariant, bad ref, missing file/history, nested cwd, spaces, linked worktree, and state preservation.

Acceptance: G-01 through G-12 for Python.

## G2. Match TypeScript behavior

- [ ] Implement the same input/path/revision boundaries in `src/gitDiff.ts` and CLI error handling.
- [ ] Use shared small spec inputs or duplicate explicit fixtures to exercise the same CLI outcomes; avoid a parity framework.
- [ ] Test argument-count behavior, empty refs, missing executable, containment, and filesystem failures.
- [ ] Run all existing two-file diff tests unchanged.

Acceptance: G-01 through G-12 for TypeScript; G-13 parity.

## G3. Document and finish

- [ ] Add a consumer recipe distinguishing previous-commit, target-tip, and merge-base comparisons.
- [ ] State history prerequisites, no implicit fetch, same-path limitation, and handling for new/renamed/deleted specs.
- [ ] Ensure recipes run on spec changes as well as code/test changes; no `|| true` or equivalent suppression.
- [ ] Update current architecture and consumer README with implemented behavior; accept ADR 0021 with the change.
- [ ] Run final gates; record commands, results, unresolved items, and the tested Git/Python/Node versions.
