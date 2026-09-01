# Test and Schema Hardening Spec

This spec covers only the hardening change. The product contract remains in `docs/SPEC.md`.

## Required behavior

### Spec loading

- A valid YAML file returns a validated `PostulateSpec`.
- A missing file throws `SpecLoadError` and includes the resolved path.
- Invalid YAML throws `SpecLoadError` and identifies the file as invalid YAML.
- A schema-invalid document throws `SpecLoadError` and includes the failing field path.

### Prompt generation

A generated prompt must:

- tell the coding agent not to invent behavior outside the spec;
- tell the coding agent to surface ambiguity rather than guess;
- request implementation;
- request tests for every BDD scenario;
- request property tests or assertions for every invariant;
- request a correctness argument;
- request remaining assumptions;
- embed the loaded spec.

### CLI behavior

- Load failure exits `2`.
- Failed structural checks exit `1`.
- Successful `check` exits `0`.
- `ci` without `--fail-on-warnings` does not fail only because warnings exist.
- `ci --fail-on-warnings` exits `1` for a warning-only spec.
- Successful `prompt` exits `0` and writes the generated prompt to stdout.
- `diff` exits `1` when a regression is present.

### JSON Schema mirror

The checked-in JSON Schema must agree with the current Zod schema on the constraints covered by the consistency test, including:

- required top-level fields;
- required contract fields;
- required BDD scenario fields;
- minimum lengths for required non-empty strings and arrays;
- risk values and default;
- defaultable collection/object fields represented as optional in JSON Schema.

## Non-requirements

This change does not establish that mapped tests exist, ran, or passed. It does not make invariants executable and does not change Postulate's claims about correctness.
