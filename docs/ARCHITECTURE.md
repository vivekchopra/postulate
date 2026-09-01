# Postulate Architecture

This document describes the system as it exists today. It is not a roadmap and it does not record rejected designs. Design rationale belongs in `docs/adr/`; change-specific work belongs in `docs/plans/`.

## System boundary

Postulate loads YAML specifications, validates their shape, applies structural checks, generates LLM implementation prompts, compares specifications for regressions, and (Python) resolves `test_mapping` locators against pytest collection.

It does not call an LLM, execute contract expressions, run mapped tests, enforce declared policies, prove correctness, or replace a user's test runner.

## Implementations

| Surface | Location | Commands |
| --- | --- | --- |
| TypeScript CLI (reference) | `src/` | `check`, `prompt`, `ci`, `diff` |
| Python adapter (PyPI `postulate`) | `adapters/python/` | `check`, `prompt`, `ci`, `diff`, **`verify`** |

Both implementations share the same YAML contract ([`docs/SPEC.md`](SPEC.md)). Parity tests use fixtures under `adapters/fixtures/specs/`.

## TypeScript components

```text
                         +-------------------+
                         |    postulate CLI  |
                         |   src/index.ts    |
                         +---------+---------+
                                   |
             +---------------------+----------------------+
             |                     |                      |
             v                     v                      v
     +---------------+      +--------------+      +---------------+
     |   loadSpec    |      |  checkSpec   |      |   diffSpecs   |
     | loadSpec.ts   |      |   check.ts   |      |    diff.ts    |
     +-------+-------+      +------+-------+      +-------+-------+
             |                     |                      |
             v                     v                      |
     +---------------+      +--------------+              |
     | PostulateSchema|     |  invariants  |              |
     |   spec.ts      |     | invariants.ts|              |
     +---------------+      +--------------+              |
                                                            |
                                   +------------------------+
                                   |
                                   v
                           +---------------+
                           | prompt builder|
                           |   prompt.ts   |
                           +---------------+
```

## Python components

```text
                         +-------------------+
                         |  postulate (CLI)  |
                         |  adapters/python  |
                         +---------+---------+
                                   |
        +--------------------------+---------------------------+
        |                          |                           |
        v                          v                           v
 +-------------+           +-------------+            +----------------+
 |  load_spec  |           | check_spec  |            |  verify_spec   |
 | models.py   |           |  check.py   |            |   verify.py    |
 +-------------+           +-------------+            +--------+-------+
        |                          |                            |
        v                          v                            v
 +-------------+           +-------------+            pytest --collect-only
 | PostulateSpec|          | diff/prompt |            (node ID resolution)
 +-------------+           +-------------+
```

### `adapters/python/src/postulate/cli.py`

CLI entry with the same exit semantics as TypeScript for shared commands. `verify` exits `2` on load or pytest collection failure.

### `adapters/python/src/postulate/verify.py`

Runs structural checks, collects pytest node IDs from `--project-root`, and resolves `test_mapping` locators ([ADR 0015](adr/0015-pytest-test-mapping-locator.md), [ADR 0016](adr/0016-verify-command.md)).

## Responsibilities (TypeScript)

### `src/index.ts`

Owns the CLI surface and process exit behavior for:

- `check <spec-file>`
- `prompt <spec-file>`
- `ci <spec-file> [--fail-on-warnings]`
- `diff <before> <after>`

Load failures exit `2`; failed checks or regressions exit `1`.

### `src/spec.ts`

Defines the runtime Postulate specification contract with Zod and exports the inferred TypeScript types.

The Zod schema is the runtime source of truth. `schemas/postulate.schema.json` mirrors it for editor/tool integration and is covered by consistency tests.

### `src/loadSpec.ts`

Owns the filesystem and YAML parsing boundary.

### `src/check.ts`

Applies structural checks. Does not open files named in `test_mapping`.

### `src/invariants.ts`

Known invariant name registry (informational).

### `src/prompt.ts`

Renders a codegen prompt. Does not invoke a model.

### `src/diff.ts`

Compares two loaded specifications for structural regressions and improvements.

## Data flow

### Check / CI

```text
YAML file -> load -> schema validation -> check_spec -> diagnostics -> exit code
```

### Verify (Python only)

```text
YAML file -> load -> check_spec -> pytest --collect-only -> resolve test_mapping -> exit code
```

### Prompt

```text
YAML file -> load -> build_codegen_prompt -> stdout
```

### Diff

```text
before YAML -> load --+
                      +-> diff_specs -> regressions/improvements -> exit code
after YAML  -> load --+
```

## Test boundary

- TypeScript: `tests/` plus `examples/ts-late-fee/`
- Python: `adapters/python/tests/` plus `adapters/python/examples/minimal-pytest/`
- Shared parity fixtures: `adapters/fixtures/specs/`

No external services or network calls in unit tests.

## Documentation lifecycle

- `ARCHITECTURE.md`: what the system looks like now.
- `adr/`: why durable design decisions were made.
- `plans/<change>/`: scoped implementation plans.
- `ROADMAP.md`: future product direction.

When code changes the current architecture, update this file in the same branch.
