# Cursor Prompts: Python Adapter

Read first:

- `docs/ARCHITECTURE.md`
- `docs/plans/python-adapter/{PLAN,SPEC,TASKS,ACCEPTANCE}.md`
- `docs/adr/0014-python-adapter-package.md` through `0016-verify-command.md` (Milestone A)
- `docs/adr/0017-git-aware-diff.md` and `0018-pytest-plugin-exercised-mapping.md` (Milestone B)

Implement **one milestone at a time**. Run that milestone's acceptance checks before continuing.

---

## Milestone A: Python CLI + verify

```text
You are working on Postulate.

Read docs/ARCHITECTURE.md, docs/plans/python-adapter/, and ADRs 0014-0016.

Implement Milestone A only: Python package under adapters/python/ with check, ci, prompt, diff, and verify.

Before coding, state:
1. the milestone and tasks you selected (A1-A6),
2. what is in scope,
3. what is explicitly out of scope (git diff, pytest plugin, policies, webcheck-api, YAML schema changes),
4. files you expect to create or modify,
5. tests you will add.

Constraints:
- Match TypeScript structural check, ci, prompt, and diff behavior on shared fixtures.
- verify uses pytest --collect-only; do not execute tests.
- test_mapping locators use pytest node IDs (path::test_name).
- Do not change src/spec.ts or the YAML contract.
- Do not implement Milestone B or C features.
- Add parity tests; no network access in unit tests.
- Update docs/ARCHITECTURE.md when the Python adapter lands.

Definition of done:
- Milestone A acceptance in docs/plans/python-adapter/ACCEPTANCE.md passes.
- Summarize files changed and how to run Python tests locally.
```

---

## Milestone B: Git diff + pytest plugin

```text
You are working on Postulate.

Read docs/plans/python-adapter/ and ADRs 0017-0018.

Verify Milestone A acceptance still passes before starting.

Implement Milestone B only:
- postulate diff --git <ref> <spec-file> in Python and TypeScript
- pytest plugin --postulate-spec

Before coding, state scope, out-of-scope items, files, and tests.

Constraints:
- Preserve two-file diff behavior.
- Git mode uses local git show; no network fetch.
- Plugin checks exercised node IDs after session; does not replace verify.
- No policy enforcement or init command.
- Add tests with git and pytester fixtures.

Definition of done:
- Milestone B acceptance passes.
- npm test and adapters/python pytest both pass.
```

---

## Milestone C: Policies + init

```text
You are working on Postulate.

Read docs/plans/python-adapter/ Milestone C and write ADR 0019 before implementing policy rules.

Implement Milestone C only: policy pack (unit_tests_stay_offline, no_secrets_in_output) and postulate init.

Do not add OPA/Rego. Heuristics may warn by default; document false positives.

Definition of done:
- Milestone C acceptance passes.
- ADR 0019 merged.
```

---

## Milestone D: webcheck-api pilot (consumer repo)

```text
You are working on webcheck-api, not the postulate repository.

Prerequisites: postulate PyPI package (or editable install) with verify and pytest plugin.

Read webcheck-api docs/adr/0011-unit-tests-stay-offline.md and 0012-no-secrets-in-output.md.

Implement Milestone D only:
- specs/safety/postulate.yaml mapped to tests/test_safety.py
- postulate verify in CI
- pytest --postulate-spec in CI

Do not map docs/CHECKS.md scanner IDs into Postulate.
Do not change scanner behavior.

Definition of done:
- Milestone D acceptance in postulate docs/plans/python-adapter/ACCEPTANCE.md passes in webcheck-api.
```

---

## Parity fix prompt

```text
Parity test failed between TypeScript and Python Postulate implementations.

Fixture: <name>
Expected: <behavior>
Actual TS: <output>
Actual Python: <output>

Fix only the incorrect implementation(s). Update shared fixture documentation if the contract was ambiguous.
Do not add new features. Rerun npm test and adapters/python pytest.
```

---

## Post-milestone review

```text
Review the implementation against:
- docs/plans/python-adapter/SPEC.md
- docs/plans/python-adapter/ACCEPTANCE.md
- ADRs 0014-0018

Check for:
- YAML schema changes without ADR
- broken TypeScript/Python parity
- verify running tests instead of collecting
- plugin conflated with verify
- webcheck CHECKS.md mapping (should not exist)
- network-dependent unit tests
- scope creep into property-test generation or OPA

Fix only blockers for the current milestone acceptance. List future improvements without implementing them.
```
