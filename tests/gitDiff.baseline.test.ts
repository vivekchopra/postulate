import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { afterEach, describe, expect, it } from "vitest";

const tempDirs: string[] = [];
const cliPath = path.resolve("src/index.ts");

const baseSpec = `
feature: git_g0_fixture
risk: high
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
    given: {}
    when: {}
    then:
      ok: true
test_mapping:
  deterministic_output: tests/test_example.py::test_one
  example_scenario: tests/test_example.py::test_two
`;

function runCli(...args: string[]) {
  return spawnSync(process.execPath, ["--import", "tsx", cliPath, ...args], {
    cwd: process.cwd(),
    encoding: "utf8",
    env: { ...process.env, NO_COLOR: "1" }
  });
}

function initGitRepo(dir: string): string {
  const specPath = path.join(dir, "postulate.yaml");
  fs.writeFileSync(specPath, baseSpec, "utf8");

  const git = (...gitArgs: string[]) =>
    spawnSync("git", gitArgs, { cwd: dir, encoding: "utf8" });

  git("init");
  git("config", "user.email", "test@example.com");
  git("config", "user.name", "Test User");
  git("add", "postulate.yaml");
  git("commit", "-m", "initial spec");

  return specPath;
}

afterEach(() => {
  for (const dir of tempDirs.splice(0)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

describe("git diff G0 regressions", () => {
  it("G-05: missing working-tree spec must exit 2 with readable load error", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "postulate-g0-ts-"));
    tempDirs.push(dir);
    const specPath = initGitRepo(dir);
    fs.unlinkSync(specPath);

    const result = runCli("diff", "--git", "HEAD", specPath);
    const combined = `${result.stdout}\n${result.stderr}`;

    expect(result.status).toBe(2);
    expect(combined).toContain("Spec file not found");
    expect(combined).not.toContain("Traceback");
    expect(combined).not.toMatch(/Error: ENOENT.*lstat/);
  });

  it("G-06: missing Git executable must exit 2 with actionable diagnostic", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "postulate-g0-ts-"));
    tempDirs.push(dir);
    const specPath = initGitRepo(dir);

    const nodeBin = path.dirname(process.execPath);
    const result = spawnSync(
      process.execPath,
      ["--import", "tsx", cliPath, "diff", "--git", "HEAD", specPath],
      {
        cwd: process.cwd(),
        encoding: "utf8",
        env: { PATH: nodeBin, NO_COLOR: "1" }
      }
    );
    const combined = `${result.stdout}\n${result.stderr}`;

    expect(result.status).toBe(2);
    expect(combined.toLowerCase()).toMatch(/git/);
    expect(combined).not.toContain("Traceback");
    expect(combined).not.toMatch(/Error: ENOENT.*spawn/);
  });
});
