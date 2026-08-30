# Postulate

Postulate is a framework for specifying and validating software behavior in AI-assisted development. You postulate the contract before code is generated, and everything that follows is judged against it.

> As AI makes code generation cheap, validating correctness becomes the bottleneck.

*postulate*, verb: to assume or suggest that something is true, often as a foundational principle for reasoning. 

A Postulate spec is a YAML file that sits next to your code and defines:
- correctness contracts
- BDD scenarios
- invariants
- policies
- mappings between behavior and tests

Example:

```yaml
invariants:
  - does_not_mutate_input
  - fee_never_exceeds_principal
```

If those invariants disappear in a later PR, `postulate diff` flags the regression before merge.

## Status

This is a very early version (v0.1). What ships today:

- YAML spec schema with Zod-based validation and readable error messages.
- A `check` command that enforces a small set of structural rules.
- A `ci` command with an optional `--fail-on-warnings` flag.
- A `diff` command that flags dropped invariants, removed postconditions, and weakened risk between two spec versions.
- A `prompt` command that builds an LLM codegen prompt from a spec.
- A small registry of well-known invariants: `does_not_mutate_input`, `deterministic_output`, `pure`, `idempotent`, and friends.
- A worked TypeScript example with a spec, an implementation, and tests covering every named invariant and failure case.

See [Current checks](#current-checks) for the exact rules. Planned work lives in [ROADMAP.md](./ROADMAP.md); implementation tracking is in [docs/TASKS.md](./docs/TASKS.md).

## Docs for contributors

| Doc | Purpose |
| --- | --- |
| [`docs/SPEC.md`](docs/SPEC.md) | Product and technical source of truth |
| [`docs/TASKS.md`](docs/TASKS.md) | Phased implementation plan |
| [`docs/PLAN.md`](docs/PLAN.md) | Build plan / sequencing |
| [`docs/CURSOR_PROMPTS.md`](docs/CURSOR_PROMPTS.md) | Cursor task prompts |
| [`docs/adr/`](docs/adr/README.md) | Architecture Decision Records |
| [`docs/README.md`](docs/README.md) | Docs map |

New design changes go in `docs/adr/` (copy `docs/adr/template.md`, take the next id).

## Install and try

From source:

```bash
npm install
npm run build
node dist/index.js check examples/ts-late-fee/postulate.yaml
node dist/index.js prompt examples/ts-late-fee/postulate.yaml
node dist/index.js ci examples/ts-late-fee/postulate.yaml --fail-on-warnings
npm test
```

Once published to npm:

```bash
npm install -g @postulate/cli
postulate check ./postulate.yaml
```

The package is published under the scoped name `@postulate/cli`. The CLI binary is `postulate`.

## Influences

### David Gries, *The Science of Programming*

Gries argued that programs should be developed alongside explicit reasoning about correctness (preconditions, postconditions, invariants, proof-oriented construction) rather than tested into shape after the fact. Postulate uses the same vocabulary. However, its not a theorem prover and nor is it a substitute for formal verification. It treats specifications as first-class artifacts in an AI-assisted workflow.

### Behavior-Driven Development

Postulate borrows BDD's executable, human-readable scenarios as a layer alongside contracts and invariants, so product-visible behavior lives beside the more formal specifications.

### AI guardrails

Postulate also draws on recent work around specification-first development, constrained generation for LLMs, and policy-based validation for AI-generated software.

## Core concepts

### Contracts

```yaml
contract:
  preconditions:
    - invoice.amount_cents >= 0
  postconditions:
    - fee_cents >= 0
    - fee_cents == 0 when today <= due_date
  failure_cases:
    - negative amount_cents raises a validation error
```

### Invariants

```yaml
invariants:
  - does_not_mutate_input
  - deterministic_output
  - fee_never_exceeds_principal
```

Postulate ships with a small registry of well-known invariants. Custom invariants are fine, but every invariant (known or custom) must point to a test via `test_mapping`, or `check` fails.

### BDD scenarios

```yaml
bdd:
  - name: no_fee_before_due
    given:
      due_date: "2026-05-31"
      amount_cents: 10000
    when:
      today: "2026-05-21"
    then:
      fee_cents: 0
```

### Policies

```yaml
policies:
  - no_network_calls
  - no_db_writes
```

Policies are declarations today. Enforcement is on the roadmap.

### Test mapping

```yaml
test_mapping:
  no_fee_before_due: "lateFee.test.ts > no_fee_before_due"
  does_not_mutate_input: "lateFee.test.ts > does_not_mutate_input"
```

`postulate check` fails if any named invariant is missing from `test_mapping`. This is the rule that turns "list it in YAML and ignore it in code" from a silent failure into a CI failure.

## Workflow

> Postulate the contract first.

```
write spec → postulate check → postulate prompt → LLM writes code & tests → postulate ci → review → merge
                                                                                    ↑
                                                            postulate diff for subsequent changes
```

## Current checks

| Check                              | Severity | Rule                                                                       |
| ---------------------------------- | -------- | -------------------------------------------------------------------------- |
| Risk requires invariants           | error    | High or critical risk specs must declare at least one invariant.           |
| BDD `then` is non-empty            | error    | Every scenario must specify at least one expected result.                  |
| Invariant has a test mapping       | error    | Every named invariant must appear in `test_mapping`.                       |
| Risk requires correctness argument | warning  | High or critical risk specs should include `correctness_argument`.         |
| BDD scenario has a test mapping    | warning  | Every named scenario should appear in `test_mapping`.                      |
| Contract not too thin              | warning  | preconditions + postconditions ≥ 3                                         |
| Recognised vs. custom invariants   | info     | Surfaces which invariants Postulate knows about and which are unrecognised.|

`postulate diff <before> <after>` reports regressions (dropped invariants, removed postconditions, removed scenarios, removed policies, weakened risk) along with the inverse improvements.

## What Postulate is not

- A theorem prover.
- A formal verification tool in the technical sense (model checking, weakest-precondition proofs).
- A replacement for engineering judgment.
- A guarantee of correctness.

What it does try to do is externalize intent before the LLM writes the code, treat specifications as artifacts that can be reviewed and diffed like code, enforce a minimum of structural discipline at CI time, and flag regressions when specs are weakened over time.

## License

MIT
