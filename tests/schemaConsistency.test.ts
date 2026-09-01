import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { PostulateSchema } from "../src/spec.js";

type JsonSchema = {
  required?: string[];
  properties?: Record<string, JsonSchema & {
    enum?: string[];
    default?: unknown;
    minLength?: number;
    minItems?: number;
    items?: JsonSchema;
  }>;
  enum?: string[];
  default?: unknown;
  minLength?: number;
  minItems?: number;
  items?: JsonSchema;
};

const schemaPath = path.resolve("schemas/postulate.schema.json");
const jsonSchema = JSON.parse(fs.readFileSync(schemaPath, "utf8")) as JsonSchema;

function requiredSet(schema: JsonSchema): Set<string> {
  return new Set(schema.required ?? []);
}

describe("JSON Schema mirror", () => {
  it("matches the Zod schema's required top-level fields", () => {
    expect(requiredSet(jsonSchema)).toEqual(new Set(["feature", "contract", "bdd"]));

    const minimal = {
      feature: "example",
      contract: { preconditions: ["input"], postconditions: ["output"] },
      bdd: [{ name: "scenario" }]
    };
    expect(PostulateSchema.safeParse(minimal).success).toBe(true);
  });

  it("matches required contract and scenario fields", () => {
    const contract = jsonSchema.properties?.contract;
    const scenario = jsonSchema.properties?.bdd?.items;

    expect(requiredSet(contract ?? {})).toEqual(new Set(["preconditions", "postconditions"]));
    expect(requiredSet(scenario ?? {})).toEqual(new Set(["name"]));

    expect(PostulateSchema.safeParse({
      feature: "example",
      contract: { preconditions: ["input"], postconditions: ["output"] },
      bdd: [{ name: "scenario" }]
    }).success).toBe(true);
  });

  it("mirrors non-empty string and array constraints", () => {
    expect(jsonSchema.properties?.feature?.minLength).toBe(1);
    expect(jsonSchema.properties?.contract?.properties?.preconditions?.minItems).toBe(1);
    expect(jsonSchema.properties?.contract?.properties?.postconditions?.minItems).toBe(1);
    expect(jsonSchema.properties?.bdd?.minItems).toBe(1);
    expect(jsonSchema.properties?.bdd?.items?.properties?.name?.minLength).toBe(1);

    expect(PostulateSchema.safeParse({
      feature: "",
      contract: { preconditions: ["input"], postconditions: ["output"] },
      bdd: [{ name: "scenario" }]
    }).success).toBe(false);
  });

  it("mirrors risk values and defaults", () => {
    expect(jsonSchema.properties?.risk?.enum).toEqual(["low", "medium", "high", "critical"]);
    expect(jsonSchema.properties?.risk?.default).toBe("medium");

    const parsed = PostulateSchema.parse({
      feature: "example",
      contract: { preconditions: ["input"], postconditions: ["output"] },
      bdd: [{ name: "scenario" }]
    });
    expect(parsed.risk).toBe("medium");
  });

  it("documents defaults for defaultable collections and scenario objects", () => {
    expect(jsonSchema.properties?.contract?.properties?.failure_cases?.default).toEqual([]);
    expect(jsonSchema.properties?.invariants?.default).toEqual([]);
    expect(jsonSchema.properties?.policies?.default).toEqual([]);
    expect(jsonSchema.properties?.test_mapping?.default).toEqual({});
    expect(jsonSchema.properties?.bdd?.items?.properties?.given?.default).toEqual({});
    expect(jsonSchema.properties?.bdd?.items?.properties?.when?.default).toEqual({});
    expect(jsonSchema.properties?.bdd?.items?.properties?.then?.default).toEqual({});
  });
});
