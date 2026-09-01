# Cursor Prompts: Test and Schema Hardening

These prompts are intentionally bounded. Run one phase at a time and review the diff before continuing.

## Phase 1: loader and prompt tests

```text
Read docs/ARCHITECTURE.md and docs/plans/test-hardening/{PLAN,SPEC,TASKS,ACCEPTANCE}.md.

Implement only loader and prompt test coverage.
Do not modify product behavior or the Postulate YAML contract.
Do not add new commands or roadmap features.

Run the relevant tests, then stop. Summarize files changed and any unresolved assumption.
```

## Phase 2: CLI tests

```text
Read docs/ARCHITECTURE.md and docs/plans/test-hardening/{PLAN,SPEC,TASKS,ACCEPTANCE}.md.

Implement only subprocess coverage for check, ci, prompt, and diff exit behavior, including ci --fail-on-warnings.
Do not refactor the CLI unless a test cannot be written against its current public behavior.
Do not add new commands or roadmap features.

Run the relevant tests, then stop. Summarize files changed and any unresolved assumption.
```

## Phase 3: schema mirror

```text
Read docs/ARCHITECTURE.md and docs/plans/test-hardening/{PLAN,SPEC,TASKS,ACCEPTANCE}.md.

Implement only the JSON Schema consistency test and correct schemas/postulate.schema.json where it disagrees with src/spec.ts.
src/spec.ts is the runtime source of truth for this phase.
Do not change the YAML contract and do not add a schema-generation dependency.

Run the relevant tests, then stop. Summarize files changed and any unresolved assumption.
```

## Phase 4: acceptance

```text
Read docs/plans/test-hardening/ACCEPTANCE.md.

Do not add features. Run every acceptance command and report each result.
If something fails, fix only defects within this plan's scope and rerun the failing acceptance check.
Stop when acceptance is complete.
```
