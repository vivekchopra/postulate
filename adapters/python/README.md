# Postulate Python adapter

Native Python CLI for Postulate specs. Matches the TypeScript reference for `check`, `ci`, `prompt`, `diff`, and adds `verify` for pytest `test_mapping` resolution, `policies check` for declared policy heuristics, `init` for scaffolding new specs, and a pytest plugin for execution coverage.

## Install

```bash
cd adapters/python
pip install -e ".[dev]"
```

The package registers a pytest entry point automatically. After install, use `pytest --postulate-spec …` on the **same** pytest invocation that runs your tests. Postulate does not spawn a second test run.

## Commands

```bash
postulate check path/to/postulate.yaml
postulate ci path/to/postulate.yaml --fail-on-warnings
postulate prompt path/to/postulate.yaml
postulate diff before.yaml after.yaml
postulate diff --git HEAD~1 path/to/postulate.yaml
postulate verify path/to/postulate.yaml --project-root .
postulate policies check path/to/postulate.yaml --project-root .
postulate init --output specs/feature/postulate.yaml [--tests tests/test_feature.py]
pytest --postulate-spec path/to/postulate.yaml [--postulate-fail-on-warning]
```

### Policy pack (Milestone C)

When a spec declares `unit_tests_stay_offline` or `no_secrets_in_output`, run:

```bash
postulate policies check specs/safety/postulate.yaml --project-root .
```

Violations are warnings by default. Use `--fail-on-warnings` in CI to promote them to errors. Heuristics may produce false positives (documented in [ADR 0019](../../docs/adr/0019-policy-pack-heuristics.md)).

### test_mapping locators

Use pytest node IDs relative to the project root (pytest `rootpath` / `postulate verify --project-root`):

```text
tests/test_safety.py::test_no_secrets_in_output
tests/test_safety.py::TestOutput::test_no_secrets
tests/test_safety.py::test_values[param-case]
```

Rules:

- Paths are root-relative and exact. Shorthand such as `tests/test_safety.py::…` does **not** match `packages/a/tests/test_safety.py::…`.
- A base locator (no `[…]`) is satisfied when **at least one** parametrized case runs, not all cases.
- Parameter text inside `[…]` is preserved verbatim.

### verify vs pytest plugin

| Command | Question answered |
| --- | --- |
| `postulate verify` | Can pytest **collect** each mapped node from `--project-root`? (structural + collection only) |
| `pytest --postulate-spec` | Did mapped tests **execute** in this session? (non-skipped call reports) |

Run both in CI when specs back pytest suites:

```bash
postulate verify specs/safety/postulate.yaml --project-root .
pytest --postulate-spec specs/safety/postulate.yaml
```

**Execution is not the same as passing.** A mapped test that fails an assertion still counts as exercised; pytest retains the failure exit code. When mappings are satisfied but pytest failed, the plugin prints `mapping execution check satisfied; pytest session failed` rather than `plugin passed`.

### Plugin semantics and migration

Behavior is defined in [ADR 0020](../../docs/adr/0020-pytest-execution-coverage.md) (supersedes [ADR 0018](../../docs/adr/0018-pytest-plugin-exercised-mapping.md) skip/execution details).

| Topic | Behavior |
| --- | --- |
| Declared claims | Every invariant and BDD scenario name is checked, even when `test_mapping` is absent or blank. |
| Skipped / xfail (skipped report) | Do **not** count as exercised. |
| XPASS | Counts as exercised; pytest still applies strict xfail policy. |
| `--postulate-fail-on-warning` | Promotes BDD and unknown-key warnings to failures. |
| Partial runs (`-k`, selected paths, `-x`) | Unrun mapped tests are reported as not exercised. |
| Unsupported modes | `--collect-only` and active pytest-xdist (`-n`) with `--postulate-spec` exit with usage errors; use `postulate verify` for collection-only checks. |
| Exit codes | Coverage failures change **0 → 1** only; existing pytest failures (1, 5, …) are preserved. |

**Migration from pre-0020 behavior:** use full root-relative locators, ensure CI runs the suite paths that cover spec-backed modules, and expect skipped tests or missing mappings to fail where they previously passed silently.

## Recommended CI (Python projects)

```yaml
- run: pip install -e "./adapters/python[dev]"
- run: postulate verify specs/safety/postulate.yaml --project-root .
- run: pytest --postulate-spec specs/safety/postulate.yaml
```

For PRs that change specs (or code/tests that should stay aligned with the spec), compare against a local base revision. Prefer a merge-base for multi-commit branches:

```bash
set -e
# Previous commit only:
# postulate diff --git HEAD~1 specs/safety/postulate.yaml
#
# Target tip (must already be available locally; no implicit fetch):
# postulate diff --git origin/main specs/safety/postulate.yaml
#
# Full branch change vs target:
base_sha=$(git merge-base HEAD origin/main)
postulate diff --git "$base_sha" specs/safety/postulate.yaml
```

Do not wrap the check in `|| true`. Missing history, a new/renamed path with no blob at the base, or a deleted working spec exits 2 for review. Invoke from the consumer repo; symlinked specs are rejected.
## Examples

### Minimal pytest consumer

```bash
cd examples/minimal-pytest
pip install -e "../..[dev]"
postulate check postulate.yaml
postulate verify postulate.yaml --project-root .
pytest --postulate-spec postulate.yaml
```

### Safety / offline fixture (`no_secrets_in_output`)

```bash
cd examples/safety-offline
pip install -e "../..[dev]"
postulate verify postulate.yaml --project-root .
pytest --postulate-spec postulate.yaml
```

This example maps the `no_secrets_in_output` invariant to `tests/test_safety.py::test_no_secrets_in_output`.

## Tests

```bash
pytest
```

Implementation plans: [`docs/plans/python-adapter/`](../../docs/plans/python-adapter/PLAN.md) (Milestones A–C), [`docs/plans/pytest-coverage/`](../../docs/plans/pytest-coverage/PLAN.md) (execution coverage hardening).
