# 0020. Measure execution of every declared pytest claim

- Status: Accepted
- Date: 2026-09-02
- Supersedes: [0018](0018-pytest-plugin-exercised-mapping.md) (skip and execution semantics)
- Refines: [0015](0015-pytest-test-mapping-locator.md), path identity and parameter matching
- Plan: [pytest-coverage](../plans/pytest-coverage/PLAN.md)
- Superseded by: (none)

## Context

The existing plugin can report success when a claim has no mapping or its mapped test was skipped. Path truncation and suffix matching can also attribute an unrelated test to a claim. These results do not satisfy "compare spec claims with tests that actually ran."

## Decision

Evaluate the union of invariant names and BDD scenario names. Every invariant without an exercised mapping is an error. Every BDD-only claim without one is a warning, promoted by the existing `--postulate-fail-on-warning` flag. A shared invariant/scenario name uses the invariant severity. Unknown mapping keys always warn.

A test is exercised only when pytest emits a non-skipped call report with passed or failed outcome. Setup skips, setup failures, runtime skips, and expected failures reported as skipped do not count. This is deliberately conservative when a body partially executes before skip/xfail. A failed call counts as executed, while pytest still fails the suite. XPASS is execution, not proof of correctness; pytest's strictness determines its test outcome.

A locator identifies one root-relative pytest node. Normalize only the filesystem path portion; preserve class/function/parameter text verbatim. Do not strip directories up to `tests/`, use suffix matching, globbing, or infer a test name from a claim. Exact parametrized locators require that case. A base locator is satisfied by at least one exercised parametrization, not all cases.

Keep `verify` collection-only. Share claim classification and locator matching between verify and the plugin without conflating collected and exercised IDs. Avoid duplicate missing-mapping diagnostics where verify already runs structural checks.

Load/schema validation occurs before tests, with pytest usage errors for invalid plugin inputs. At session finish, preserve every existing nonzero pytest exit status, including statuses unknown to this version of Postulate. Coverage failures change only status 0 to 1. Store a bounded summary of names and report outcomes, not captured test output.

The first hardened version supports a normal single-process session. Reject active distributed execution and `--collect-only` when `--postulate-spec` is present, with actionable usage messages. For collection-only checking, use `postulate verify`. Full xdist aggregation, rerun semantics, and cross-session coverage are deferred.

## Consequences

Skipped mappings and ambiguous shorthand paths can newly fail CI. This is an intentional correction. Migration guidance tells users to map real root-relative nodes and run the relevant suite. No "count skips as coverage" escape hatch is added.

No schema change, new plugin package, new command, line coverage, JSON evidence protocol, test-body execution by Postulate, or general adapter framework is needed.

## Alternatives

- Count all reports: preserves the current false-positive behavior.
- Count only passed tests: conflates execution with assertion success and duplicates pytest's test gate.
- Infer mappings from function names or decorators: introduces a second mapping system and ambiguous identity.
- Require all parametrizations: valuable separately, but adds collection-completeness semantics beyond this small feature.
