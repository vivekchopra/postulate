# Pytest coverage — implementation notes

## P0: Establish baseline

**Date:** 2026-09-02  
**Planning baseline commit:** `89d0048` (`docs: bump next ADR id to 0020 after policy pack ADR`)  
**Implementation branch:** `master` (local; uncommitted planning overlay docs preserved separately)  
**Scope:** P0 only — no production code changes, no ADR acceptance, no P1 work.

### Git status at start

- **HEAD:** `89d0048`, synced with `origin/master`.
- **Preserved local changes (not part of P0 commit):** modified `ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/PLAN.md`, `docs/README.md`, `docs/TASKS.md`, `docs/adr/README.md`; untracked planning overlay (`docs/plans/python-project-testing.md`, `docs/plans/python-testing-review.md`, `docs/plans/pytest-coverage/`, `docs/plans/git-diff-hardening/`, proposed ADRs 0020/0021).
- **P0 file changes:** `adapters/python/tests/test_pytest_coverage_regressions.py`, `adapters/python/pyproject.toml` (marker registration), this file, `docs/plans/pytest-coverage/TASKS.md` checkboxes.

### Implementation vs review baseline (`89d0048`)

Compared current source to [python-testing-review.md](../python-testing-review.md). **No drift** from the planning snapshot on the gaps under test:

| Gap | Review finding | Source evidence (unchanged at `89d0048`) | Confirmed by P0 regression |
| --- | --- | --- | --- |
| P-01 Missing mapping silently passes | Plugin never evaluates declared claims without `test_mapping` keys | `check_mapping_coverage` iterates `test_mapping.items()` only; plugin does not call `check_spec` | Yes — plugin prints "passed", exit 0 |
| P-03 Skipped tests count as exercised | Setup skips and skipped reports added to `ran_node_ids` | `pytest_plugin.py` `pytest_runtest_logreport`: `if report.when == "call" or report.skipped` | Yes — skipped mapped test, plugin exit 0 |
| P-06 Path collision / suffix match | `_normalize_node_id` truncates at `/tests/`; `resolve_locator` suffix-matches | `mapping.py` lines 13–15, 23–25 | Yes — unit + plugin false pass |

**Additional review gaps (not covered by P0 regressions; still open for P1/P2):**

- Pytest failures can lose original exit meaning (`pytest_sessionfinish` sets exit 1/2 without preserving prior status).
- Plugin assumes terminal reporter exists (`terminal.write_line` without guard).
- Git diff hardening items are out of P0 scope (separate plan).
- `postulate check` already errors on missing invariant mappings; the plugin gap is independent of structural check.

### Environment

Isolated venv (not committed): `adapters/python/.venv-p0`

```bash
/opt/homebrew/bin/python3.11 -m venv adapters/python/.venv-p0
adapters/python/.venv-p0/bin/pip install -e './adapters/python[dev]'
```

| Component | Version |
| --- | --- |
| Python | 3.11.14 |
| pytest | 9.1.1 |
| postulate (editable) | 0.1.0 |
| pydantic | 2.13.5 |
| typer | 0.27.2 |
| PyYAML | 6.0.3 |
| pluggy | 1.6.0 |

Platform: darwin (macOS).

### Commands and results

#### Baseline adapter suite (existing tests; must pass)

```bash
cd adapters/python
.venv-p0/bin/python -m pytest tests/ -m "not p0_regression" -v
```

**Result:** 37 passed, 5 deselected (regression module collected but skipped by marker).

#### P0 regression suite (intended behavior; expected to fail until P1/P2)

```bash
cd adapters/python
.venv-p0/bin/python -m pytest tests/test_pytest_coverage_regressions.py -v
```

**Result:** 5 failed (all expected at baseline).

