# Git diff hardening — implementation notes

## G0: Establish baseline

**Date:** 2026-09-02  
**Planning baseline commit:** `89d0048` (loaders unchanged in intent since Milestone B at `387f5f9`)  
**Branch:** `cursor/pytest-coverage-p0-baseline` (local; uncommitted pytest-coverage + G0 work)  
**Scope:** G0 only — baseline tests and notes; no production code changes.

### Git status at start

Local work includes completed pytest-coverage P0–P3 (uncommitted) plus this G0 baseline. Preserved unrelated planning overlay files remain unstaged.

### Implementation vs review baseline

Compared both loaders to [python-testing-review.md](../python-testing-review.md) and [ADR 0021](../../adr/0021-git-diff-input-boundary.md). **Comparator (`diff_specs` / `diffSpecs`) unchanged** — G-01–G-03 behavior still covered by existing happy-path tests.

| Gap | Review / ADR finding | Python evidence | TypeScript evidence |
| --- | --- | --- | --- |
| G-06 Missing Git executable | `_run_git` lets `FileNotFoundError` escape | CLI exit **1**; Typer surfaces `[Errno 2] No such file or directory: 'git'` | CLI exit **2**, but message reads `Not a git repository: git rev-parse failed` (spawn failure misclassified) |
| G-05 Missing working-tree file | TS `realpathSync` outside normalized boundary | CLI exit **2**; `Spec file not found: …` after historical load succeeds | CLI exit **1**; uncaught `ENOENT` from `realpathSync` in `repoRelativeSpecPath` before `loadSpec` |
| English stderr fragments | Both classify ref/path errors via stderr substrings | `git_diff.py` lines 49–62 | `gitDiff.ts` lines 48–58 |
| No `rev-parse --verify` commit resolution | ADR 0021 step 3 | Uses `git show ref:path` directly | Same |

**Confirmed unchanged (G0 scope):**

- Regression detection: dropped invariant → exit 1 (`test_git_diff.py`, `cli.test.ts` git case).
- Two-file diff mode independent of Git (`test_cli_two_file_diff_still_works`, `cli.test.ts` two-file case).
- Bad ref → exit 2 with `Git ref not found` (both CLIs).

### Environment

| Component | Version |
| --- | --- |
| Python | 3.11.14 (`.venv-p0`) |
| pytest | 9.1.1 |
| Node | v24.14.1 |
| vitest | 2.1.9 |
| Git | system `git` (available on PATH for fixture setup) |

Platform: darwin (macOS).

### Commands and results

#### Existing baseline tests (must pass)

```bash
cd adapters/python
.venv-p0/bin/python -m pytest tests/test_git_diff.py -v

cd ../..
npm test -- tests/cli.test.ts tests/diff.test.ts
npm run build
```

| Suite | Result |
| --- | --- |
| `tests/test_git_diff.py` | **8 passed** |
| `tests/cli.test.ts` + `tests/diff.test.ts` | **16 passed** (8 + 8) |
| `npm run build` | **Success** |

#### G0 regression suites (intended behavior; expected failures until G1/G2)

```bash
cd adapters/python
.venv-p0/bin/python -m pytest tests/test_git_diff_regressions.py -v

cd ../..
npm test -- tests/gitDiff.baseline.test.ts
```

| Test | Acceptance | Expected | Actual (baseline) |
| --- | --- | --- | --- |
| `test_g06_python_missing_git_executable_must_exit_two_with_readable_error` | G-06 | exit 2, no traceback | exit **1**, errno message |
| `test_g05_python_missing_working_tree_file_must_exit_two` | G-05 | exit 2 | exit **2** ✓ (passes — documents Python already correct) |
| TS `G-05: missing working-tree spec…` | G-05 | exit 2, readable | exit **1**, `lstat` stack |
| TS `G-06: missing Git executable…` | G-06 | exit 2, actionable | exit **2** ✓ but misleading “Not a git repository” wording |

Run baseline adapter tests separately during G0–G2:

```bash
pytest tests/ -m "not g0_regression"
pytest tests/ -m g0_regression
```

Full Python adapter suite (including pytest-coverage work): **76 passed** when run without g0 regressions filter at time of G0 (69 core + integration; g0 adds 1 passing + 1 failing Python regression).

### Files changed (G0)

| File | Change |
| --- | --- |
| `adapters/python/tests/test_git_diff_regressions.py` | New — G-05/G-06 regressions |
| `tests/gitDiff.baseline.test.ts` | New — TS G-05/G-06 regressions |
| `adapters/python/pyproject.toml` | Register `g0_regression` marker |
| `docs/plans/git-diff-hardening/IMPLEMENTATION_NOTES.md` | This file |
| `docs/plans/git-diff-hardening/TASKS.md` | G0 checkboxes |

**Not changed:** `git_diff.py`, `gitDiff.ts`, comparators, ADR statuses.

### Python vs TypeScript difference summary (G0 finding)

| Scenario | Python CLI | TypeScript CLI |
| --- | --- | --- |
| Working spec deleted before `diff --git` | Exit **2**, `Spec file not found` | Exit **1**, uncaught filesystem error in `repoRelativeSpecPath` |
| `git` not on `PATH` | Exit **1**, uncaught spawn error | Exit **2**, categorized as not-a-repository |

G1 should normalize Python spawn failures. G2 should match Python load order and boundary handling, including working-file reads before/alongside path canonicalization per ADR 0021.

### Next group

**G1:** Harden Python Git loading (`git_diff.py`, `cli.py`).
