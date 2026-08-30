# Postulate Product & Technical Specification

This file is the source of truth. [`TASKS.md`](TASKS.md) is the implementation plan. [`PLAN.md`](PLAN.md) is sequencing. [`adr/`](adr/README.md) records locked design choices.

---

## 1. Product Definition

**Postulate** is a framework for specifying and validating software behavior in AI-assisted development.

You postulate the contract before code is generated, and everything that follows is judged against it.

> As AI makes code generation cheap, validating correctness becomes the bottleneck.

*postulate*, verb: to assume or suggest that something is true, often as a foundational principle for reasoning.

A Postulate spec is a YAML file that sits next to your code and defines:

- correctness contracts
- BDD scenarios
- invariants
- policies
- mappings between behavior and tests

The product answers:

> What did we claim this code must do, is that claim structurally complete, and did a later change weaken it?

---

## 2. Product Positioning

Primary positioning:

> **Postulate the contract before the LLM writes the code.**

Short positioning:

> **Spec-anchored development for AI-generated software.**

More tactical positioning:

> **Treat specifications as artifacts that can be reviewed, checked, and diffed like code.**

Use language like:

- correctness contract
- named invariants
- spec-anchored development
- structural discipline at CI time
- spec regression
- AI guardrails

Avoid positioning as:

- a theorem prover
- formal verification
- a replacement for tests
- a guarantee of correctness
- an LLM coding agent
- a general test framework

Avoid claims like:

- the implementation is proven correct
- generated code cannot invent behavior
- policies are enforced (they are declarations in v0.1)
- custom invariants have built-in semantics

---

## 3. Version Scope: v0.1 CLI

This version includes:

- YAML spec schema (`PostulateSchema` in Zod, mirrored in `schemas/postulate.schema.json`)
- Readable schema-validation errors on load
- `postulate check`
- `postulate prompt`
- `postulate ci` with optional `--fail-on-warnings`
- `postulate diff` of two spec file paths
- A small registry of well-known invariant names
- A worked TypeScript example (`examples/ts-late-fee`)
- GitHub Actions that build, test, and run `postulate ci` against the example

This version does **not** include:

- Property-test generation from named invariants
- Policy enforcement (semgrep, eslint, OPA/Rego)
- Coverage measurement against tests that actually ran
- Architectural drift detection
- Git-aware diff (`HEAD~1` or other refs)
- Multi-language adapters (Python, Ruby, Go, Rust, …)
- A test runner
- Semantic evaluation of contract predicates
- Theorem proving / model checking
- npm-published package (documented, not yet the distribution path in-repo)

---

## 4. Influences

### David Gries, *The Science of Programming*

Programs should be developed alongside explicit reasoning about correctness (preconditions, postconditions, invariants) rather than tested into shape after the fact. Postulate uses that vocabulary. It is not a theorem prover and is not a substitute for formal verification. It treats those specifications as first-class artifacts in an AI-assisted workflow.

### Behavior-Driven Development

Executable, human-readable scenarios live beside contracts and invariants, so product-visible behavior is specified in the same file.

### AI guardrails

Specification-first development, constrained generation for LLMs, and policy-based validation for AI-generated software.

---

## 5. Layers

| Layer                | Purpose                       | Output                                       |
| -------------------- | ----------------------------- | -------------------------------------------- |
| Contract             | Define correctness            | Preconditions, postconditions, failure cases |
| BDD                  | Define observable behavior    | Scenarios                                    |
| Invariants           | Define always-true properties | Assertions or property tests                 |
| Codegen              | Constrain LLM implementation  | Implementation, tests, assumptions           |
| Correctness argument | Explain why it works          | Reviewable proof sketch                      |
| CI                   | Enforce discipline            | Required artifact checks                     |

See also [`framework.md`](framework.md).

---

## 6. Stack

Required:

```text
Node.js >= 20
TypeScript (ESM, NodeNext)
commander
zod
yaml
picocolors
vitest (dev)
```

Package name: `postulate` (npm scope `@postulate/cli` when published).  
CLI binary: `postulate`.  
Entry: `src/index.ts` → `dist/index.js`.

The spec format is plain YAML. Any language can produce one. The v0.1 implementation is TypeScript-first; language-specific adapters are later.

---

## 7. Spec Format

A spec is a YAML document validated by `PostulateSchema` in `src/spec.ts`. `loadSpec()` reads the file, parses YAML, and runs Zod. Schema failures are `SpecLoadError` with path-qualified messages.

JSON Schema mirror: `schemas/postulate.schema.json`. Zod is authoritative. If they disagree, fix the JSON Schema to match Zod and add a test.

### 7.1 Fields

