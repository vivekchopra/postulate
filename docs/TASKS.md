# Postulate TASKS.md

This file is the implementation plan for Cursor.

Use `docs/SPEC.md` as the source of truth. Implement only the current task. Do not jump ahead.

---

## Operating Rules for Cursor

Every Cursor task should include these constraints:

```text
Do not add theorem proving, model checking, policy enforcement, coverage measurement, architectural drift detection, git-aware diff, multi-language adapters, or unrelated features unless this task explicitly asks for them.
Do not claim Postulate proves correctness.
Do not evaluate contract predicate strings as code.
Preserve the public CLI (check, prompt, ci, diff) unless a change is required by the task.
Add or update tests.
Keep the implementation simple and explicit.
```

Before moving to the next phase, run:

```bash
npm test
npm run build
node dist/index.js check examples/ts-late-fee/postulate.yaml
node dist/index.js ci examples/ts-late-fee/postulate.yaml
```

---

## Phase 0: Project Setup

### Goal

Get the TypeScript CLI into a runnable state.

### Tasks

- [x] Create `package.json` (`postulate`, bin `postulate`, Node `>=20`)
- [x] Create `tsconfig.json` (ESM, NodeNext, `src` → `dist`)
- [x] Create `src/` package
- [x] Create `docs/` folder
- [x] Create `.gitignore`
- [x] Configure vitest (`npm test`)
- [x] MIT license
- [x] CODEOWNERS

### Acceptance Criteria

```bash
npm install
npm test
```

passes.

---

## Phase 1: Spec Schema + Load

### Goal

Define the YAML spec contract and fail loudly on invalid files.

### Tasks

- [x] Implement Zod `PostulateSchema` / `ScenarioSchema` in `src/spec.ts`
- [x] Include fields from `SPEC.md`: `feature`, `owner`, `risk`, `contract`, `invariants`, `bdd`, `policies`, `test_mapping`, `correctness_argument`
- [x] Implement `loadSpec` in `src/loadSpec.ts`
- [x] `SpecLoadError` for missing file, invalid YAML, and Zod failures
- [x] Path-qualified Zod error messages
- [x] Mirror schema in `schemas/postulate.schema.json`

### Cursor Prompt

```text
Read docs/SPEC.md. Implement Phase 1 only.

Create the Zod spec schema and YAML loader with readable SpecLoadError messages.

Do not implement check, prompt, ci, diff, or the example.

Add tests for schema defaults and load failures.
```

### Acceptance Criteria

Loading a valid spec returns a typed object. Missing files, bad YAML, and schema failures exit as `SpecLoadError`.

---

## Phase 2: Structural Checks

### Goal

Enforce the v0.1 check table.

### Tasks

- [x] Implement `checkSpec` in `src/check.ts`
- [x] Error: high/critical risk requires at least one invariant
- [x] Error: every BDD `then` is non-empty
- [x] Error: every named invariant appears in `test_mapping`
- [x] Warning: high/critical risk should include `correctness_argument`
- [x] Warning: every BDD scenario name should appear in `test_mapping`
- [x] Warning: preconditions + postconditions >= 3
- [x] Info: recognised vs custom invariants
- [x] Implement `printCheckResult`
- [x] Wire `postulate check <spec-file>` (exit 1 on errors, exit 2 on load failure)
- [x] Tests in `tests/check.test.ts`

### Cursor Prompt

```text
Implement structural checks from docs/SPEC.md section 9.

Do not evaluate contract strings. Do not open test files named in test_mapping.
Add tests for each error and warning.
```

### Acceptance Criteria

```bash
npm test
node dist/index.js check examples/ts-late-fee/postulate.yaml
```

passes once the example exists. A spec that lists an unmapped invariant fails.

---

## Phase 3: Codegen Prompt

### Goal

Build an LLM prompt from a loaded spec. Do not call a model.

### Tasks

- [x] Implement `buildCodegenPrompt` in `src/prompt.ts`
- [x] Instruct: do not invent behavior; list ambiguities instead of guessing
- [x] Require implementation, BDD tests, invariant tests, correctness argument, remaining assumptions
- [x] Embed spec as JSON
- [x] Wire `postulate prompt <spec-file>`

### Cursor Prompt

```text
Implement postulate prompt from docs/SPEC.md section 11.

Print text to stdout. Do not call an LLM.
```

### Acceptance Criteria

```bash
node dist/index.js prompt examples/ts-late-fee/postulate.yaml
```

prints a prompt that contains the spec JSON and the required return shape.

---

## Phase 4: CI Command

### Goal

Same checks as `check`, with an opt-in stricter gate.

### Tasks

- [x] Wire `postulate ci <spec-file>`
- [x] `--fail-on-warnings` exits non-zero when warnings exist
- [x] Without the flag, warnings do not fail CI

