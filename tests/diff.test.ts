import { describe, expect, it } from "vitest";
import { diffSpecs } from "../src/diff.js";
import type { PostulateSpec } from "../src/spec.js";

const baseSpec: PostulateSpec = {
  feature: "example",
  owner: "test",
  risk: "high",
  contract: {
    preconditions: ["a >= 0"],
    postconditions: ["b > 0", "c is bounded"],
    failure_cases: []
  },
  invariants: ["deterministic_output", "does_not_mutate_input"],
  bdd: [{ name: "scenario_a", given: {}, when: {}, then: { ok: true } }],
  policies: ["no_network_calls"],
  test_mapping: {}
};

describe("diffSpecs", () => {
  it("reports no regressions for identical specs", () => {
    const result = diffSpecs(baseSpec, baseSpec);
    expect(result.regressions).toEqual([]);
    expect(result.improvements).toEqual([]);
  });

  it("flags dropped invariants as regressions", () => {
    const after = { ...baseSpec, invariants: ["deterministic_output"] };
    const result = diffSpecs(baseSpec, after);
    expect(
      result.regressions.some((r) =>
        r.includes("does_not_mutate_input")
      )
    ).toBe(true);
  });

  it("flags added invariants as improvements", () => {
    const after = {
      ...baseSpec,
      invariants: [...baseSpec.invariants, "idempotent"]
    };
    const result = diffSpecs(baseSpec, after);
    expect(
      result.improvements.some((i) => i.includes("idempotent"))
    ).toBe(true);
  });

  it("flags weakened risk as a regression", () => {
    const after = { ...baseSpec, risk: "low" as const };
    const result = diffSpecs(baseSpec, after);
    expect(
      result.regressions.some((r) => r.includes("Risk level weakened"))
    ).toBe(true);
  });

  it("flags strengthened risk as an improvement", () => {
    const before = { ...baseSpec, risk: "low" as const };
    const result = diffSpecs(before, baseSpec);
    expect(
      result.improvements.some((i) => i.includes("Risk level strengthened"))
    ).toBe(true);
  });

  it("flags removed postconditions as regressions", () => {
    const after = {
      ...baseSpec,
      contract: { ...baseSpec.contract, postconditions: ["b > 0"] }
    };
    const result = diffSpecs(baseSpec, after);
    expect(
      result.regressions.some((r) => r.includes("Postcondition removed"))
    ).toBe(true);
  });

  it("flags removed BDD scenarios as regressions", () => {
    const after = {
      ...baseSpec,
      bdd: [
        { name: "scenario_b", given: {}, when: {}, then: { ok: true } }
      ]
    };
    const result = diffSpecs(baseSpec, after);
    expect(
      result.regressions.some((r) =>
        r.includes("BDD scenario removed: 'scenario_a'")
      )
    ).toBe(true);
  });

  it("flags removed policies as regressions", () => {
    const after = { ...baseSpec, policies: [] };
    const result = diffSpecs(baseSpec, after);
    expect(
      result.regressions.some((r) =>
        r.includes("Policy removed: 'no_network_calls'")
      )
    ).toBe(true);
  });
});
