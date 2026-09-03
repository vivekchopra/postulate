# Git-aware diff contract

Status: Implemented (see [ADR 0021](../../adr/0021-git-diff-input-boundary.md)).

## Public behavior

```bash
postulate diff --git HEAD~1 specs/safety/postulate.yaml
postulate diff before.yaml after.yaml
```

Git mode takes one revision and one working-tree spec path. Two-file mode takes two paths. Missing/extra operands, an empty ref, ranges, option-like refs, and a revision that does not resolve to a commit are usage/load failures. No new flags are required.

The historical file is "before". The current file on disk, including uncommitted changes, is "after". This is not an index comparison or automatically a HEAD comparison. A supplied ref is used exactly as specified, never silently replaced by a merge-base.

## Loading steps

1. Discover the Git worktree from invocation cwd, including when cwd is a subdirectory or a linked worktree. Outside a repository, report a readable error.
2. Resolve the input spec path relative to cwd. Require a readable regular file whose canonical target remains within the discovered repository. Reject a symlinked spec. Keep spaces and non-ASCII characters intact. Repository containment must use path components, not a naive prefix such as `startsWith("..")` that rejects valid names like `..spec.yaml`.
3. Resolve one commit with `git rev-parse --verify --end-of-options <ref>^{commit}`. Use the returned object ID for subsequent reads. Reject invalid or absent history without fetching.
4. Read the same repository-relative path from that commit as raw blob content. Do not apply external diff/text conversion drivers. An absent or non-blob historical path is a load error.
5. Parse historical and current content with existing spec loaders. Diagnostics distinguish the revision/path source from the working file.
6. Call the existing `diff_specs` / `diffSpecs` comparator unchanged.

Use argument arrays with shell execution disabled. Handle Git spawn failures, missing executable, permissions, invalid cwd, path resolution, blob read, encoding, and YAML/schema errors at the boundary. Error messages need stable categories and source paths; exact Git stderr text is not part of the compatibility contract. Git itself owns object-ID format; do not assume a 40-character SHA.

## Results

| Condition | Exit |
| --- | --- |
| Identical spec, improvements only, or no classified regression | 0 |
| Removed invariant, removed postcondition, removed BDD name, removed policy, or weaker risk | 1 |
| Invalid invocation, Git unavailable, outside repo, unreadable path, invalid ref, absent historical file, invalid YAML/schema | 2 |

Retain existing material-diff messages. Keep errors readable without raw stack traces. Do not present missing history as no changes. Two-file mode requires neither Git nor repository containment and keeps its existing behavior.

## Repository state

The command must not fetch, checkout, write the spec, change branches, modify index entries, or change HEAD. Tests compare HEAD, index/tree state, and working spec bytes before and after invocation. Fixture setup may commit locally; no remote is required.

## PR comparison

`HEAD~1` answers "what changed since the previous commit?" It is not a complete multi-commit PR baseline. To compare branch changes, prepare the local history outside Postulate and supply the merge-base explicitly:

```bash
# Run from the consumer repository with origin/main already available.
# Replace origin/main with the actual target branch ref.
set -e
base_sha=$(git merge-base HEAD origin/main)
postulate diff --git "$base_sha" specs/safety/postulate.yaml
```

If merge-base fails, stop that check; do not proceed with an empty ref. CI should use a fail-fast shell. For GitHub PR jobs comparing branch changes, check out the PR head SHA with full history, make the target commit available, and calculate the merge-base with that target. A default synthetic merge checkout answers a different question. Record which baseline the job uses.

A newly added or renamed spec returns 2 when that path did not exist at the base. A deleted working spec also returns 2. CI must surface those failures for review rather than skipping all missing files. Automatic rename matching is out of scope.
