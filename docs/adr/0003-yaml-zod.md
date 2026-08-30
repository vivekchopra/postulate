# 0003. YAML specs validated by Zod

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

Authors need a file they can write by hand next to code. The CLI needs typed, defaulted objects and readable errors.

## Decision

Specs are YAML documents. Runtime validation is Zod (`PostulateSchema` in `src/spec.ts`). `loadSpec` parses YAML then runs Zod. `schemas/postulate.schema.json` is a mirror for editors; Zod is authoritative.

## Consequences

Invalid specs never reach `check` / `prompt` / `diff`. Schema drift between Zod and JSON Schema is a maintenance risk — Phase 8 in `TASKS.md` closes that gap.

## Alternatives considered

- JSON only — worse to write by hand; YAML is the author format.
- JSON Schema as the only validator — weaker TypeScript inference than Zod.
- TOML / custom DSL — extra learning cost for no gain at v0.1.