### Cursor Prompt

```text
Add postulate ci. Reuse checkSpec. Do not duplicate check rules.
```

### Acceptance Criteria

`ci` without the flag matches `check` exit behavior for errors. With `--fail-on-warnings`, a warning-only spec exits 1.

---

## Phase 5: Spec Diff

### Goal

Flag spec regressions between two file paths.

### Tasks

- [x] Implement `diffSpecs` in `src/diff.ts`
- [x] Regression: dropped invariants, removed postconditions, removed BDD scenario names, removed policies, weakened risk
- [x] Improvement: the inverse
- [x] Implement `printDiffResult`
- [x] Wire `postulate diff <before> <after>` (exit 1 on regressions)
- [x] Tests in `tests/diff.test.ts`

### Cursor Prompt

```text
Implement postulate diff from docs/SPEC.md section 10.

Compare two file paths only. Do not add git refs.
Add tests for each regression and improvement class.
```

### Acceptance Criteria

```bash
npm test
```

Identical specs print "No material spec changes." Dropping an invariant exits 1.

---

## Phase 6: Known-Invariant Registry

### Goal

Recognise a small set of well-known names without giving them executable semantics yet.

### Tasks

- [x] Implement `KNOWN_INVARIANTS` / `KNOWN_INVARIANT_NAMES` in `src/invariants.ts`
- [x] Include `does_not_mutate_input`, `deterministic_output`, `deterministic_for_same_input`, `pure`, `idempotent`, `total`
- [x] `check` info-lists recognised vs custom names
- [x] Custom names remain valid if mapped in `test_mapping`

### Cursor Prompt

```text
Add the known-invariant registry from docs/SPEC.md section 12.

Do not generate property tests. Recognition is informational.
```

### Acceptance Criteria

A spec using `does_not_mutate_input` reports it as recognised. A custom name reports as custom and still requires `test_mapping`.

---

## Phase 7: Worked TypeScript Example + Repo CI

### Goal

Show the full workflow on one feature.

### Tasks

- [x] `examples/ts-late-fee/postulate.yaml`
- [x] `examples/ts-late-fee/lateFee.ts`
- [x] `examples/ts-late-fee/lateFee.test.ts` covering BDD scenarios, named invariants, and failure cases
- [x] `test_mapping` complete for invariants and scenarios
- [x] GitHub Actions: build, test, `postulate ci` on the example
- [x] `docs/framework.md` and `docs/pr-template.md`
- [x] Root README and ROADMAP

### Cursor Prompt

```text
Add the late-fee example from docs/SPEC.md. Map every invariant and scenario to a test.
Wire GitHub Actions as specified. Do not add more examples.
```

### Acceptance Criteria

```bash
npm test
npm run build
node dist/index.js check examples/ts-late-fee/postulate.yaml
node dist/index.js ci examples/ts-late-fee/postulate.yaml
```

passes.

---

## Phase 8: Test and Schema Hardening

### Goal

Close gaps in v0.1 so later phases do not rest on untested load/prompt/CLI paths or a drifting JSON Schema.

### Tasks

- [ ] Add `tests` for `loadSpec`: missing file, invalid YAML, schema failure messages, happy path
- [ ] Add `tests` for `buildCodegenPrompt`: required sections, spec JSON embedded, no invented behavior instruction
- [ ] Add CLI tests (or subprocess tests) for `check` / `ci` / `prompt` / `diff` exit codes
- [ ] Add a test that `schemas/postulate.schema.json` stays consistent with `PostulateSchema` (or document a generation step and use it)
- [ ] Cover `ci --fail-on-warnings` exit behavior

### Cursor Prompt

```text
Read docs/SPEC.md and docs/TASKS.md. Implement Phase 8 only.

Add tests for loadSpec, prompt, CLI exit codes, and schema consistency.
Do not add property-test generation, policy enforcement, git diffs, or new commands.
```

### Acceptance Criteria

```bash
npm test
npm run build
node dist/index.js check examples/ts-late-fee/postulate.yaml
node dist/index.js ci examples/ts-late-fee/postulate.yaml --fail-on-warnings
```

passes, and a deliberately invalid spec file fails load with a path-qualified message.

---

## Phase 9: Property Tests from Named Invariants

### Goal

Named invariants such as `does_not_mutate_input` generate property-test scaffolds instead of requiring the author to write the property by hand.

### Tasks

- [ ] Pair each known invariant with a generator description
- [ ] Generate a test scaffold (likely fast-check) from recognised names
- [ ] Keep custom invariants as author-written tests via `test_mapping`
- [ ] Document how generated tests relate to `test_mapping`
- [ ] Tests for generation output; do not require live LLM calls

### Cursor Prompt

