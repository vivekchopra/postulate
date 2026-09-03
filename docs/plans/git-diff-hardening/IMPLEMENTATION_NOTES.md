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

---

## G1: Harden Python Git loading

**Date:** 2026-09-03  
**Branch:** `cursor/pytest-coverage-p0-baseline`  
**Scope:** Python `git_diff.py` + `tests/test_git_diff.py` only (no TypeScript production changes).

### Key changes

| Behavior | Implementation |
| --- | --- |
| Discover repo from invocation cwd | `find_git_root(cwd)` via `rev-parse --show-toplevel` |
| Validate working file | Reject symlinks; require regular file; containment via `Path.relative_to` (allows `..spec.yaml`) |
| Resolve commit once | `rev-parse --verify --end-of-options <ref>^{commit}` then `cat-file -e` + `show` |
| Missing Git on PATH | `FileNotFoundError` → `GitDiffError("Git executable not found on PATH")` → CLI exit **2** |
| No English stderr matching | Classify by operation return codes / exceptions |

Deleted `test_git_diff_regressions.py` (cases absorbed into `test_git_diff.py`). Removed unused `g0_regression` pytest marker.

### Commands and results

```bash
cd adapters/python
.venv-p0/bin/pytest tests/test_git_diff.py -q
.venv-p0/bin/pytest tests/ -q
```

| Suite | Result |
| --- | --- |
| `tests/test_git_diff.py` | **20 passed** |
| Full adapter `tests/` | **88 passed** |

### Next group

**G2:** TypeScript parity (`src/gitDiff.ts`).

---

## G2: Match TypeScript behavior

**Date:** 2026-09-03  
**Scope:** `src/gitDiff.ts`, `tests/gitDiff.test.ts`, `tests/cli.test.ts` (cwd-aware CLI harness).

### Key changes

Mirrored Python boundaries: cwd discovery, symlink rejection, path-component containment (allows `..spec.yaml`), `rev-parse --verify --end-of-options <ref>^{commit}`, `cat-file -e` + `show`, spawn `ENOENT` → “Git executable not found on PATH”, no English stderr classification.

CLI tests must spawn with fixture `cwd` and an absolute `--import` path to `tsx` so Node resolves the loader outside the consumer repo.

Deleted `tests/gitDiff.baseline.test.ts` (absorbed into `tests/gitDiff.test.ts`).

### Commands and results

```bash
npm test -- tests/gitDiff.test.ts tests/cli.test.ts tests/diff.test.ts
```

| Suite | Result |
| --- | --- |
| `tests/gitDiff.test.ts` | **20 passed** |
| `tests/cli.test.ts` | **8 passed** |

---

## G3: Document and finish

**Date:** 2026-09-03

### Documentation

- Accepted [ADR 0021](../../adr/0021-git-diff-input-boundary.md); ADR index updated; [0017](../../adr/0017-git-aware-diff.md) marked refined by 0021.
- Root README and `adapters/python/README.md`: previous-commit / target-tip / merge-base recipes; no `|| true`; new/renamed/deleted path → exit 2; no implicit fetch.
- `docs/ARCHITECTURE.md`: cwd discovery and boundary behavior.
- Plan/SPEC status → Implemented.

### Final gates

```bash
cd adapters/python && .venv-p0/bin/pytest tests/ -q
npm test
npm run build
```

| Gate | Result |
| --- | --- |
| Python adapter tests | **88 passed** |
| `npm test` | **66 passed** (8 files) |
| `npm run build` | **Success** |

### Environment (final)

| Component | Version |
| --- | --- |
| Python (adapter venv `.venv-p0`) | 3.11.14 |
| Node | v24.14.1 |
| Git | 2.50.1 (Apple Git-155) |
| vitest | 2.1.9 |

### Unresolved / out of scope

- Rename detection, automatic merge-base inside Postulate, remote fetch.
- Linked Git worktree exercised only insofar as `rev-parse --show-toplevel` supports it (no dedicated multi-worktree fixture).
- Non-English Git locale: classification no longer depends on English stderr substrings.
