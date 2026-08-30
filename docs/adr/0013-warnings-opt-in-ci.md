# 0013. Warnings fail CI only with --fail-on-warnings

- Status: Accepted
- Date: 2026-08-11
- Deciders: postulate
- Supersedes: (none)
- Superseded by: (none)

## Context

Some rules are worth surfacing immediately (unmapped invariants). Others are discipline (thin contracts, unmapped BDD names, missing correctness argument) that teams may adopt gradually.

## Decision

`check` exits 1 only on errors. Warnings and info never fail `check`.

`ci` is the same as `check` unless `--fail-on-warnings` is set, in which case any warning exits 1.

This repository's GitHub Action runs `ci` **without** the flag.

## Consequences

Consumers opt into stricter gates. Error-level rules stay the default floor. Do not silently promote a warning to an error without an ADR.

## Alternatives considered

- Fail CI on warnings by default — noisy for early adoption.
- No `ci` command — teams would reimplement `--fail-on-warnings` in shell.
