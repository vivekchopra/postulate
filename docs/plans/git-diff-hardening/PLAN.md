# Git-aware diff hardening for PRs

Status: Implemented (G0–G3). `diff --git` is hardened in Python and TypeScript.

## Outcome

A PR check can compare a historical spec with the working-tree spec and fail when an invariant is removed, without manually checking out the old file. Existing happy-path functionality stays intact; environment, path, and revision failures become predictable.

```bash
postulate diff --git HEAD~1 specs/safety/postulate.yaml
```

Read [SPEC](SPEC.md), [ACCEPTANCE](ACCEPTANCE.md), and [ADR 0021](../../adr/0021-git-diff-input-boundary.md).

## Sequence

1. **G0: Baseline.** Run existing diff tests and identify uncovered failure paths in both CLIs.
2. **G1: Python boundary.** Normalize subprocess/filesystem failures, resolve a single commit, and validate working-tree paths.
3. **G2: TypeScript parity.** Implement equivalent behavior and exercise the same cases through its CLI.
4. **G3: PR use and documentation.** Document merge-base selection, shallow history, new/renamed specs, and the unchanged two-file fallback.

The work is independent of the pytest plan. Avoid mixing the two implementations into one large PR.

## Expected files

| Files | Change |
| --- | --- |
| `adapters/python/src/postulate/git_diff.py`, `cli.py` | Bounded Git loading and typed errors |
| `src/gitDiff.ts`, `src/index.ts` | Equivalent TypeScript behavior |
| `adapters/python/tests/test_git_diff.py` | Temporary-repository and process-error tests |
| `tests/cli.test.ts`, optional `tests/gitDiff.test.ts` | Same observable cases through TS entry point |
| `adapters/fixtures/` | Small shared before/after inputs if useful; no framework |
| Python README, root README, architecture, ADR index | Accurate PR commands and failure semantics |

## Out of scope

New diff classifications, BDD body semantics, mapping-removal diff rules, rename detection, remote fetching, checkout, staging, whole-repo spec discovery, multi-file reports, GitHub integration APIs, and consumer repository changes.

## Release boundary

This is a CLI hardening change. It does not change what counts as a spec regression. A missing historical file remains exit 2 and needs explicit review. Invocation now selects the repository and symlinked specs are rejected, as specified in ADR 0021.
