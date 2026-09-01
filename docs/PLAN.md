# Postulate Project Build Order

This file records project-level sequencing. It is not the implementation plan for an individual change. Change-specific plans live under `docs/plans/<change>/`.

## Product sentence

Postulate is a framework for specifying and validating software behavior in AI-assisted development. You postulate the contract before code is generated, and everything that follows is judged against it.

## Build order

1. YAML spec schema + Zod validation
2. `check`: structural rules
3. `prompt`: LLM codegen prompt from a spec
4. `ci`: check with optional `--fail-on-warnings`
5. `diff`: spec regression detection
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
write spec -> postulate check -> postulate prompt -> LLM writes code & tests -> postulate ci -> review -> merge
                                                                                     ^
                                                             postulate diff for subsequent changes
```

The spec format stays language-neutral. The v0.1 implementation is TypeScript-first.

## Current change

Test and schema hardening is tracked in [`plans/test-hardening/`](plans/test-hardening/).

## Shipped in v0.1

Phases 0-7 are complete:

- YAML spec schema with Zod validation and readable errors
- `check`, `prompt`, `ci`, and `diff`
- a small registry of well-known invariants
- a worked TypeScript late-fee example covering named invariants and failure cases

## Next

After test/schema hardening, follow [`ROADMAP.md`](../ROADMAP.md). Each substantial roadmap item should get its own plan folder before implementation. Write an ADR first when the change introduces a durable design decision.

## Non-goals unless an ADR supersedes them

Do not build:

- a theorem prover or model checker
- weakest-precondition proofs
- a guarantee of correctness
- a replacement for engineering judgment
- a general-purpose test runner
- a language-specific linter as the spec format
