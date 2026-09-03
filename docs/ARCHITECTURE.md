# Postulate Architecture

This document describes the current Python adapter pytest coverage behavior and the TypeScript/Python CLI surfaces. Decision rationale is in `docs/adr/`; change plans live under `docs/plans/`.

## System boundary

Postulate loads YAML specs, validates structure, renders implementation prompts, and compares specs for structural regressions. Its Python adapter also resolves mapped tests through pytest collection, observes reports from a pytest run, scans selected policy heuristics, and scaffolds specs.

It does not prove correctness, evaluate contract expressions, call an LLM, or replace pytest. Collection can import project code and execute collection hooks; it is not a sandbox. The plugin observes tests run by pytest on the **same invocation** that carries `--postulate-spec`; it does not launch a second test run.

## Implementations

| Surface | Location | Current commands |
| --- | --- | --- |
| TypeScript reference | `src/` | `check`, `prompt`, `ci`, `diff`, `diff --git` |
| Python adapter | `adapters/python/` | Shared commands plus `verify`, `policies check`, `init`; pytest plugin |

The YAML shape is modeled in Zod (`src/spec.ts`) and Pydantic (`adapters/python/src/postulate/models.py`). The checked-in JSON Schema supports tooling; consistency/parity tests cover selected cases. Schema generation is not implemented.

## Responsibilities

| Concern | TypeScript | Python |
| --- | --- | --- |
| CLI and exit behavior | `index.ts` | `cli.py` |
| YAML and schema loading | `loadSpec.ts`, `spec.ts` | `load_spec.py`, `models.py` |
| Structural rules | `check.ts`, `invariants.ts` | `check.py`, `invariants.py` |
| Prompt rendering | `prompt.ts` | `prompt.py` |
| Structural diff | `diff.ts` | `diff.py` |
| Historical spec loading | `gitDiff.ts` | `git_diff.py` |
| Collection, locator resolution, claim enumeration | None | `verify.py`, `mapping.py` |
| Pytest session exercise observation | None | `pytest_plugin.py` |
| Policy heuristics and spec scaffolding | None | `policies.py`, `init_cmd.py` |

Python files in this table are under `adapters/python/src/postulate/`.

## Current flows

`check` and `ci` load a spec and apply structural rules. `ci` can promote warnings. `prompt` loads the spec and prints a constrained prompt; it invokes no model.

`verify` runs structural checks, launches `python -m pytest --collect-only -q --rootdir=<project-root>`, parses node IDs, and checks that mapped locators resolve in collection output. It does not run test bodies. Missing invariant mapping keys are reported by structural `check`; `verify` adds blank/unresolved locator diagnostics without duplicating structural missing-key messages.

The pytest entry point is `postulate_exercise = postulate.pytest_plugin` (pytest 11 entry-point discovery). Without `--postulate-spec` the plugin registers nothing and emits no output. With the flag:

1. **Configure:** load and schema-validate the spec once; reject `--collect-only` and active xdist with usage errors (exit 4).
2. **Run:** record non-skipped `call` reports (passed or failed) as exercised node IDs; record setup/call skip and setup failure hints for diagnostics.
3. **Finish:** evaluate every declared invariant and BDD scenario via `mapping.check_exercise_coverage`; print category counts; preserve nonzero pytest exit statuses; change **0 → 1** only when coverage fails or warnings are promoted.

Invariant gaps are errors; BDD-only gaps are warnings unless `--postulate-fail-on-warning` is set. Unknown `test_mapping` keys always warn. Locators are exact root-relative pytest node IDs shared with `verify` ([ADR 0020](adr/0020-pytest-execution-coverage.md)).

`diff --git` discovers the Git worktree from the **invocation cwd** (not from the directory of an absolute path alone). It resolves one commit with `git rev-parse --verify --end-of-options <ref>^{commit}`, reads that blob at the same repository-relative path as the working file, then calls the same comparator as two-file diff. The working path must be a regular file inside the discovered repository; symlinked specs and paths outside the repo are rejected (exit 2). Missing Git, bad refs, and absent historical/working files are exit 2. The command does not fetch, check out, or mutate repository state ([ADR 0021](adr/0021-git-diff-input-boundary.md)).

`policies check` applies Python heuristics for `unit_tests_stay_offline` and `no_secrets_in_output`. `init` creates a skeleton spec and can suggest mappings from pytest collection.

## Tests and documentation

TypeScript tests live in `tests/` and `examples/ts-late-fee/`. Python tests live in `adapters/python/tests/`; consumers in `adapters/python/examples/minimal-pytest/` and `adapters/python/examples/safety-offline/`. Shared spec fixtures live in `adapters/fixtures/specs/`. CI runs Node and Python jobs.

Further work is indexed in [Python project testing](plans/python-project-testing.md). Git-aware diff input boundaries are documented in [ADR 0021](adr/0021-git-diff-input-boundary.md); plan notes live under `docs/plans/git-diff-hardening/`.
