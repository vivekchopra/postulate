# Postulate Python adapter

Native Python CLI for Postulate specs. Matches the TypeScript reference for `check`, `ci`, `prompt`, `diff`, and adds `verify` for pytest `test_mapping` resolution.

## Install

```bash
cd adapters/python
pip install -e ".[dev]"
```

## Commands

```bash
postulate check path/to/postulate.yaml
postulate ci path/to/postulate.yaml --fail-on-warnings
postulate prompt path/to/postulate.yaml
postulate diff before.yaml after.yaml
postulate diff --git HEAD~1 path/to/postulate.yaml
postulate verify path/to/postulate.yaml --project-root .
pytest --postulate-spec path/to/postulate.yaml
```

### test_mapping locators

Use pytest node IDs relative to `--project-root`:

```text
tests/test_example.py::test_example_case
```

## Recommended CI (Python projects)

```yaml
- run: pip install postulate
- run: postulate verify specs/safety/postulate.yaml --project-root .
- run: pytest --postulate-spec specs/safety/postulate.yaml
```

Run `postulate verify` before tests to confirm mappings resolve in collection. Run `pytest --postulate-spec` after tests to confirm mapped tests were exercised in the session.

For PRs that change specs, compare against the base branch:

```bash
postulate diff --git origin/main specs/safety/postulate.yaml
```

## Minimal example

```bash
cd examples/minimal-pytest
pip install -e "../..[dev]"
postulate check postulate.yaml
postulate verify postulate.yaml --project-root .
pytest --postulate-spec postulate.yaml
```

## Tests

```bash
pytest
```

## Plan

Implementation tracked in [`docs/plans/python-adapter/`](../../docs/plans/python-adapter/PLAN.md).
