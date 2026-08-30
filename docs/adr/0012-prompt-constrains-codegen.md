# 0012. Prompt constrains codegen; CLI does not call a model

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

The workflow needs a way to hand a spec to an LLM without Postulate becoming an agent platform.

## Decision

`postulate prompt` prints a text prompt to stdout: implement from the contract, do not invent behavior, list ambiguities instead of guessing, return implementation + BDD tests + invariant tests + correctness argument + assumptions, then embed the spec as JSON.

The CLI does not call an LLM, choose a provider, or write files.

## Consequences

Users pipe or paste the prompt into whatever model they use. Postulate stays offline and deterministic. Productizing an agent is out of scope.

## Alternatives considered

- Built-in LLM call — API keys, non-determinism, and vendor lock-in in a validation tool.
- Generate code directly in Postulate — not the product; the spec is.
