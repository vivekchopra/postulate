# 0014. Python adapter as a first-class package

- Status: Accepted
- Date: 2026-08-31
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

The YAML spec format is language-neutral ([0010](0010-language-neutral-spec.md)), but the only implementation is a TypeScript CLI. Python consumers such as webcheck-api must install Node, build Postulate, and still cannot validate `test_mapping` against pytest.

Without a native Python package, "multi-language adapters" stays a roadmap bullet and spec-anchored workflows cannot land in Python codebases.

## Decision

Add a Python adapter under `adapters/python/` and publish it to PyPI as **`postulate`**.

- Python 3.11+, Pydantic v2, Typer (or argparse if Typer is unnecessary), PyYAML.
- Console script: `postulate` with the same subcommands as the TypeScript CLI: `check`, `prompt`, `ci`, `diff`.
- Structural check, prompt, diff, and CI semantics match the TypeScript reference implementation.
- The TypeScript CLI remains the reference implementation for the Node/TypeScript ecosystem; behavioral parity is tested, not code sharing.

Package layout:

```text
adapters/python/
  pyproject.toml
  src/postulate/
    __init__.py
    models.py          # Pydantic PostulateSpec
    load_spec.py
    check.py
    diff.py
    prompt.py
    invariants.py
    cli.py
  tests/
```

## Consequences

- Python repos can `pip install postulate` and run spec checks without Node.
- Two implementations must stay in sync when structural rules change; add parity tests or a shared fixture corpus.
- Ruby/Go adapters follow the same pattern later; do not fork the YAML schema per language.
- Implementation is tracked in [`plans/python-adapter/`](../plans/python-adapter/PLAN.md).

## Alternatives considered

- Shell out to the Node CLI from Python — couples Python CI to Node anyway; poor DX.
- Replace the TypeScript CLI with Python only — abandons the TypeScript example and existing npm workflow.
- Single polyglot binary (e.g. WASM) — over-engineered for v0.2.
