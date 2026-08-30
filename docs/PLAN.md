# Postulate Build Plan

## Product sentence

Postulate is a framework for specifying and validating software behavior in AI-assisted development. You postulate the contract before code is generated, and everything that follows is judged against it.

## Build order

1. YAML spec schema + Zod validation
2. `check` — structural rules
3. `prompt` — LLM codegen prompt from a spec
4. `ci` — check with optional `--fail-on-warnings`
5. `diff` — spec regression detection
6. Known-invariant registry
7. Worked TypeScript example
8. Test/schema hardening
9. Property tests from named invariants
10. Policy enforcement
11. Coverage measurement
12. Architectural drift detection
13. Git-aware diff
14. Multi-language adapters

```text
write spec → postulate check → postulate prompt → LLM writes code & tests → postulate ci → review → merge
                                                                                    ↑
                                                            postulate diff for subsequent changes
```

The spec format stays language-neutral. The v0.1 implementation is TypeScript-first.

## v0.1 demo goal

```bash
npm install
npm run build
node dist/index.js check examples/ts-late-fee/postulate.yaml
node dist/index.js prompt examples/ts-late-fee/postulate.yaml
node dist/index.js ci examples/ts-late-fee/postulate.yaml --fail-on-warnings
npm test
```

A reviewer should be able to read `examples/ts-late-fee/postulate.yaml`, see every named invariant mapped to a test, and run `postulate check` / `postulate ci` without reading the implementation first.

## v0.1 shipped

Phases 0–7 in [`TASKS.md`](TASKS.md) are complete. What ships today:

- YAML spec schema with Zod validation and readable errors
- `check`, `prompt`, `ci`, `diff`
- A small registry of well-known invariants
- A worked TypeScript late-fee example covering named invariants and failure cases

## Next

Close test/schema gaps, then the roadmap: generated property tests, policy enforcement, coverage, architectural drift, git-aware diff, and language adapters. See [`TASKS.md`](TASKS.md).

## Non-goals (all versions unless an ADR supersedes)

Do not build:

- A theorem prover or model checker
- Weakest-precondition proofs
- A guarantee of correctness
- A replacement for engineering judgment
- A general-purpose test runner
- A language-specific linter as the spec format
