# 0002. Spec first

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

AI makes generating code cheap. The failure mode is implementing first and writing a spec that matches whatever shipped. Postulate exists to invert that order.

## Decision

The workflow is: write spec → `check` → `prompt` → LLM writes code and tests → `ci` → review → merge. Subsequent changes use `diff`.

The spec is the artifact that constrains generation. Code is judged against it, not the other way around.

## Consequences

Features that skip a spec are out of scope for the Postulate workflow. `prompt` is generated from the spec, not from existing code. See [0012](0012-prompt-constrains-codegen.md).

## Alternatives considered

- Code-first with inferred specs — would rubber-stamp generated behavior.
- Specs as comments in source — not reviewable or diffable as a first-class artifact.
