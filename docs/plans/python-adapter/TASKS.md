# Python Adapter Tasks

Each milestone should merge independently. Acceptance criteria are in [`ACCEPTANCE.md`](ACCEPTANCE.md).

Read ADRs [0014](../../adr/0014-python-adapter-package.md)–[0018](../../adr/0018-pytest-plugin-exercised-mapping.md) before starting.

---

## Milestone A — Python CLI + verify

### A1. Package scaffold

- [x] Create `adapters/python/pyproject.toml` with `postulate` package and `postulate` console script
- [x] Create `src/postulate/` modules: `models`, `load_spec`, `check`, `diff`, `prompt`, `invariants`, `cli`
- [x] Add `adapters/python/tests/` with pytest configuration
- [x] Confirm Python `>=3.11` matches webcheck-api

### A2. Spec load + models

- [x] Pydantic `PostulateSpec` mirroring Zod `PostulateSchema`
- [x] `load_spec(path) -> PostulateSpec` with `SpecLoadError` and field paths on validation failure
- [x] Tests: valid YAML, missing file, malformed YAML, schema error path

### A3. Structural check + CI

- [x] Port `check_spec` rules from `src/check.ts`
- [x] Port `print_check_result` with matching prefixes
- [x] Wire `postulate check` and `postulate ci --fail-on-warnings`
- [x] Tests: parity against shared fixtures (copy or symlink from `adapters/fixtures/specs/`)

### A4. Prompt + diff

- [x] Port `build_codegen_prompt` (section presence tests)
- [x] Port `diff_specs` and two-file `postulate diff`
- [x] Tests: regression/improvement classes match TS `tests/diff.test.ts` scenarios

### A5. verify command

- [x] Implement pytest collection parser for node IDs
- [x] Implement locator resolution per [0015](../../adr/0015-pytest-test-mapping-locator.md)
- [x] Wire `postulate verify <spec> [--project-root] [--fail-on-warnings]`
- [x] Tests: fake pytest output fixtures (no dependency on webcheck-api)
- [x] Tests: integration with a tiny sample project under `adapters/python/examples/minimal-pytest/`

### A6. Documentation + packaging

- [x] `adapters/python/README.md` with install and command examples
- [x] Update root `docs/ARCHITECTURE.md` when A merges (current state includes Python adapter)
- [x] Add parity job to Postulate CI (run TS + Python tests)
- [ ] Prepare PyPI publish workflow (can be manual first publish)

### Cursor prompt

See [`CURSOR_PROMPTS.md`](CURSOR_PROMPTS.md) § Milestone A.

---

## Milestone B — Git diff + pytest plugin

### B1. Git-aware diff (Python)

- [x] `postulate diff --git <ref> <spec-file>`
- [x] `git show <ref>:<path>` for before; load working tree file for after
- [x] Clear errors: not a git repo, ref missing, spec absent at ref
- [x] Tests: temporary git fixture repo

### B2. Git-aware diff (TypeScript)

- [x] Same `--git` flag on TS `postulate diff`
- [x] Tests in `tests/diff.test.ts` or `tests/cli.test.ts`
- [x] Parity with Python behavior on shared fixtures

### B3. pytest plugin

- [x] Entry point `postulate.pytest_plugin`
- [x] `--postulate-spec` and `--postulate-fail-on-warning`
- [x] Compare session's ran node IDs to `test_mapping`
- [x] Tests: plugin unit tests with pytester's `pytester` fixture

### B4. Consumer docs

- [x] Document CI snippet in `adapters/python/README.md`
- [x] Add "Python consumers" section to root `README.md`

### Cursor prompt

See [`CURSOR_PROMPTS.md`](CURSOR_PROMPTS.md) § Milestone B.

---

## Milestone C — Policies + init (optional follow-up)

### C1. Policy ADR

- [x] Write ADR 0019 for policy rule definitions and severity

### C2. Policy enforcement

- [x] `unit_tests_stay_offline` heuristic for `tests/`
- [x] `no_secrets_in_output` heuristic
- [x] `postulate policies check` (or documented equivalent)
- [x] Tests with intentional violations in fixture tree

### C3. init scaffold

- [x] `postulate init --output ... [--tests ...]`
- [x] Tests: creates file, suggests mappings from collection

---

## Milestone D — webcheck-api pilot (consumer repo) — **Skipped**

Tracked here for sequencing; implemented in **webcheck-api**, not postulate. **Cancelled** for this plan — consumer pilot deferred to a separate webcheck-api effort.

### D1. Safety spec

- [x] ~~Add `specs/safety/postulate.yaml` covering normalize/sanitize/assert_safe_target invariants~~ (skipped)
- [x] ~~Map to existing tests in `tests/test_safety.py`~~ (skipped)
- [x] ~~`postulate verify` in CI~~ (skipped)

### D2. pytest plugin in CI

- [x] ~~`pytest --postulate-spec specs/safety/postulate.yaml` in CI or `scripts/smoke.sh`~~ (skipped)

### D3. Second spec (stretch)

- [x] ~~`specs/free_scans/postulate.yaml` + mappings to `tests/test_free_scans_api.py`~~ (skipped)

### D4. PR template

- [x] ~~Note spec changes and `postulate diff --git` output in webcheck PR checklist (optional)~~ (skipped)

---

## Status

| Milestone | Status |
| --- | --- |
| A — Python CLI + verify | **Complete** (PyPI workflow pending) |
| B — Git diff + pytest plugin | **Complete** |
| C — Policies + init | **Complete** |
| D — webcheck pilot | **Skipped** (consumer repo; deferred) |
