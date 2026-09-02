import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { afterEach, describe, expect, it } from "vitest";
const tempDirs: string[] = [];
const cliPath = path.resolve("src/index.ts");

function writeTempSpec(contents: string, name = "postulate.yaml"): string {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "postulate-cli-"));
  tempDirs.push(dir);
  const file = path.join(dir, name);
  fs.writeFileSync(file, contents, "utf8");
  return file;
}

function runCli(...args: string[]) {
  return spawnSync(process.execPath, ["--import", "tsx", cliPath, ...args], {
    cwd: process.cwd(),
    encoding: "utf8",
    env: { ...process.env, NO_COLOR: "1" }
  });
}

const validSpec = `
feature: example
risk: medium
contract:
  preconditions:
    - input exists
    - input is valid
  postconditions:
    - output exists
bdd:
  - name: example_scenario
    then:
      result: true
test_mapping:
  example_scenario: example.test.ts > example_scenario
`;

const warningOnlySpec = `
feature: example
risk: medium
contract:
  preconditions:
    - input exists
  postconditions:
    - output exists
bdd:
  - name: example_scenario
    then:
      result: true
test_mapping:
  example_scenario: example.test.ts > example_scenario
`;

const invalidCheckSpec = `
feature: example
risk: high
contract:
  preconditions:
    - input exists
    - input is valid
  postconditions:
    - output exists
bdd:
  - name: example_scenario
    then:
      result: true
test_mapping:
  example_scenario: example.test.ts > example_scenario
`;

afterEach(() => {
  for (const dir of tempDirs.splice(0)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

describe("CLI exit behavior", () => {
  it("returns 2 when the spec cannot be loaded", () => {
    const result = runCli("check", path.join(os.tmpdir(), "definitely-missing-postulate.yaml"));

    expect(result.status).toBe(2);
    expect(result.stderr).toContain("Spec file not found");
  });

  it("returns 1 when structural checks fail", () => {
    const result = runCli("check", writeTempSpec(invalidCheckSpec));

    expect(result.status).toBe(1);
  });

  it("returns 0 when check succeeds", () => {
    const result = runCli("check", writeTempSpec(validSpec));

    expect(result.status).toBe(0);
  });

  it("does not fail warning-only ci by default", () => {
    const result = runCli("ci", writeTempSpec(warningOnlySpec));

    expect(result.status).toBe(0);
  });

  it("fails warning-only ci with --fail-on-warnings", () => {
    const result = runCli("ci", writeTempSpec(warningOnlySpec), "--fail-on-warnings");

    expect(result.status).toBe(1);
  });

  it("prints a prompt and exits 0", () => {
    const result = runCli("prompt", writeTempSpec(validSpec));

    expect(result.status).toBe(0);
    expect(result.stdout).toContain("Do not invent behavior outside the spec");
    expect(result.stdout).toContain('"feature": "example"');
  });

  it("returns 1 when diff finds a regression", () => {
    const before = writeTempSpec(`
feature: example
risk: medium
contract:
  preconditions:
    - input exists
    - input is valid
  postconditions:
    - output exists
    - output is stable
invariants:
  - deterministic_output
bdd:
  - name: example_scenario
    then:
      result: true
test_mapping:
  deterministic_output: example.test.ts > deterministic_output
  example_scenario: example.test.ts > example_scenario
`, "before.yaml");

    const after = writeTempSpec(validSpec, "after.yaml");
    const result = runCli("diff", before, after);

    expect(result.status).toBe(1);
  });

  it("returns 1 when diff --git finds a regression", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "postulate-git-"));
    tempDirs.push(dir);

    const specV1 = `
feature: example
risk: medium
contract:
  preconditions:
    - input exists
    - input is valid
  postconditions:
    - output exists
invariants:
  - deterministic_output
bdd:
  - name: example_scenario
    then:
      result: true
test_mapping:
  deterministic_output: example.test.ts > deterministic_output
  example_scenario: example.test.ts > example_scenario
`;

    const specV2 = `
feature: example
risk: medium
contract:
  preconditions:
    - input exists
    - input is valid
  postconditions:
    - output exists
invariants: []
bdd:
  - name: example_scenario
    then:
      result: true
test_mapping:
  example_scenario: example.test.ts > example_scenario
`;

    const specPath = path.join(dir, "postulate.yaml");
    fs.writeFileSync(specPath, specV1, "utf8");

    const git = (...args: string[]) =>
      spawnSync("git", args, { cwd: dir, encoding: "utf8" });

    git("init");
    git("config", "user.email", "test@example.com");
    git("config", "user.name", "Test");
    git("add", ".");
    git("commit", "-m", "initial");

    fs.writeFileSync(specPath, specV2, "utf8");

    const result = runCli("diff", "--git", "HEAD", specPath);
    expect(result.status).toBe(1);
    expect(result.stdout).toContain("deterministic_output");
  });
});