| Test | Acceptance ID | Expected | Actual (baseline) | Bug demonstrated |
| --- | --- | --- | --- | --- |
| `test_p01_declared_invariant_without_mapping_must_fail_plugin` | P-01 | exit 1, names `no_secrets_in_output`, missing mapping | exit 0, "plugin passed" | Claim without mapping not evaluated |
| `test_p03_skipped_mapped_test_must_not_count_as_exercised` | P-03 | exit 1, invariant not exercised | exit 0, "plugin passed" | Skipped call counts as exercised |
| `test_p06_normalize_preserves_root_relative_path` | P-06 | preserve `packages/b/tests/...` | truncates to `tests/test_safety.py::...` | `/tests/` path stripping |
| `test_p06_shorthand_locator_must_not_suffix_match_different_package` | P-06 | `resolve_locator` returns False | returns True | suffix matching |
| `test_p06_plugin_shorthand_locator_must_not_match_nested_package_test` | P-06 | exit 1 | exit 0, "plugin passed" | truncation + shorthand collision |

#### Full collection (informational)

```bash
.venv-p0/bin/python -m pytest tests/ -v
```

**Result:** 37 passed, 5 failed (baseline + regressions together).

TypeScript baseline (`npm test`, `npm run build`) was **not re-run** in P0; prior milestone verification reported 46 passing TS tests at `414b25e`/`89d0048`.

### Files changed (P0)

| File | Change |
| --- | --- |
| `adapters/python/tests/test_pytest_coverage_regressions.py` | New — 5 regression tests marked `p0_regression` |
| `adapters/python/pyproject.toml` | Register `p0_regression` marker |
| `docs/plans/pytest-coverage/IMPLEMENTATION_NOTES.md` | This baseline record |
| `docs/plans/pytest-coverage/TASKS.md` | P0 checkboxes updated after verification |

**Not changed:** `mapping.py`, `pytest_plugin.py`, `verify.py`, schema, ADR statuses, Git diff code.

### Confirmed gaps blocking P1 start

Nothing blocks P1 — regressions are in place and failing as expected. P1 should:

1. Enumerate declared claims (invariants + BDD names), including absent/blank mappings.
2. Replace `_normalize_node_id` `/tests/` truncation and `resolve_locator` suffix matching with exact root-relative identity.
3. Share corrected matching with `verify`.

P2 remains blocked on P1 for report-classification integration but can proceed in parallel once mapping helpers exist.

### Notes for regression authors

- Plugin subprocess specs require at least one BDD scenario (`PostulateSpec.bdd` `min_length=1`). Placeholder `unused_scenario` entries are used where BDD coverage is not under test.
- Run baseline and regressions separately during P0–P2 to avoid conflating unrelated failures:

```bash
pytest tests/ -m "not p0_regression"   # must pass
pytest tests/ -m p0_regression         # expected failures until fixed
```

## P1: Make mapping identity complete and exact

**Date:** 2026-09-02  
**Branch:** `cursor/pytest-coverage-p0-baseline` (local, uncommitted)  
**Scope:** P1 only — mapping/verify; no report lifecycle (P2), no docs/ADR acceptance (P3).

### Changes

| File | Change |
| --- | --- |
| `adapters/python/src/postulate/mapping.py` | Claim enumeration; exact locator normalization/matching; unknown-key warnings; `include_missing_claims` flag for verify dedup |
| `adapters/python/src/postulate/verify.py` | `--rootdir` alignment; `include_missing_claims=False`; import `normalize_node_id` |
| `adapters/python/src/postulate/pytest_plugin.py` | Use `normalize_node_id` (behavior via shared `check_mapping_coverage`) |
| `adapters/python/tests/test_mapping.py` | New — unit and plugin tests for P-01, P-02, P-04 through P-07 |
| `adapters/python/tests/test_pytest_coverage_regressions.py` | Trimmed to P-03 only (P-01/P-06 fixed by P1) |

### Behavior

