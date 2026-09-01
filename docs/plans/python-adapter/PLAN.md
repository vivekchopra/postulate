# Python Adapter Plan

## Goal

Make Postulate usable in Python codebases (first consumer: **webcheck-api**) without Node.js, and close the gap between `test_mapping` and pytest.

After this change, a Python project can:

```bash
pip install postulate
postulate check specs/safety/postulate.yaml
postulate verify specs/safety/postulate.yaml
pytest --postulate-spec specs/safety/postulate.yaml
postulate diff --git origin/master specs/safety/postulate.yaml
```

## Why now

- Test/schema hardening for the TypeScript CLI is complete.
- webcheck-api has extensive pytest coverage and ADRs (offline tests, no secrets) but no contract layer tying specs to tests.
- Without pytest integration, Postulate remains a YAML linter for Python repos.

## Milestones

| Milestone | Outcome | ADRs |
| --- | --- | --- |
| **A — Python CLI + verify** | PyPI package, CLI parity, pytest collection resolves `test_mapping` | [0014](../adr/0014-python-adapter-package.md), [0015](../adr/0015-pytest-test-mapping-locator.md), [0016](../adr/0016-verify-command.md) |
| **B — Exercise + git diff** | pytest plugin for mapped tests that ran; `diff --git` | [0017](../adr/0017-git-aware-diff.md), [0018](../adr/0018-pytest-plugin-exercised-mapping.md) |
| **C — Policies + scaffolding** | Optional policy pack; `postulate init` | (policy ADR when implementing) |
| **D — webcheck pilot** | One real spec in webcheck-api CI | consumer repo change |

Implement milestones in order. Do not start B until A acceptance passes.

## Scope (Milestones A–B in this repo)

### Milestone A

- `adapters/python/` package with Pydantic models mirroring `PostulateSchema`
- CLI: `check`, `prompt`, `ci`, `diff`, **`verify`**
- Pytest node ID collection and mapping resolution
- Parity tests against shared YAML fixtures (structural check, diff, prompt sections)
- PyPI-publishable `pyproject.toml`
- Example spec under `adapters/python/examples/` (minimal; not webcheck-sized)

### Milestone B

- `postulate diff --git <ref> <spec-file>` in TypeScript and Python
- pytest plugin `--postulate-spec`
- Document recommended CI snippet for Python consumers

### Milestone C (later, same plan folder)

- `postulate init --module ... --tests ...`
- Policy pack v1: `unit_tests_stay_offline`, `no_secrets_in_output` (Python AST/grep rules)
- `postulate ci --enforce-policies` or `postulate policies check`

### Milestone D (webcheck-api repo)

- Add `specs/safety/postulate.yaml` (pilot)
- Wire `postulate verify` + `pytest --postulate-spec` in webcheck CI
- Second spec: `specs/free_scans/postulate.yaml` (optional stretch)

## Explicitly out of scope (all milestones unless a new ADR says otherwise)

- Changing the YAML schema fields or check severity table in `docs/SPEC.md`
- Theorem proving, model checking, or evaluating contract predicate strings
- Mapping webcheck scanner `CHECKS.md` IDs into Postulate specs
- Property-test generation from named invariants (separate roadmap item)
- Architectural drift detection
- OPA/Rego policy engine
- Replacing pytest or running tests inside `check`

## Target architecture

```text
                    +---------------------------+
                    |   postulate CLI (PyPI)    |
                    |   adapters/python/        |
                    +-------------+-------------+
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
        v                         v                         v
 +-------------+          +-------------+          +------------------+
 |  load_spec  |          | check_spec  |          | verify_mappings  |
 |  (Pydantic) |          |  (parity)   |          | pytest collect   |
 +-------------+          +-------------+          +------------------+
        |                         |                         |
        v                         v                         v
 +-------------+          +-------------+          +------------------+
 |   prompt    |          |    diff     |          | pytest plugin    |
 |             |          |  (+ --git)  |          | --postulate-spec |
 +-------------+          +-------------+          +------------------+

TypeScript CLI (src/) remains reference; shared fixture corpus keeps behavior aligned.
```

## Consumer spec layout (webcheck-api)

Postulate specs belong at **module/API boundaries**, not per scanner check:

```text
specs/
  safety/postulate.yaml
  free_scans/postulate.yaml
  stripe_webhooks/postulate.yaml   # later
```

Each file: `feature`, `risk`, `contract`, `bdd`, `invariants`, `policies`, `test_mapping`, `correctness_argument`.

## Files expected to change (Postulate repo)

```text
adapters/python/**                          # new package
adapters/fixtures/**                        # shared YAML specs for parity tests (optional)
docs/adr/0014-0018.md
docs/adr/README.md
docs/plans/python-adapter/*
docs/TASKS.md
docs/PLAN.md
docs/ROADMAP.md                             # cross-link
src/diff.ts                                 # Milestone B: --git
tests/diff.test.ts                          # Milestone B
```

webcheck-api changes are Milestone D in that repository.

## Parity strategy

- Add `adapters/fixtures/specs/` with 3–5 YAML files (valid, high-risk warning, invalid mapping, diff before/after).
- TypeScript tests: existing suite.
- Python tests: load same fixtures; assert same `check` errors/warnings and `diff` regressions.
- On intentional divergence, update both implementations and document in an ADR.

## Risk

| Risk | Mitigation |
| --- | --- |
| Two implementations drift | Shared fixture corpus + parity tests in CI |
| pytest collection slow/flaky | Document `--project-root`; cache collection in verify if needed |
| PyPI name `postulate` taken | Fallback `postulate-spec` documented in plan tasks |
| webcheck pilot blocked on Milestone C policies | Pilot uses A+B only; policies are optional |
