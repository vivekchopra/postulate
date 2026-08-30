# 0008. Commander CLI with check, prompt, ci, diff

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

The workflow needs a small CLI: validate, produce a codegen prompt, gate CI, and compare spec versions.

## Decision

Use `commander`. Public commands in v0.1:

- `postulate check <spec-file>`
- `postulate prompt <spec-file>`
- `postulate ci <spec-file> [--fail-on-warnings]`
- `postulate diff <before> <after>`

Load failures exit 2. Check/CI/diff failures exit 1.

## Consequences

New verbs (coverage, policy, git diff) need a CLI design and usually an ADR. Do not overload `check` with those jobs.

## Alternatives considered

- Single `postulate <file>` command with flags — harder to explain in CI and docs.
- yargs / custom argv — commander is enough for four commands.
