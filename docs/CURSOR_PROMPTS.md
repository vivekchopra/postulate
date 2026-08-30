# CURSOR_PROMPTS.md

Reusable Cursor prompts for Postulate.

Read these files first on every task:

- `docs/SPEC.md`
- `docs/TASKS.md`
- `docs/PLAN.md`
- `docs/CURSOR_PROMPTS.md`
- `docs/adr/README.md`

---

## Next Phase Prompt

Paste this when starting a new phase.

```text
You are working on Postulate.

Read these files first:
- docs/SPEC.md
- docs/TASKS.md
- docs/PLAN.md
- docs/CURSOR_PROMPTS.md
- docs/adr/README.md

First, verify the previous completed phase/task before starting new work.

Previous-stage verification:
1. Identify the most recently completed phase/task from docs/TASKS.md and the current codebase.
2. Verify that its stated acceptance criteria still pass.
3. Check for obvious regressions in:
   - tests
   - CLI behavior (check, prompt, ci, diff)
   - spec schema / load errors
   - the late-fee example
4. If there is a blocking regression, fix only that regression before continuing.
5. Do not refactor, redesign, or improve previous-stage work unless it blocks the next task.

Then find the next incomplete phase/task in docs/TASKS.md and implement only that phase/task.

Before coding new work, do the following:
1. State the previous phase/task you verified.
2. State whether verification passed or what blocking regression you fixed.
3. State the exact next phase/task you selected.
4. Explain why it is the next incomplete item.
5. Summarize what is in scope.
6. Summarize what is explicitly out of scope.
7. List the files you expect to modify.
8. List the tests you will add or update.

Then implement only the selected phase/task.

General constraints:
- Do not implement future phases.
- Do not add theorem proving, model checking, or weakest-precondition proofs.
- Do not claim Postulate proves correctness.
- Do not evaluate contract predicate strings as executable code.
- Do not add policy enforcement unless the selected task explicitly asks for it.
- Do not add coverage measurement unless the selected task explicitly asks for it.
- Do not add architectural drift detection unless the selected task explicitly asks for it.
- Do not add git-aware diff unless the selected task explicitly asks for it.
- Do not add multi-language adapters unless the selected task explicitly asks for them.
- Do not call an LLM from the CLI unless the selected task explicitly asks for it.
- Preserve existing public CLI behavior unless the selected task explicitly changes it.
- Keep implementation simple and explicit.
- Avoid broad refactors unless required by the selected task.
- Do not change unrelated files.
- If you discover a problem outside this task, note it but do not fix it unless it blocks the selected task.
- If the task changes schema, CLI contract, check severity, or invariant semantics, add an ADR in the same change.

Product/model requirements:
- Specs remain YAML validated by Zod (`PostulateSchema`).
- Every named invariant must still map to `test_mapping` (error).
- High/critical risk still requires at least one invariant (error).
- Policies remain declarations until a task implements enforcement.
- `postulate prompt` must not invent behavior outside the spec; ambiguities are listed, not guessed.
- Known-invariant recognition stays informational until a task implements generators.

Testing requirements:
- Add or update tests for the selected task.
- Unit tests must be deterministic (no live LLM, no network).
- If CLI behavior changes, add CLI/exit-code tests.
- If schema behavior changes, add load/schema tests.
- If check rules change, add check tests.
- If diff behavior changes, add diff tests.
- Keep `examples/ts-late-fee` green unless the task explicitly changes it.

Definition of done:
- npm test passes.
- npm run build succeeds.
- Existing CLI still works: postulate check, prompt, ci, diff.
- examples/ts-late-fee still checks clean.
- No future-scope features were added.
- Summarize changed files and why.
- Summarize how to manually test the completed task.
- Mark the phase complete in docs/TASKS.md only if acceptance criteria pass.
```

---

## Post-Implementation Review Prompt

```text
Review the implementation against:
- docs/SPEC.md
- docs/TASKS.md
- docs/PLAN.md
- docs/adr/

Check for:
- future-phase scope creep
- missing tests
- tests that call live LLMs or the network
- broken CLI behavior (check, prompt, ci, diff)
- schema load regressions
- check severity changes that were not ADRed
- claims of formal verification or proven correctness
- evaluating contract strings as code
- broad refactors
- unrelated file changes
- example late-fee regressions
- JSON Schema drifting from Zod

If anything blocks the current task's definition of done, fix it.

If something is only a future improvement, list it but do not implement it.
```

---

## Failure Fix Prompt

```text
I ran:

<command>

It failed with:

<error output>

Fix only the issue causing this failure.
Do not refactor unrelated code.
Do not implement future phases.
Add or update a test that would have caught this.
```

---

## Spec-First Feature Prompt

Use when implementing a feature *in another repo* that has a `postulate.yaml`.

```text
You are implementing code from a Postulate correctness contract.

Read the spec file first. Do not invent behavior outside the spec.
If the spec is ambiguous, list the ambiguity instead of guessing.

Return:
1. Implementation
2. Tests generated from every BDD scenario
3. Property tests or assertions for every invariant
4. Correctness argument mapping code paths to postconditions
5. Remaining assumptions

Then update test_mapping so every named invariant (and each BDD scenario) points at a test.

Run the project's tests. If postulate CLI is available, run:
- postulate check <spec>
- postulate ci <spec>
```

You can also paste the output of `postulate prompt <spec-file>` as the task body.
