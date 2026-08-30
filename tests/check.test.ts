import { describe, expect, it } from "vitest";
import { checkSpec } from "../src/check.js";
import type { PostulateSpec } from "../src/spec.js";

const baseSpec: PostulateSpec = {
  feature: "example",
  owner: "test",
  risk: "medium",
  contract: {
    preconditions: ["input exists"],
    postconditions: ["output exists"],
    failure_cases: []
  },
  invariants: [],
  bdd: [
    { name: "example_scenario", given: {}, when: {}, then: { result: true } }
  ],
  policies: [],
  test_mapping: { example_scenario: "examples.test.ts > example" }
};

describe("checkSpec", () => {
  it("passes a basic valid spec", () => {
    expect(checkSpec(baseSpec).ok).toBe(true);
  });

  it("requires invariants for high-risk specs", () => {
    const result = checkSpec({ ...baseSpec, risk: "high" });
    expect(result.ok).toBe(false);
    expect(
      result.errors.some((e) => e.includes("requires at least one invariant"))
    ).toBe(true);
  });

  it("requires every invariant to have an entry in test_mapping", () => {
    const result = checkSpec({
      ...baseSpec,
      invariants: ["deterministic_output"]
    });
    expect(result.ok).toBe(false);
    expect(
      result.errors.some(
        (e) =>
          e.includes("deterministic_output") && e.includes("test_mapping")
      )
    ).toBe(true);
  });

  it("passes when every invariant is mapped to a test", () => {
    const result = checkSpec({
      ...baseSpec,
      invariants: ["deterministic_output"],
      test_mapping: {
        ...baseSpec.test_mapping,
        deterministic_output: "examples.test.ts > deterministic"
      }
    });
    expect(result.ok).toBe(true);
  });

  it("warns when a BDD scenario has no test_mapping entry", () => {
    const result = checkSpec({
      ...baseSpec,
      test_mapping: {} // strip the mapping
    });
    expect(
      result.warnings.some((w) => w.includes("BDD scenario"))
    ).toBe(true);
  });

  it("errors when a scenario has an empty 'then'", () => {
    const result = checkSpec({
      ...baseSpec,
      bdd: [{ name: "empty_then", given: {}, when: {}, then: {} }],
      test_mapping: { empty_then: "test" }
    });
    expect(result.ok).toBe(false);
  });

  it("warns on high-risk specs without a correctness_argument", () => {
    const result = checkSpec({
      ...baseSpec,
      risk: "high",
      invariants: ["does_not_mutate_input"],
      test_mapping: {
        ...baseSpec.test_mapping,
        does_not_mutate_input: "tests"
      }
    });
    expect(
      result.warnings.some((w) => w.includes("correctness_argument"))
    ).toBe(true);
  });

  it("reports recognised invariants in info", () => {
    const result = checkSpec({
      ...baseSpec,
      invariants: ["does_not_mutate_input"],
      test_mapping: {
        ...baseSpec.test_mapping,
        does_not_mutate_input: "tests"
      }
    });
    expect(
      result.info.some((i) => i.includes("Recognised invariants"))
    ).toBe(true);
  });

  it("reports custom invariants separately in info", () => {
    const result = checkSpec({
      ...baseSpec,
      invariants: ["my_domain_rule"],
      test_mapping: {
        ...baseSpec.test_mapping,
        my_domain_rule: "tests"
      }
    });
    expect(result.info.some((i) => i.includes("Custom invariants"))).toBe(true);
  });
});
