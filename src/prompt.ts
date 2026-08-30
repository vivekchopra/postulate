import type { PostulateSpec } from "./spec.js";

export function buildCodegenPrompt(spec: PostulateSpec): string {
  return [
    "You are implementing code from a correctness contract.",
    "",
    "Do not invent behavior outside the spec. If the spec is ambiguous, list the ambiguity instead of guessing.",
    "",
    "Return:",
    "1. Implementation",
    "2. Tests generated from every BDD scenario",
    "3. Property tests or assertions for every invariant",
    "4. Correctness argument mapping code paths to postconditions",
    "5. Remaining assumptions",
    "",
    "SPEC:",
    JSON.stringify(spec, null, 2),
    ""
  ].join("\n");
}
