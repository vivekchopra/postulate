# Python Adapter Acceptance

Done is defined per milestone. Do not mark a milestone complete until its section passes.

---

## Milestone A acceptance

From repository root:

```bash
# TypeScript reference (must still pass)
npm test
npm run build

# Python adapter
cd adapters/python
pip install -e ".[dev]"
pytest
postulate check ../../examples/ts-late-fee/postulate.yaml    # structural only; TS locator strings may warn on verify
postulate prompt ../../examples/ts-late-fee/postulate.yaml | head -20
```

From `adapters/python/examples/minimal-pytest/`:

```bash
pip install -e "../..[dev]"
postulate check postulate.yaml
postulate verify postulate.yaml --project-root .
```

All commands exit `0` except where a negative test is explicitly run.

### Behavioral acceptance (Milestone A)

Without network access:

- Python `check` produces the same errors/warnings as TypeScript on shared fixtures in `adapters/fixtures/specs/`
- `verify` fails when a `test_mapping` locator does not exist in pytest collection
- `verify` passes when every invariant maps to a collected node ID in the minimal example
- `ci --fail-on-warnings` matches TypeScript semantics
- `diff` matches TypeScript on shared before/after fixture pairs
- Load failures exit `2` with field paths

### Scope acceptance (Milestone A)

Review the diff and confirm:

- no YAML schema field additions or removals
- no changes to TypeScript check severity without an ADR
- no git-aware diff yet
- no pytest plugin yet
- no policy enforcement yet
- no webcheck-api files in this repo

---

## Milestone B acceptance

```bash
# Python
cd adapters/python
pytest
postulate diff --git HEAD~1 examples/minimal-pytest/postulate.yaml   # in fixture repo with git history
pytest --postulate-spec examples/minimal-pytest/postulate.yaml

# TypeScript
cd ../../
npm test
node dist/index.js diff --git HEAD~1 examples/ts-late-fee/postulate.yaml   # when spec unchanged at ref, or use fixture repo
```

### Behavioral acceptance (Milestone B)

- `diff --git` detects a dropped invariant between ref and working tree
- Two-file `diff` still works unchanged
- pytest plugin fails when a mapped test was not executed in the session
- pytest plugin passes when all invariant mappings ran

### Scope acceptance (Milestone B)

- no policy enforcement
- no `init` command required
- webcheck pilot still out of scope for postulate repo

---

## Milestone C acceptance (when implemented)

- `postulate policies check` reports violations for fixture code that breaks `unit_tests_stay_offline`
- `postulate init` creates a valid skeleton spec
- ADR 0019 merged

---

## Milestone D acceptance (webcheck-api repo)

In webcheck-api:

```bash
pip install postulate   # or path dep until PyPI
postulate verify specs/safety/postulate.yaml --project-root .
pytest --postulate-spec specs/safety/postulate.yaml
```

Existing `pytest` suite still passes. PR that removes a mapped invariant without updating the spec fails `postulate diff --git`.

---

## Parity regression gate (ongoing)

CI must run both:

```bash
npm test
cd adapters/python && pytest
```

On every PR touching `src/` or `adapters/python/`.
