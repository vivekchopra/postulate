# 0021. Keep Git diff local and make its inputs explicit

- Status: Accepted
- Date: 2026-09-02
- Refines: [0017](0017-git-aware-diff.md)
- Plan: [git-diff-hardening](../plans/git-diff-hardening/PLAN.md)

## Context

Both CLIs already support Git-aware diff. The missing work is reliable error handling and an unambiguous PR comparison, not another diff engine. Current loaders classify some errors by matching English Git stderr and do not normalize every process/filesystem error.

## Decision

Keep `postulate diff --git <ref> <spec-file>`. Resolve one commit-like revision, read the file at that commit, and compare it with the working-tree file at the same repository-relative path. Branches, commit SHAs, tags resolving to commits, and ancestry selectors such as `HEAD~1` are supported. Ranges, raw trees/blobs, empty refs, and leading-option forms are rejected as input errors.

Use local Git subprocesses with argument arrays and no shell. Resolve the revision once with `git rev-parse --verify --end-of-options <ref>^{commit}`. Use the resulting object ID when reading the blob. Classify errors by operation (repository discovery, revision resolution, blob read, working file read, parsing), not translated stderr. Retain useful Git details as secondary diagnostics.

Git mode discovers the repository from the invocation directory. Resolve the user-supplied path relative to that directory; require its canonical target to be a regular file inside that repository. Reject a symlinked spec rather than silently compare a symlink's historical text with its current target. Paths through a linked parent directory must still remain inside the repository, and the canonical relative path is used consistently. This removes accidental selection of a different repository through an outside path. Linked Git worktrees remain supported.

Keep exit codes 0 (no regression), 1 (regression), and 2 (usage/load/environment failure). Missing history or an absent historical file is an error, never an empty baseline. Two-file diff remains independent of Git and its containment rule.

No fetch, checkout, index update, automatic merge-base calculation, rename search, or remote API call occurs inside Postulate. PR automation supplies the intended base explicitly. For branch changes, a locally computed merge-base avoids treating changes on the base branch as PR removals.

## Consequences

A path in another repo is rejected when invoked from the current repo; users must change directory to the intended repo. Symlinked specs get an actionable failure. These bounded compatibility changes are documented.

New or renamed specs have no historical file at the same path and fail with code 2. Users review those cases explicitly or use two-file mode with an explicitly prepared prior file. Semantic scenario-body diffs and whole-repository spec discovery remain outside this change.

## Alternatives

- Leave stderr pattern matching: brittle across Git versions/locales.
- Add `--base`, `--head`, rename detection, and automatic fetch: larger scope with hidden state changes.
- Treat missing base as empty: can silently lose the invariant-removal guard.
- Compare against `origin/main` automatically: makes a project branch-name assumption and changes the requested command contract.
