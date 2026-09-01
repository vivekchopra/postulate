# Python Adapter Spec

This spec covers the Python adapter and pytest integration. The product contract remains in [`docs/SPEC.md`](../../SPEC.md). Durable decisions are in ADRs [0014](../../adr/0014-python-adapter-package.md)–[0018](../../adr/0018-pytest-plugin-exercised-mapping.md).

## Package

| Property | Value |
| --- | --- |
| PyPI name | `postulate` (fallback `postulate-spec` if unavailable) |
| Python | `>=3.11` |
| Console script | `postulate` |
| Location | `adapters/python/` |

Dependencies (runtime): `pydantic>=2`, `pyyaml`, `typer` (or stdlib `argparse` if Typer rejected during implementation), `rich` optional for output coloring.

Dev: `pytest`, `pytest-cov` optional.

## Commands

### Shared with TypeScript (behavioral parity)

| Command | Exit 0 | Exit 1 | Exit 2 |
| --- | --- | --- | --- |
| `check <spec>` | no structural errors | structural errors | load failure |
| `ci <spec> [--fail-on-warnings]` | same as TS | same as TS | load failure |
| `prompt <spec>` | prints prompt | — | load failure |
| `diff <before> <after>` | no regressions | regressions | load failure |

Output prefixes match [`SPEC.md`](../../SPEC.md) §8.1 (`i`, `!`, `✗`, `+`, `-`, `✓`).

### Python-specific

#### `verify <spec> [--project-root PATH] [--fail-on-warnings] [--pytest-args ...]`

1. Load and structurally check the spec (same rules as `check`).
2. Run `pytest --collect-only -q` with `cwd=project_root` (append `--pytest-args` when provided).
3. Parse collected node IDs from stdout (support pytest 8.x default output).
4. For each `test_mapping` entry:
   - **Invariant key**: locator must match a collected node ID exactly, or match a parametrized variant per [0015](../../adr/0015-pytest-test-mapping-locator.md).
   - **BDD scenario key**: same, but severity is **warning** unless `--fail-on-warnings`.
5. Report unresolved mappings with spec key and locator string.
6. Exit codes follow [0016](../../adr/0016-verify-command.md).

Collection failure (pytest exits non-zero) → verify exits `2` with stderr explaining collection failed.

#### `diff --git <ref> <spec-file>`

Per [0017](../../adr/0017-git-aware-diff.md). Implemented in Python (Milestone B) and TypeScript (Milestone B).

#### pytest plugin

Register entry point `pytest11` → `postulate.pytest_plugin`.

Options:

- `--postulate-spec PATH` — required to activate plugin
- `--postulate-fail-on-warning` — treat unexercised BDD mappings as failure

After session finish, compare `test_mapping` locators to **ran** node IDs (including skipped tests; exclude deselected).

## test_mapping locator format (Python)

Canonical:

```text
tests/test_safety.py::test_normalize_domain_from_url
```

Rules:

- Relative to `--project-root` (default `.`).
- Use `/` separators in paths.
- Parametrized: full node ID including `[param]`.

Example spec fragment:

```yaml
test_mapping:
  does_not_mutate_input: "tests/test_safety.py::test_sanitize_does_not_leak_raw_env"
  normalize_domain_strips_www: "tests/test_safety.py::test_normalize_domain_from_url"
```

## Structural check parity

Python `check_spec` must implement the same rules as `src/check.ts` ([`SPEC.md`](../../SPEC.md) §9):

- high/critical → requires invariants (error)
- non-empty BDD `then` (error)
- invariant → `test_mapping` key (error)
- high/critical → `correctness_argument` (warning)
- BDD name → `test_mapping` (warning)
- thin contract (warning)
- recognised vs custom invariants (info)

Known invariant names match `src/invariants.ts`.

## Prompt parity

Python `build_codegen_prompt` must include the same required sections as `src/prompt.ts` ([`SPEC.md`](../../SPEC.md) §11). Tests assert section presence, not byte-identical prose.

## Milestone C: policy pack (draft requirements)

Policies are still free strings in YAML. Milestone C adds optional enforcement for:

| Policy name | Intent |
| --- | --- |
| `unit_tests_stay_offline` | Under `tests/`, flag bare `httpx`/`requests` usage without `respx` or `monkeypatch` patterns (heuristic) |
| `no_secrets_in_output` | Flag test assertions that embed long secret-like literals without using project sanitizers |

Enforcement command (name TBD): `postulate policies check <spec> --project-root PATH`.

False positives are warnings by default; `--fail-on-warnings` promotes to error.

Write ADR 0019 when implementing policy rules.

## Milestone C: `init`

```text
postulate init --output specs/<name>/postulate.yaml [--tests tests/test_foo.py]
```

- Creates directory and skeleton YAML with `feature`, empty `contract`, one placeholder BDD scenario.
- If `--tests` provided, suggest `test_mapping` keys from collected `test_*` function names (no overwrite if file exists).

## Non-requirements

- Verify does not run mapped tests.
- Plugin does not run structural `check`.
- No automatic sync from webcheck `docs/CHECKS.md`.
- No guarantee that passing verify means behavior is correct.

## Consumer CI snippet (webcheck-api)

```yaml
- run: pip install postulate
- run: postulate verify specs/safety/postulate.yaml --project-root .
- run: pytest --postulate-spec specs/safety/postulate.yaml
```

Milestone D adds this to webcheck-api; not required for Postulate repo acceptance.
