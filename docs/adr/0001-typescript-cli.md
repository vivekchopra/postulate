# 0001. TypeScript CLI

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

The first implementation needs one language for schema validation, CLI, and tests. The spec format itself is language-neutral YAML.

## Decision

Implement the v0.1 CLI in TypeScript on Node.js 20+, published (when published) as `@postulate/cli` with binary `postulate`. Use ESM, Zod, commander, and vitest.

## Consequences

Contributors to the reference CLI work in TypeScript. Other languages consume YAML specs; they do not need this package until adapters exist ([0010](0010-language-neutral-spec.md)).

## Alternatives considered

- Python — fine for CLIs, but the first worked example and typical AI-codegen target in this repo is TypeScript.
- Split languages (TS schema + another CLI) — duplicated models.
