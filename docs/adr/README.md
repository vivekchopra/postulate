# Architecture Decision Records

ADRs are an append-only log of design choices. One decision per file. Never delete an ADR; mark it **Superseded** and point at the replacement.

## Index

| ID | Title | Status |
| --- | --- | --- |
| [0000](0000-use-adrs.md) | Record design changes as ADRs | Accepted |
| [0001](0001-typescript-cli.md) | TypeScript CLI | Accepted |
| [0002](0002-spec-first.md) | Spec first | Accepted |
| [0003](0003-yaml-zod.md) | YAML specs validated by Zod | Accepted |
| [0004](0004-structural-not-formal.md) | Structural checks, not formal verification | Accepted |
| [0005](0005-named-invariant-registry.md) | Named invariant registry; custom names allowed | Accepted |
| [0006](0006-test-mapping-enforcement.md) | Every invariant must map to a test | Accepted |
| [0007](0007-policies-are-declarations.md) | Policies are declarations until enforced | Accepted |
| [0008](0008-commander-four-commands.md) | Commander CLI with check, prompt, ci, diff | Accepted |
| [0009](0009-diff-two-files.md) | Diff compares two file paths | Accepted |
| [0010](0010-language-neutral-spec.md) | Language-neutral spec, TypeScript-first implementation | Accepted |
| [0011](0011-risk-based-rules.md) | Risk drives required invariants and correctness argument | Accepted |
| [0012](0012-prompt-constrains-codegen.md) | Prompt constrains codegen; CLI does not call a model | Accepted |
| [0013](0013-warnings-opt-in-ci.md) | Warnings fail CI only with --fail-on-warnings | Accepted |
| [0014](0014-python-adapter-package.md) | Python adapter as a first-class PyPI package | Accepted |
| [0015](0015-pytest-test-mapping-locator.md) | Pytest locator grammar for test_mapping | Accepted |
| [0016](0016-verify-command.md) | verify command for mapped-test existence | Accepted |
| [0017](0017-git-aware-diff.md) | Git-aware spec diff | Accepted |
| [0018](0018-pytest-plugin-exercised-mapping.md) | Pytest plugin for exercised spec mapping | Superseded by [0020](0020-pytest-execution-coverage.md) |
| [0019](0019-policy-pack-heuristics.md) | Policy pack heuristics (Python) | Accepted |
| [0020](0020-pytest-execution-coverage.md) | Measure execution of every declared pytest claim | Accepted |
| [0021](0021-git-diff-input-boundary.md) | Git diff input boundary and PR baseline | Accepted |

## Conventions

- Filename: `NNNN-short-kebab-title.md` (4-digit id, assigned once, never reused).
- Status: `Proposed` → `Accepted` → `Deprecated` or `Superseded`.
- Do not nest by status or topic. Status and links live in the file.
- One decision per ADR. Related but distinct choices get separate files.
- If a PR changes the spec schema, CLI contract, check severity, or invariant semantics, include an ADR in the same PR.
- Copy [`template.md`](template.md). Do not number the template.

## How to add one

1. Take the next free id from this index.
2. Copy `template.md` to `NNNN-title.md`.
3. Fill Context, Decision, Consequences, and real alternatives.
4. Add a row to the table above.
5. Merge as `Accepted` unless the decision is still under review.
