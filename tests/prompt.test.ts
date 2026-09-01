import { describe, expect, it } from "vitest";
import { buildCodegenPrompt } from "../src/prompt.js";
import type { PostulateSpec } from "../src/spec.js";

const spec: PostulateSpec = {
  feature: "example",
  owner: "test",
  risk: "medium",
  contract: {
    preconditions: ["input exists"],
    postconditions: ["output exists"],
    failure_cases: []
  },
  invariants: ["deterministic_output"],
  bdd: [
    { name: "example_scenario", given: {}, when: {}, then: { result: true } }
  ],
  policies: [],
  test_mapping: {
    deterministic_output: "example.test.ts > deterministic_output",
    example_scenario: "example.test.ts > example_scenario"
  }
};

describe("buildCodegenPrompt", () => {
  it("bounds the agent to behavior in the spec", () => {
    const prompt = buildCodegenPrompt(spec);

    expect(prompt).toContain("Do not invent behavior outside the spec");
    expect(prompt).toContain("list the ambiguity instead of guessing");
  });

  it("requests implementation, scenario tests, invariant checks, correctness reasoning, and assumptions", () => {
    const prompt = buildCodegenPrompt(spec);

    expect(prompt).toContain("1. Implementation");
    expect(prompt).toContain("Tests generated from every BDD scenario");
    expect(prompt).toContain("Property tests or assertions for every invariant");
    expect(prompt).toContain("Correctness argument");
    expect(prompt).toContain("Remaining assumptions");
  });

  it("embeds the loaded spec as JSON", () => {
    const prompt = buildCodegenPrompt(spec);

    expect(prompt).toContain('"feature": "example"');
    expect(prompt).toContain('"deterministic_output"');
    expect(prompt).toContain('"example_scenario"');
  });
});
