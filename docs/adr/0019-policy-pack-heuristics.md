# 0019. Policy pack heuristics (Python)

- Status: Accepted
- Date: 2026-09-01
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

[0007](0007-policies-are-declarations.md) stores `policies` as free strings without enforcement. Python consumers (webcheck-api first) already declare `unit_tests_stay_offline` and `no_secrets_in_output` in ADRs and want CI signal before OPA/Rego or semgrep rules land.

Milestone C needs a small, opt-in policy pack that:

- runs only for policies listed in the spec YAML;
- inspects the consumer project's `tests/` tree;
- warns by default (mirrors [0013](0013-warnings-opt-in-ci.md));
- does not change the YAML schema or TypeScript structural checks.

## Decision

Add `postulate policies check <spec> [--project-root PATH] [--fail-on-warnings]` to the Python adapter.

### Supported policies (v1)

| Policy | Heuristic | Severity |
| --- | --- | --- |
| `unit_tests_stay_offline` | Under `tests/`, flag Python files that import or call `httpx` / `requests` unless the file also uses `respx` or a `monkeypatch` pattern (fixture parameter or `.setattr` call). | warning |
| `no_secrets_in_output` | Flag `assert` statements whose compared string literals look secret-like (length ≥ 16, high character diversity, or known prefixes such as `sk-`, `AKIA`) unless the assertion involves a sanitizer call (`sanitize`, `redact`, `mask`, `scrub`, `assert_safe`). | warning |

Behavior:

1. Load spec; exit `2` on load failure.
2. For each policy name in `spec.policies` that has a registered checker, scan `project_root/tests/**/*.py`.
3. Emit `!` warnings for violations; exit `0` unless `--fail-on-warnings` (then exit `1`).
4. Unknown policy names are ignored (still declarations for `diff`); no error.
5. Policies not listed in the spec are not checked.

Heuristics are intentionally shallow AST/grep rules. Documented false positives include: commented-out imports, type-only imports, tests that mock via `unittest.mock.patch` without `monkeypatch`, and short placeholder secrets in fixtures.

OPA/Rego and semgrep integration remain out of scope.

### `postulate init`

Add `postulate init --output PATH [--tests FILE ...]`:

- Creates parent directories and a skeleton spec (`feature`, placeholder contract, one BDD scenario).
- With `--tests`, runs pytest collection on the given paths and suggests `test_mapping` entries keyed by the `test_*` function suffix (e.g. `test_foo` → `foo`).
- Does not overwrite an existing output file.

## Consequences

- Python CI can run `postulate policies check` after `verify` when policies are declared.
- TypeScript CLI does not gain policy enforcement in v1; parity is not required for Milestone C.
- Teams must treat policy warnings as heuristic signal, not proof.
- Future policies or stricter rules need a new ADR or an amendment to this one.

## Alternatives considered

- `postulate ci --enforce-policies` — overloads `ci` semantics; separate subcommand keeps structural check unchanged.
- Error severity by default — too noisy for heuristic rules; opt-in strictness via `--fail-on-warnings`.
- Enforce all policies in every repo — ignores the declaration model; only listed policies run.
