# Git diff acceptance

Use temporary repositories with local commits and no remotes. Run the observable cases in both CLIs. Keep two-file behavior covered.

| ID | Setup | Required result |
| --- | --- | --- |
| G-01 | Historical and working spec identical; then improvements only | Exit 0 in both cases |
| G-02 | Drop `no_secrets_in_output` invariant from current file | Exit 1; names removed invariant |
| G-03 | Separately weaken risk, remove postcondition, BDD name, policy | Existing regressions still produce 1; no new diff semantics |
| G-04 | Bad ref, empty ref, range, raw tree/blob, option-like ref | Exit 2, readable revision/usage diagnostic, no stack trace |
| G-05 | Valid ref but historical path absent; current file absent/deleted | Exit 2, identifies failing source; never no-regression success |
| G-06 | Git not on PATH; outside repository; inaccessible cwd/path | Exit 2, actionable environment/path diagnostic |
| G-07 | Nested spec from repo root, then from nested cwd; spaces/non-ASCII filename; valid `..spec.yaml` filename | Same before/after content selected and correct result |
| G-08 | Absolute path inside repo; file outside repo; symlinked spec | Inside regular file accepted; outside and symlinked specs rejected |
| G-09 | Bad YAML/schema in historical content, then working content | Exit 2; distinguish historical revision/path from current file |
| G-10 | Dirty working spec differs from both HEAD and index | Compare with actual working bytes; HEAD, index, branch, and file contents unchanged |
| G-11 | Missing shallow-history ancestor, first-commit `HEAD~1`, linked Git worktree | Missing history returns 2 without fetch; linked worktree comparison works |
| G-12 | Two-file mode outside Git; missing/extra arguments; mixed Git/two-file arguments | Valid two-file mode unchanged; malformed command exits 2 |
| G-13 | Run same case table through Python and built TypeScript CLIs | Same exit/result category and named regression; formatting/color need not be byte-identical |

Also cover a branch, a commit SHA, and a tag resolving to a commit. Verify non-English Git errors do not change the top-level result category. Process/permission failure paths may use narrow mocks when filesystem permissions cannot be reliably reproduced by a privileged test runtime.

## Verification commands

From repository root with Python development dependencies installed:

```bash
python -m pytest adapters/python/tests/test_git_diff.py
npm test -- tests/cli.test.ts tests/diff.test.ts
npm run build
python -m pytest adapters/python/tests
npm test
```

Include `tests/gitDiff.test.ts` in the focused command if created. Record actual commands and results; do not infer parity from file existence or task checkboxes.

## PR recipe acceptance

Construct a local branch with two commits and a target branch that advances independently. Show why `HEAD~1` sees only the final commit, then demonstrate a merge-base comparison covering the branch's full spec change. Fail the recipe when the required base history is missing. Record that no checkout/fetch happens inside either Postulate command.
