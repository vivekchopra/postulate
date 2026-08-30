# 0010. Language-neutral spec, TypeScript-first implementation

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

The spec needs to sit next to Python, Go, Ruby, and TypeScript code. Encoding it as TypeScript types would lock the format to one ecosystem.

## Decision

The spec format is plain YAML. Any language can produce one. The reference CLI and first example are TypeScript. Language-specific adapters (test discovery, generation, policy checks) are Phase 14.

## Consequences

Do not put TypeScript-only constructs in the YAML schema. Locator strings in `test_mapping` stay opaque. Adapters must not fork the schema.

## Alternatives considered

- TypeScript-only specs (`.ts` exporting a spec object) — easier for this repo, unusable elsewhere.
- Per-language spec formats — defeats `diff` and shared CI.