- **Claims:** `check_mapping_coverage` now walks declared invariant and BDD names in deterministic order. Missing or blank mappings error for invariants and warn for BDD-only claims. Shared names emit one invariant-severity message.
- **Locators:** Path portion normalized (`./` stripped, `..` collapsed, no `/tests/` truncation). Exact node match; unparametrized base matches `base[param]` only. No suffix/path shorthand matching.
- **Unknown keys:** Warn even when the locator resolves to a collected/observed node.
- **Verify:** Passes `--rootdir=<project-root>` to pytest collection; skips missing-claim diagnostics already covered by `check_spec`; still reports blank/unresolved locators.

Parametrized matching rules are covered in `test_mapping.py` (P-07); inline comments in tests document base-vs-exact case behavior.

### Commands and results

Environment: same as P0 (`adapters/python/.venv-p0`, Python 3.11.14, pytest 9.1.1).

```bash
cd adapters/python
.venv-p0/bin/pip install -e '.[dev]'
.venv-p0/bin/python -m pytest tests/ -m "not p0_regression" -v
.venv-p0/bin/python -m pytest tests/ -m p0_regression -v
```

| Suite | Result |
| --- | --- |
| Baseline (`not p0_regression`) | **54 passed**, 1 deselected |
| P0 regression (`p0_regression`) | **1 failed** (expected — P-03 skipped-test counting; P2 scope) |

Acceptance coverage from new tests:

| ID | Status after P1 |
| --- | --- |
| P-01 | Pass — missing invariant mapping fails plugin |
| P-02 | Pass — BDD missing/blank/unresolved warns; strict flag fails; verify dedupes structural missing BDD |
| P-03 | **Fail** — skipped mapped test still counts as exercised (P2) |
| P-04 | Pass — shared name, one invariant error |
| P-05 | Pass — unknown key warns despite resolved target |
| P-06 | Pass — no path truncation or suffix collision |
| P-07 | Pass — exact/base parametrization and class nodes |

### Unresolved / deferred to P2

- P-03: `pytest_plugin.py` still records skipped setup/call reports as exercised.
- Exit-status preservation, early spec validation, terminal-reporter guard (P-08–P-14).
- Per-category exercised/declared summary lines (P2 diagnostics).

### Next group

**P3:** Prove installed-plugin behavior and document migration.

## P2: Observe execution and preserve pytest behavior

**Date:** 2026-09-02  
**Branch:** `cursor/pytest-coverage-p0-baseline` (local, uncommitted)  
**Scope:** P2 only — plugin lifecycle and exercise reporting; no P3 docs/CI/ADR acceptance.

### Changes

| File | Change |
| --- | --- |
| `adapters/python/src/postulate/mapping.py` | `ExerciseSummary`, `compute_exercise_summary`, `check_exercise_coverage` with skip/setup hints |
| `adapters/python/src/postulate/pytest_plugin.py` | Early spec validation; eligible call tracking; category summary; exit-status preservation; stderr fallback |
| `adapters/python/tests/test_pytest_plugin_lifecycle.py` | **New** — P-03, P-08 through P-14 lifecycle tests |
| `adapters/python/tests/test_pytest_plugin.py` | Updated exercise failure message assertion |
| `adapters/python/tests/test_pytest_coverage_regressions.py` | **Removed** — P-03 covered in lifecycle suite |
| `adapters/python/pyproject.toml` | Removed `p0_regression` marker (no longer needed) |

### Behavior

- **Early validation (`pytest_configure`):** Spec loaded once; invalid/missing spec → `UsageError` (exit 4) before test bodies run. `--collect-only` and active xdist (`-n` / `PYTEST_XDIST_WORKER`) rejected with guidance to use `postulate verify`.
- **Eligible reports:** Only non-skipped `call` reports with passed/failed outcomes count as exercised. Setup failures/skips and call skips recorded as hints for diagnostics.
- **Diagnostics:** `check_exercise_coverage` emits `spec claims '…' but no mapped test ran (reason)` with reasons `skipped`, `setup failed`, or `no eligible call report`. Category summary lines: `invariants exercised X/Y`, `BDD scenarios exercised X/Y`.
- **Exit codes:** Coverage failure changes exit **0 → 1** only. Preexisting nonzero statuses (including 1, 4, 5) are preserved. When pytest failed but mappings satisfied: `mapping execution check satisfied; pytest session failed` (not "plugin passed").
- **Terminal reporter:** Falls back to stderr when `terminalreporter` is disabled. No Postulate I/O without `--postulate-spec`.

