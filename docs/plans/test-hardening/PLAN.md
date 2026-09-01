# Test and Schema Hardening Plan

## Goal

Close the untested v0.1 paths before adding new product behavior. This change hardens the existing loader, prompt generation, CLI behavior, and JSON Schema mirror without changing the Postulate YAML contract or public commands.

## Why now

The current implementation has direct tests for structural checks and spec diffing, but the loader, prompt builder, CLI exit behavior, and JSON Schema mirror are not independently covered. Later roadmap work would otherwise build on behavior that can regress silently.

## Scope

This change will:

- add direct tests for `loadSpec`;
- add direct tests for `buildCodegenPrompt`;
- add subprocess tests for CLI exit codes and stdout/stderr behavior;
- cover `ci --fail-on-warnings`;
- add a consistency test for the checked-in JSON Schema and fix known differences from the Zod runtime schema;
- document the current architecture and the change-specific workflow.

## Explicitly out of scope

Do not add:

- new CLI commands;
- changes to the YAML contract;
- test-file discovery or validation of `test_mapping` targets;
- generated property tests;
- policy enforcement;
- coverage measurement;
- semantic contract diffing;
- architectural drift detection;
- git-aware diff;
- language adapters;
- a generic validation-rule framework.

## Approach

### Loader tests

Use temporary local files. Cover a valid spec, missing file, malformed YAML, and Zod validation failure with a path-qualified error message. No network access is required.

### Prompt tests

Construct an in-memory `PostulateSpec` and verify the stable contract of the generated prompt: no invented behavior, BDD tests, invariant tests/assertions, correctness argument, remaining assumptions, and embedded spec JSON.

The tests should avoid matching the entire prompt byte-for-byte so harmless prose edits do not cause unnecessary churn.

### CLI tests

Run the TypeScript CLI in subprocesses through Node with the installed `tsx` loader. Use temporary fixture specs to verify exit codes for load failure, structural failure, warning-only CI with and without `--fail-on-warnings`, prompt success, and diff regression.

The CLI implementation is not refactored solely for testing in this change.

### JSON Schema consistency

`src/spec.ts` remains the runtime source of truth. The checked-in `schemas/postulate.schema.json` is an interoperability mirror.

This phase does not add a schema-generation dependency. Instead, tests cover the structural constraints most likely to drift between the two representations: required properties, minimum string/array lengths, the risk enum, and scenario required fields/defaultable fields.

If the contract grows materially, replace this mirror test with generated JSON Schema in a separate design change.

## Files expected to change

```text
docs/ARCHITECTURE.md
docs/README.md
docs/PLAN.md
docs/TASKS.md
docs/plans/test-hardening/*
schemas/postulate.schema.json
tests/loadSpec.test.ts
tests/prompt.test.ts
tests/cli.test.ts
tests/schemaConsistency.test.ts
```

No source implementation file under `src/` should need to change for this phase.
