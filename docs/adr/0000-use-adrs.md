# 0000. Record design changes as ADRs

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

v0.1 shipped as a single commit with design intent spread across README, ROADMAP, and code comments. That is enough for a tiny CLI and unusable once schema, CLI, and check severity start changing independently.

## Decision

Record locked design changes as Architecture Decision Records under `docs/adr/`.

- One decision per file: `NNNN-short-kebab-title.md`
- Flat directory; status lives in the file, not in folder names
- Never delete an ADR; mark it Superseded and link the replacement
- Do not keep a parallel living `DECISIONS.md`

## Consequences

New work that changes the spec schema, CLI contract, check severity, or invariant semantics should add or update an ADR in the same change. Product spec and task lists remain separate.

## Alternatives considered

- Keep decisions only in README/ROADMAP — cheaper at nine items, no status or supersession trail.
- Nested `accepted/` / `proposed/` folders — status changes require moves and break links.
