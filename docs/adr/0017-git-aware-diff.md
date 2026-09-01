# 0017. Git-aware spec diff

- Status: Accepted
- Date: 2026-08-31
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

`postulate diff` compares two file paths ([0009](0009-diff-two-files.md)). PR workflows need to compare the spec at `HEAD` against `HEAD~1` (or another ref) without manually materializing the old file.

## Decision

Extend `diff` in **both** CLIs (TypeScript and Python) with optional git mode:

```text
postulate diff --git <ref> <spec-file>
```

- `<ref>` is any single git revision resolvable by `git show <ref>:<spec-path>` (for example `HEAD~1`, `main`, a commit SHA).
- `<spec-file>` is the path in the working tree; the same relative path is used inside the repo at `<ref>`.
- Compare loaded spec at `<ref>` (before) against loaded spec at working tree path (after).
- If the spec did not exist at `<ref>`, treat that as a load failure with a clear message.
- Two-path mode `postulate diff <before> <after>` remains unchanged.

Implementation uses local `git` subprocess calls. No network fetch.

## Consequences

- PR CI can run `postulate diff --git origin/master specs/safety/postulate.yaml` when the base branch is fetched.
- Requires a git working tree; bare checkouts without git history fail with a clear error.
- Milestone B of [`plans/python-adapter/`](../plans/python-adapter/PLAN.md); not required for Milestone A.

## Alternatives considered

- Only support two paths and let CI check out base — works but awkward in GitHub Actions.
- `postulate diff HEAD~1` with implicit path — too magic; explicit spec path is clearer.
- Use libgit2 bindings — unnecessary dependency for `git show`.
