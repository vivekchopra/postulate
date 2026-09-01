# Test and Schema Hardening Tasks

Each task should be independently reviewable. Acceptance criteria are in `ACCEPTANCE.md`, not duplicated here.

## 1. Loader coverage

- [x] Test valid YAML loading.
- [x] Test missing-file `SpecLoadError`.
- [x] Test malformed-YAML `SpecLoadError`.
- [x] Test schema-validation failure with a field path.

## 2. Prompt coverage

- [x] Test the no-invented-behavior instruction.
- [x] Test ambiguity handling instruction.
- [x] Test required output sections.
- [x] Test that the spec is embedded.

## 3. CLI coverage

- [x] Test load-failure exit code.
- [x] Test structural-check failure exit code.
- [x] Test successful check exit code.
- [x] Test warning-only `ci` without strict warnings.
- [x] Test `ci --fail-on-warnings`.
- [x] Test prompt success/output.
- [x] Test diff regression exit code.

## 4. JSON Schema mirror

- [x] Add a consistency test for the important Zod/JSON Schema constraints.
- [x] Correct the checked-in JSON Schema where it disagrees with the runtime Zod schema.

## 5. Documentation

- [x] Add current-state `docs/ARCHITECTURE.md`.
- [x] Separate the project build order from this change-specific plan.
- [x] Separate tasks from acceptance criteria.
- [x] Add bounded agent prompts for this change.
