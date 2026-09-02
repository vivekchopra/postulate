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