| Field | Required | Default | Notes |
| --- | --- | --- | --- |
| `feature` | yes | — | Non-empty string. Feature name. |
| `owner` | no | — | Team or person. |
| `risk` | no | `medium` | `low` \| `medium` \| `high` \| `critical`. |
| `contract.preconditions` | yes | — | Array of strings, min 1. |
| `contract.postconditions` | yes | — | Array of strings, min 1. |
| `contract.failure_cases` | no | `[]` | Array of strings. |
| `invariants` | no | `[]` | Array of names. Known or custom. |
| `bdd` | yes | — | Array of scenarios, min 1. |
| `bdd[].name` | yes | — | Non-empty string. Used as `test_mapping` key. |
| `bdd[].given` | no | `{}` | Arbitrary object. |
| `bdd[].when` | no | `{}` | Arbitrary object. |
| `bdd[].then` | no | `{}` | Expected results. Empty `then` fails `check`. |
| `policies` | no | `[]` | Array of names. Declarations only in v0.1. |
| `test_mapping` | no | `{}` | Map from invariant/scenario name → test locator string. |
| `correctness_argument` | no | — | Free-text proof sketch. Warned for high/critical risk. |

Contract predicates and failure cases are **strings**. v0.1 does not parse or evaluate them. They are reviewed by humans and copied into the codegen prompt.

### 7.2 Example

```yaml
feature: late_fee_calculation
owner: billing
risk: high

contract:
  preconditions:
    - invoice.amount_cents >= 0
    - invoice.due_date is a valid ISO date string (YYYY-MM-DD)
    - today is a valid ISO date string (YYYY-MM-DD)
  postconditions:
    - fee_cents >= 0
    - fee_cents == 0 when today <= invoice.due_date
    - fee_cents == round(amount_cents * 0.015 * full_months_overdue) when today > due_date
    - fee_cents <= invoice.amount_cents
    - same input returns same output
  failure_cases:
    - missing or empty invoice.due_date raises a validation error
    - negative invoice.amount_cents raises a validation error
    - malformed date string raises a validation error

invariants:
  - does_not_mutate_input
  - deterministic_for_same_input
  - fee_never_exceeds_principal

bdd:
  - name: no_fee_before_due_date
    given:
      amount_cents: 10000
      due_date: "2026-05-31"
    when:
      today: "2026-05-21"
    then:
      fee_cents: 0

policies:
  - no_network_calls
  - no_db_writes

test_mapping:
  no_fee_before_due_date: "lateFee.test.ts > no_fee_before_due_date"
  does_not_mutate_input: "lateFee.test.ts > does_not_mutate_input"
  deterministic_for_same_input: "lateFee.test.ts > deterministic_for_same_input"
  fee_never_exceeds_principal: "lateFee.test.ts > fee_never_exceeds_principal"

correctness_argument: |
  Before or on the due date, the implementation returns 0 ...
```

Canonical worked example: `examples/ts-late-fee/postulate.yaml`.

---

## 8. CLI

```text
postulate check <spec-file>
postulate prompt <spec-file>
postulate ci <spec-file> [--fail-on-warnings]
postulate diff <before> <after>
```

Load failures (missing file, invalid YAML, schema failure) print to stderr and exit **2**.

| Command | Exit 0 | Exit 1 | Exit 2 |
| --- | --- | --- | --- |
| `check` | no errors | one or more check errors | spec load failure |
| `ci` | no errors, and no warnings if `--fail-on-warnings` | errors, or warnings with the flag | spec load failure |
| `prompt` | prompt printed to stdout | — | spec load failure |
| `diff` | no regressions (improvements allowed) | one or more regressions | spec load failure |

Warnings never fail `check`. They fail `ci` only with `--fail-on-warnings`.

Info lines are printed for recognised vs custom invariants. They never affect exit codes.

### 8.1 Output prefixes

| Prefix | Meaning |
| --- | --- |
| `i ` | info |
| `! ` | warning |
| `✗ ` | error or regression |
| `+ ` | diff improvement |
| `- ` | diff regression |
| `✓ ` | success |

---

## 9. Check Rules

`checkSpec(spec)` in `src/check.ts`. Severity is fixed for v0.1.

| Check | Severity | Rule |
| --- | --- | --- |
| Risk requires invariants | error | `risk` of `high` or `critical` requires `invariants.length >= 1`. |
| BDD `then` is non-empty | error | Every scenario must have at least one key in `then`. |
| Invariant has a test mapping | error | Every named invariant must be a key in `test_mapping`. |
| Risk requires correctness argument | warning | `high` or `critical` should include `correctness_argument`. |
| BDD scenario has a test mapping | warning | Every scenario `name` should be a key in `test_mapping`. |
| Contract not too thin | warning | `preconditions.length + postconditions.length >= 3`. |
| Recognised vs custom invariants | info | Lists names in the known registry vs names that are not. |

The invariant → `test_mapping` rule is the one that turns "list it in YAML and ignore it in code" from a silent failure into a CI failure.

v0.1 does **not**:

- open the test files named in `test_mapping`
- execute tests
- evaluate contract strings
- enforce policies
- require `test_mapping` values to match a particular locator grammar

`test_mapping` values are opaque strings. The late-fee example uses `"file.test.ts > test_name"`.

---

## 10. Diff Rules

`diffSpecs(before, after)` in `src/diff.ts` compares two already-loaded specs.

Risk order: `low < medium < high < critical`.

| Change | Classification |
| --- | --- |
| Risk lowered | regression |
| Risk raised | improvement |
| Invariant / postcondition / BDD scenario name / policy removed | regression |
| Same item added | improvement |

