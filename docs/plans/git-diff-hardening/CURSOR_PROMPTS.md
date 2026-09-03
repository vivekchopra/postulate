# Bounded coding-agent prompts

Use one prompt at a time. This work does not require the pytest plan to have landed.

## Prompt 0: Baseline (G0)

Read docs/ARCHITECTURE.md, docs/plans/python-testing-review.md, this folder's PLAN.md, SPEC.md, TASKS.md, ACCEPTANCE.md, and ADRs 0009, 0017, 0021. Inspect the existing implementations; do not rebuild Git mode. Execute only G0. State planned files and checks first. Add narrow regressions for uncovered loader failures, record expected and unrelated failures, and stop before implementation.

## Prompt 1: Python boundary (G1)

Implement only G1 against G-01 through G-12. Keep the comparator and public command syntax unchanged. Resolve the repository from invocation cwd, canonicalize contained file paths, resolve a commit once, and convert boundary failures into readable exit 2 errors. Use Git argument arrays without a shell. No fetch, checkout, rename handling, or semantic diff work. Run focused Python Git tests, report results and compatibility changes, then stop.

## Prompt 2: TypeScript parity (G2)

Read the accepted Python behavior and ADR 0021. Implement only G2. Match exit categories and input boundaries, including spawn failures and missing current files. Preserve the existing comparator and two-file command. Exercise the same temporary-repo cases through the TS CLI. Run focused tests and build, report parity gaps with concrete commands, and stop.

## Prompt 3: PR recipe and completion (G3)

Implement only G3. Document previous-commit versus merge-base comparison using explicit local refs and fail-fast commands. Explain full-history requirements, PR-head versus synthetic merge checkout, and missing/new/renamed/deleted spec handling. Do not modify webcheck or auto-fetch inside Postulate. Update architecture and accept ADR 0021 with implemented behavior. Run final acceptance gates and record evidence. Stop with changed files, results, and unresolved acceptance items.

## Final review prompt

Review both implementations against each acceptance ID. Try missing history, missing Git, mixed operands, nested paths, linked worktrees, and dirty specs. Confirm neither command changes repository state or silently uses an empty baseline. Check that all examples name their comparison baseline. Report concrete defects; do not add broader Git or semantic-diff features.