### Commands and results

```bash
cd adapters/python
.venv-p0/bin/pip install -e '.[dev]'
.venv-p0/bin/python -m pytest tests/ -q
```

**Result:** **69 passed**

| Acceptance ID | Status after P2 |
| --- | --- |
| P-03 | Pass — skipped mapped test not exercised |
| P-08 | Pass — setup failure unexercised; call/teardown failure still exercised |
| P-09 | Pass — XFAIL skip not exercised; XPASS exercised |
| P-10 | Pass — partial selection reports missing execution |
| P-11 | Pass — pytest failure status preserved when mappings satisfied |
| P-12 | Pass — invalid/missing spec → usage error 4 before tests |
| P-13 | Pass — no flag silent; missing terminal reporter safe |
| P-14 | Pass — collect-only and xdist rejected; no-tests preserves exit 5 |

### Unresolved / deferred

- **P-14 interruption:** Session interruption mid-run not explicitly tested (hard to simulate reliably in pytester); implementation preserves incoming status when nonzero.
- **P-11 arbitrary custom exit codes:** Covered for 0/1/4/5 operationally; no dedicated test for an arbitrary nonzero code like 3.

### Next group (completed)

**P3:** Prove installed-plugin behavior and document migration.

## P3: Prove installed-plugin behavior and document migration

**Date:** 2026-09-02  
**Branch:** `cursor/pytest-coverage-p0-baseline` (local, uncommitted)  
**Scope:** P3 integration, docs, CI, ADR acceptance; no Git diff hardening (G0–G3).

### Changes

| File | Change |
| --- | --- |
| `adapters/python/examples/safety-offline/` | **New** — offline fixture with `no_secrets_in_output` invariant |
| `adapters/python/tests/test_pytest_plugin_integration.py` | **New** — subprocess P-15 tests (entry-point discovery, full/targeted/skipped/failed/no-tests) |
| `adapters/python/README.md` | Migration guide, verify vs plugin, semantics table, examples |
| `docs/ARCHITECTURE.md` | Current hardened plugin/verify behavior |
| `docs/adr/0020-pytest-execution-coverage.md` | Status → **Accepted** |
| `docs/adr/0018-pytest-plugin-exercised-mapping.md` | Status → **Superseded by 0020** |
| `docs/adr/README.md` | Index updated |
| `.github/workflows/postulate.yml` | Removed duplicate plugin run; added `safety-offline` example step |

### P-15 acceptance commands

Environment: Python 3.11.14 / pytest 9.1.1 (`.venv-p0`); Node 22 for TS gates.

```bash
pip install -e './adapters/python[dev]'
pytest adapters/python/tests
npm ci && npm test && npm run build
```

| Gate | Result |
| --- | --- |
| `pytest adapters/python/tests` | **76 passed** |
| `npm test` | **46 passed** (7 files) |
| `npm run build` | **Success** |

### Acceptance evidence

| ID | Status |
| --- | --- |
| P-01 – P-14 | Pass (P0–P2 tests) |
| P-15 | Pass — installed entry-point discovery, full adapter suite, TS gates, example workflows |

### Pytest-coverage plan status

**All P0–P3 tasks complete.** Remaining work is under `docs/plans/git-diff-hardening/` (G0–G3).

### Next group (separate plan)

**G0:** Establish Git diff baseline (`docs/plans/git-diff-hardening/TASKS.md`).
