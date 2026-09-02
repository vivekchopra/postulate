# Pytest coverage tasks

All work is pending. Acceptance IDs refer to [ACCEPTANCE.md](ACCEPTANCE.md).

## P0. Establish baseline

- [x] Read current architecture, ADRs 0015/0016/0018 and proposed 0020; inspect current code before applying this plan.
- [x] Install the adapter in an isolated environment and record Python/pytest versions and baseline test results.
- [x] Add regressions showing absent mappings, skipped mapped tests, and colliding `tests/` suffixes can currently pass. Do not alter production code yet.
- [x] Record expected failures and unrelated baseline failures separately.

Acceptance: P-01, P-03, P-06 must expose the intended gaps before their fixes.

## P1. Make mapping identity complete and exact

- [x] Enumerate claims, including absent/blank mappings; preserve error/warning distinction and shared-name precedence.
- [x] Warn on unknown mapping keys regardless of locator resolution.
- [x] Normalize only path components and enforce root-relative node IDs; remove suffix matching and `/tests/` truncation.
- [x] Preserve parameter text and document exact-case versus base matching.
- [x] Share matching with verify; align its collection root with `--project-root` and deduplicate structural/mapping diagnostics.
- [x] Add focused mapping and verify tests for P-01 through P-07.

## P2. Observe execution and preserve pytest behavior

- [x] Load/schema-validate the spec once before tests; reject unsupported collection-only and active distributed modes with actionable usage errors.
- [x] Record eligible call reports, with enough non-sensitive state to explain skip/setup-failure cases.
- [x] Report per-category counts, missing claims, and mapping warnings in stable order.
- [x] Preserve all preexisting nonzero exit statuses and change only otherwise-successful sessions on coverage failure.
- [x] Support missing terminal reporter without crashing; emit no Postulate output without the flag.
- [x] Add phase/outcome, exit-status, and no-op regressions for P-08 through P-14.

## P3. Prove installed-plugin behavior and document migration

- [x] Run real pytest subprocesses with plugin entry-point discovery; cover full, targeted, skipped, failed, and no-tests sessions.
- [x] Demonstrate the user example in a small local fixture, including `no_secrets_in_output` as an invariant with a mapped pytest node.
- [x] Document that the flag is attached to the actual test invocation, not a second invocation after tests.
- [x] Document root paths, partial parameter coverage, skip/xfail semantics, strict warning flag, unsupported modes, and execution versus passing.
- [x] Remove the duplicate plugin invocation from the existing CI job; do not change unrelated CI setup.
- [x] Update architecture and ADR statuses with the actual implementation; mark ADR 0018 superseded only when 0020 is accepted.
- [x] Run P-15; record results, changed files, and any remaining failures in implementation notes.