Sets are compared by string identity. Renaming a postcondition is a remove + add (regression and improvement). Scenario bodies are not deep-diffed; only `bdd[].name` is compared.

`printDiffResult` exits 1 if `regressions.length > 0`. Improvements alone are success.

v0.1 compares two file paths. Git refs are later (`postulate diff HEAD~1`).

---

## 11. Codegen Prompt

`buildCodegenPrompt(spec)` in `src/prompt.ts` prints a prompt to stdout. It must:

1. Tell the model it is implementing from a correctness contract.
2. Forbid inventing behavior outside the spec. If the spec is ambiguous, list the ambiguity instead of guessing.
3. Require this return shape:
   1. Implementation
   2. Tests generated from every BDD scenario
   3. Property tests or assertions for every invariant
   4. Correctness argument mapping code paths to postconditions
   5. Remaining assumptions
4. Embed the spec as pretty-printed JSON under a `SPEC:` heading.

Do not call an LLM from the CLI. `prompt` only prints text.

---

## 12. Known Invariants

Registry: `src/invariants.ts`. Intentionally small in v0.1.

| Name | Meaning |
| --- | --- |
| `does_not_mutate_input` | Function arguments are unchanged after the call returns. |
| `deterministic_output` | Same inputs produce the same output across repeated calls. |
| `deterministic_for_same_input` | Same as `deterministic_output`. Both names are recognised. |
| `pure` | No observable side effects; output depends only on arguments. |
| `idempotent` | Calling the operation twice has the same effect as once. |
| `total` | Function is defined for every input that satisfies preconditions. |

Custom invariant names are allowed. `check` reports them as info (`Custom invariants (no built-in semantics yet)`). Custom names still require a `test_mapping` entry.

v0.1 does not generate tests from these names. Generation is a later phase (fast-check or equivalent).

---

## 13. Policies

Policies are free-string declarations (`no_network_calls`, `no_db_writes`, …).

v0.1:

- stores them on the spec
- diffs removals as regressions
- does not enforce them

Later: start with semgrep / eslint-based checks, then optional OPA/Rego. Policy violations should fail CI.

---

## 14. Engineer Workflow

1. Write or update `postulate.yaml`.
2. Run `postulate check postulate.yaml`.
3. Run `postulate prompt postulate.yaml` and pass the output to an LLM.
4. Add implementation and tests; populate `test_mapping` so every named invariant points at a test that exercises it.
5. Include the correctness argument in the PR (see [`pr-template.md`](pr-template.md)).
6. Let CI enforce structural completeness via `postulate ci` (optionally `--fail-on-warnings`).
7. On subsequent changes, run `postulate diff old.yaml new.yaml` to flag dropped invariants, weakened risk, or removed postconditions.

### Review guidance

Reviewers should focus on:

- Is the spec complete enough?
- Are the BDD examples meaningful?
- Are invariants actually testable, and is each one mapped to a test?
- Did generated code invent behavior the spec didn't authorise?
- Does the correctness argument match the implementation?

---

## 15. Repository Layout

```text
src/index.ts          CLI (commander)
src/spec.ts           Zod schema and types
src/loadSpec.ts       YAML load + schema errors
src/check.ts          Structural checks + printing
src/diff.ts           Spec regression diff + printing
src/prompt.ts         Codegen prompt builder
src/invariants.ts     Known-invariant registry
schemas/postulate.schema.json
examples/ts-late-fee/ postulate.yaml, lateFee.ts, lateFee.test.ts
tests/                vitest (check, diff)
.github/workflows/postulate.yml
docs/                 this documentation set
```

---

## 16. CI

`.github/workflows/postulate.yml` on pull requests and pushes to `main`:

1. `npm ci`
2. `npm run build`
3. `npm test`
4. `node dist/index.js ci examples/ts-late-fee/postulate.yaml`

The example job does not pass `--fail-on-warnings` today. Stricter gates are opt-in per consumer.

---

## 17. What Postulate Is Not

- A theorem prover.
- A formal verification tool (model checking, weakest-precondition proofs).
- A replacement for engineering judgment.
- A guarantee of correctness.

What it does try to do:

- Externalize intent before the LLM writes the code.
- Treat specifications as artifacts that can be reviewed and diffed like code.
- Enforce a minimum of structural discipline at CI time.
- Flag regressions when specs are weakened over time.

---

## 18. Future Scope

Tracked in [`TASKS.md`](TASKS.md) and [`../ROADMAP.md`](../ROADMAP.md):

1. **Property tests from named invariants** — declare the invariant; Postulate generates a property-test scaffold (likely fast-check).
2. **Policy enforcement** — semgrep/eslint first, optional OPA/Rego later; violations fail CI.
3. **Coverage measurement** — compare declared invariants and BDD scenarios against tests that actually ran.
4. **Architectural drift detection** — compare the codebase against structural expectations in the spec.
5. **Git-aware diff** — `postulate diff` against `HEAD~1` or another git reference.
6. **Multi-language adapters** — keep the YAML format language-neutral; add adapters for test discovery, generation, and policy checks.

Do not implement these unless the current `TASKS.md` phase explicitly asks for them.
