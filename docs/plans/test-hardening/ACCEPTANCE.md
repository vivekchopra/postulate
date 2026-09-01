# Test and Schema Hardening Acceptance

This file defines done independently of the implementation approach.

## Automated acceptance

From the repository root:

```bash
npm install
npm test
npm run build
node dist/index.js check examples/ts-late-fee/postulate.yaml
node dist/index.js ci examples/ts-late-fee/postulate.yaml --fail-on-warnings
```

All commands must exit `0`.

## Behavioral acceptance

The automated suite must demonstrate all of the following without network access:

- valid YAML loads successfully;
- a missing spec fails as `SpecLoadError`;
- malformed YAML fails as `SpecLoadError`;
- schema validation errors include the failing field path;
- `check` returns the documented success/failure/load-failure exit codes;
- warning-only `ci` exits `0` normally and `1` with `--fail-on-warnings`;
- `prompt` emits the spec plus the required implementation/test/correctness instructions;
- `diff` exits `1` for a regression;
- the JSON Schema mirror matches the tested runtime-schema constraints.

## Scope acceptance

Review the diff and confirm:

- no `src/` implementation behavior changed;
- no new public command was added;
- no YAML field was added or removed;
- no property-test generation, policy enforcement, coverage measurement, semantic diff, architecture-drift logic, git integration, or language adapter was introduced.
