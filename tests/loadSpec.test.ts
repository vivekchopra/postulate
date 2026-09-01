import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { loadSpec, SpecLoadError } from "../src/loadSpec.js";

const tempDirs: string[] = [];

function writeTempSpec(contents: string): string {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "postulate-load-"));
  tempDirs.push(dir);
  const file = path.join(dir, "postulate.yaml");
  fs.writeFileSync(file, contents, "utf8");
  return file;
}

afterEach(() => {
  for (const dir of tempDirs.splice(0)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

describe("loadSpec", () => {
  it("loads a valid YAML spec and applies defaults", () => {
    const file = writeTempSpec(`
feature: example
contract:
  preconditions:
    - input exists
  postconditions:
    - output exists
bdd:
  - name: example_scenario
    then:
      result: true
`);

    const spec = loadSpec(file);

    expect(spec.feature).toBe("example");
    expect(spec.risk).toBe("medium");
    expect(spec.invariants).toEqual([]);
    expect(spec.policies).toEqual([]);
    expect(spec.test_mapping).toEqual({});
  });

  it("throws SpecLoadError for a missing file", () => {
    const missing = path.join(os.tmpdir(), `postulate-missing-${Date.now()}.yaml`);

    expect(() => loadSpec(missing)).toThrowError(SpecLoadError);
    expect(() => loadSpec(missing)).toThrow(`Spec file not found: ${path.resolve(missing)}`);
  });

  it("throws SpecLoadError for invalid YAML", () => {
    const file = writeTempSpec("feature: [unterminated\n");

    expect(() => loadSpec(file)).toThrowError(SpecLoadError);
    expect(() => loadSpec(file)).toThrow("Invalid YAML");
  });

  it("includes the failing field path for schema errors", () => {
    const file = writeTempSpec(`
feature: example
contract:
  preconditions: []
  postconditions:
    - output exists
bdd:
  - name: example_scenario
    then:
      result: true
`);

    expect(() => loadSpec(file)).toThrowError(SpecLoadError);
    expect(() => loadSpec(file)).toThrow("contract.preconditions");
  });
});