```text
Read docs/SPEC.md and ROADMAP.md. Implement Phase 9 only.

Generate property-test scaffolds for known invariants.
Do not implement policy enforcement, coverage, drift, git diff, or language adapters.
```

### Acceptance Criteria

A spec that lists `does_not_mutate_input` can produce a scaffold that asserts arguments are unchanged. Custom invariants are not auto-generated.

---

## Phase 10: Policy Enforcement

### Goal

Policies like `no_network_calls` fail CI instead of remaining declarations.

### Tasks

- [ ] Start with semgrep and/or eslint-based checks
- [ ] Map known policy names to concrete rules
- [ ] Fail `postulate ci` (or a dedicated command) on violations
- [ ] Leave room for optional OPA/Rego later; do not require it in this phase unless the task is split
- [ ] Tests use fixtures, not production codebases

### Cursor Prompt

```text
Implement Phase 10 only: policy enforcement for declared policies.

Start with semgrep/eslint-style checks. Do not add OPA unless needed for the chosen design (then write an ADR).
Do not add coverage, drift, git diff, or language adapters.
```

### Acceptance Criteria

A spec that declares `no_network_calls` fails CI when the mapped implementation makes a network call in the fixture. Specs with no policies are unchanged.

---

## Phase 11: Coverage Measurement

### Goal

Catch behaviors that exist in the spec but are no longer exercised by the test suite.

### Tasks

- [ ] Compare declared invariants and BDD scenarios against tests that actually ran
- [ ] Report spec names with no executed mapping
- [ ] Tests use a recorded/fake test-run summary, not a mandatory live vitest integration in unit tests

### Cursor Prompt

```text
Implement Phase 11 only: coverage of spec names vs tests that ran.

Do not add architectural drift, git diff, or language adapters.
```

### Acceptance Criteria

If `test_mapping` points at a test that did not run, the coverage command/report flags that name.

---

## Phase 12: Architectural Drift Detection

### Goal

Refactors that quietly move boundaries between modules, layers, or services show up as explicit drift.

### Tasks

- [ ] Define how structural expectations are declared in the spec (ADR required)
- [ ] Compare the current codebase against those expectations
- [ ] Fail or warn per the ADR
- [ ] Tests use a small fixture tree

### Cursor Prompt

```text
Implement Phase 12 only. Write an ADR for how structural expectations are declared before coding.
Do not add git-aware diff or language adapters.
```

### Acceptance Criteria

A fixture that violates the declared structure is reported. A matching fixture is not.

---

## Phase 13: Git-Aware Diff

### Goal

`postulate diff` can compare against a git reference so CI does not need a manual checkout of the previous spec.

### Tasks

- [ ] Keep two-path `postulate diff <before> <after>`
- [ ] Add git ref support (for example `postulate diff HEAD~1 path/to/postulate.yaml` or `postulate diff --git HEAD~1 <spec-file>`)
- [ ] Document the chosen CLI in an ADR if it changes the public interface
- [ ] Tests use a temporary git repo fixture, not the developer's working tree

### Cursor Prompt

```text
Implement Phase 13 only: git-aware spec diff.

Preserve existing two-file diff behavior.
Do not add language adapters.
```

### Acceptance Criteria

In a git fixture, dropping an invariant between `HEAD~1` and `HEAD` exits 1. Two-file diff still works.

---

## Phase 14: Multi-Language Adapters

### Goal

Keep the YAML spec language-neutral while adding adapters for test discovery, test generation, and policy checks.

### Tasks

- [ ] Document the adapter interface (ADR)
- [ ] Keep the TypeScript CLI as the reference implementation
- [ ] Add at least one additional language adapter (start with one; do not boil the ocean)
- [ ] Tests per adapter with fixtures

### Cursor Prompt

```text
Implement Phase 14 only for the first additional language adapter agreed in an ADR.

Do not rewrite the spec format. Do not add languages beyond the one chosen for this phase.
```

### Acceptance Criteria

The same YAML spec can be checked by the TS CLI. The new adapter can discover or generate tests for that spec in its language without changing the YAML schema.

---

## Status

| Phase | Name | Status |
| --- | --- | --- |
| 0 | Project setup | Complete |
| 1 | Spec schema + load | Complete |
| 2 | Structural checks | Complete |
| 3 | Codegen prompt | Complete |
| 4 | CI command | Complete |
| 5 | Spec diff | Complete |
| 6 | Known-invariant registry | Complete |
| 7 | Worked example + repo CI | Complete |
| 8 | Test and schema hardening | **Next** |
| 9 | Property tests from named invariants | Planned |
| 10 | Policy enforcement | Planned |
| 11 | Coverage measurement | Planned |
| 12 | Architectural drift detection | Planned |
| 13 | Git-aware diff | Planned |
| 14 | Multi-language adapters | Planned |
