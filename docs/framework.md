# Postulate Framework

Short layer overview. The source of truth is [`SPEC.md`](SPEC.md).

## Layers

| Layer                | Purpose                       | Output                                       |
| -------------------- | ----------------------------- | -------------------------------------------- |
| Contract             | Define correctness            | Preconditions, postconditions, failure cases |
| BDD                  | Define observable behavior    | Scenarios                                    |
| Invariants           | Define always-true properties | Assertions or property tests                 |
| Codegen              | Constrain LLM implementation  | Implementation, tests, assumptions           |
| Correctness argument | Explain why it works          | Reviewable proof sketch                      |
| CI                   | Enforce discipline            | Required artifact checks                     |

## Engineer workflow

1. Write or update `postulate.yaml`.
2. Run `postulate check postulate.yaml`.
3. Run `postulate prompt postulate.yaml` and pass the output to an LLM.
4. Add implementation and tests; populate `test_mapping` so every named
   invariant points at a test that exercises it.
5. Include the correctness argument in the PR.
6. Let CI enforce structural completeness via `postulate ci`
   (optionally `--fail-on-warnings` for stricter gates).
7. On subsequent changes, use `postulate diff old.yaml new.yaml` to flag
   dropped invariants, weakened risk, or removed postconditions.

## Review guidance

Reviewers should focus on:

- Is the spec complete enough?
- Are the BDD examples meaningful?
- Are invariants actually testable, and is each one mapped to a test?
- Did generated code invent behavior the spec didn't authorise?
- Does the correctness argument match the implementation?
