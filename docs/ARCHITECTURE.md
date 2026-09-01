# Postulate Architecture

This document describes the system as it exists today. It is not a roadmap and it does not record rejected designs. Design rationale belongs in `docs/adr/`; change-specific work belongs in `docs/plans/`.

## System boundary

Postulate is a TypeScript CLI that loads a YAML specification, validates its shape, applies structural checks, generates an LLM implementation prompt, and compares two specifications for regressions.

It does not call an LLM, execute contract expressions, inspect mapped test files, enforce declared policies, prove correctness, or run a user's test suite.

## Current components

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

## Responsibilities

### `src/index.ts`

Owns the CLI surface and process exit behavior for:

- `check <spec-file>`
- `prompt <spec-file>`
- `ci <spec-file> [--fail-on-warnings]`
- `diff <before> <after>`

It delegates parsing and domain logic to the modules below. Load failures exit `2`; failed checks or regressions exit `1`.

### `src/spec.ts`

Defines the runtime Postulate specification contract with Zod and exports the inferred TypeScript types.

The Zod schema is the runtime source of truth. `schemas/postulate.schema.json` mirrors it for editor/tool integration and is covered by consistency tests.

### `src/loadSpec.ts`

Owns the filesystem and YAML parsing boundary. It:

1. resolves and reads a spec file;
2. parses YAML;
3. validates the parsed value with `PostulateSchema`;
4. converts expected load/validation failures into `SpecLoadError` with readable paths.

### `src/check.ts`

Applies the current structural checks to an already-loaded `PostulateSpec` and returns errors, warnings, and informational diagnostics.

It does not evaluate predicates contained in contract strings and does not open files named in `test_mapping`.

### `src/invariants.ts`

Contains the small registry of invariant names Postulate recognizes today. Recognition is informational only; known invariants do not yet have executable semantics.

### `src/prompt.ts`

Renders a loaded spec into a text prompt for an external coding agent. It does not invoke a model.

### `src/diff.ts`

Compares two loaded specifications and reports the structural regression/improvement classes supported by v0.1, including dropped invariants, removed postconditions, removed scenarios, removed policies, and risk changes.

## Data flow

### Check / CI

```text
YAML file
   -> loadSpec
   -> PostulateSchema
   -> checkSpec
   -> diagnostics
   -> CLI exit code
```

### Prompt

```text
YAML file
   -> loadSpec
   -> PostulateSchema
   -> buildCodegenPrompt
   -> stdout
```

### Diff

```text
before YAML -> loadSpec --+
                         +-> diffSpecs -> regressions/improvements -> exit code
after YAML  -> loadSpec --+
```

## Test boundary

Unit tests live in `tests/`. The worked example under `examples/ts-late-fee/` demonstrates a consumer specification, implementation, and mapped tests.

The current test suite verifies Postulate's own parser, checker, prompt generation, diff behavior, CLI exit semantics, and JSON Schema mirror. It does not use external services or make network calls.

## Documentation lifecycle

- `ARCHITECTURE.md`: what the system looks like now.
- `adr/`: why durable design decisions were made.
- `plans/<change>/PLAN.md`: scope and approach for one change.
- `plans/<change>/SPEC.md`: requirements specific to that change.
- `plans/<change>/TASKS.md`: verifiable implementation steps.
- `plans/<change>/ACCEPTANCE.md`: definition of done, written before implementation.
- `plans/<change>/CURSOR_PROMPTS.md`: bounded prompts used to execute the plan.
- `ROADMAP.md`: future product direction.

When code changes the current architecture, update this file in the same branch. Do not put future architecture or rejected alternatives here.
