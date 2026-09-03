import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { spawnSync } from "node:child_process";
import { afterEach, describe, expect, it } from "vitest";
import {
  findGitRoot,
  GitDiffError,
  loadSpecAtGitRef,
  loadSpecsForGitDiff
} from "../src/gitDiff.js";
import { SpecLoadError } from "../src/loadSpec.js";

const tempDirs: string[] = [];
const cliPath = path.resolve("src/index.ts");
const tsxLoader = createRequire(import.meta.url).resolve("tsx");

const baseSpec = `
feature: git_fixture
risk: high
contract:
  preconditions:
    - input exists
    - input is valid
  postconditions:
    - output exists
invariants:
  - deterministic_output
  - does_not_mutate_input
bdd:
  - name: example_scenario
    given: {}
    when: {}
    then:
      ok: true
test_mapping:
  deterministic_output: tests/test_example.py::test_one
  does_not_mutate_input: tests/test_example.py::test_two
  example_scenario: tests/test_example.py::test_three
`;

const droppedInvariantSpec = `
feature: git_fixture
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
  example_scenario: tests/test_example.py::test_three
`;

function runCli(cwd: string, ...args: string[]) {
  return spawnSync(process.execPath, ["--import", tsxLoader, cliPath, ...args], {
    cwd,
    encoding: "utf8",
    env: { ...process.env, NO_COLOR: "1" }
  });
}

function runGit(cwd: string, ...gitArgs: string[]) {
  const result = spawnSync("git", gitArgs, { cwd, encoding: "utf8" });
  expect(result.status).toBe(0);
  return result;
}

function initDroppedInvariantRepo(): string {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "postulate-git-"));
  tempDirs.push(dir);
  const specPath = path.join(dir, "postulate.yaml");
  fs.writeFileSync(specPath, baseSpec, "utf8");
  runGit(dir, "init");
  runGit(dir, "config", "user.email", "test@example.com");
  runGit(dir, "config", "user.name", "Test User");
  runGit(dir, "add", "postulate.yaml");
  runGit(dir, "commit", "-m", "initial spec");
  fs.writeFileSync(specPath, droppedInvariantSpec, "utf8");
  return dir;
}

afterEach(() => {
  for (const dir of tempDirs.splice(0)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

describe("gitDiff helpers", () => {
  it("finds git root from nested cwd", () => {
    const dir = initDroppedInvariantRepo();
    const nested = path.join(dir, "packages", "nested");
    fs.mkdirSync(nested, { recursive: true });
    expect(fs.realpathSync(findGitRoot(nested))).toBe(fs.realpathSync(dir));
  });

  it("rejects non-repo cwd", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "postulate-nongit-"));
    tempDirs.push(dir);
    expect(() => findGitRoot(dir)).toThrow(GitDiffError);
    expect(() => findGitRoot(dir)).toThrow(/Not a git repository/);
  });

  it("loads historical invariants at HEAD", () => {
    const dir = initDroppedInvariantRepo();
    const spec = loadSpecAtGitRef("HEAD", "postulate.yaml", dir);
    expect(spec.invariants).toContain("does_not_mutate_input");
  });

  it("errors when historical path is absent", () => {
    const dir = initDroppedInvariantRepo();
    const newSpec = path.join(dir, "specs", "new.yaml");
    fs.mkdirSync(path.dirname(newSpec), { recursive: true });
    fs.writeFileSync(newSpec, baseSpec, "utf8");
    expect(() => loadSpecAtGitRef("HEAD", newSpec, dir)).toThrow(SpecLoadError);
    expect(() => loadSpecAtGitRef("HEAD", newSpec, dir)).toThrow(/Spec not found/);
  });
});

describe("diff --git CLI", () => {
  it("detects dropped invariant regression", () => {
    const dir = initDroppedInvariantRepo();
    const result = runCli(dir, "diff", "--git", "HEAD", "postulate.yaml");
    expect(result.status).toBe(1);
    expect(result.stdout).toContain("does_not_mutate_input");
  });

  it("rejects bad refs with exit 2", () => {
    const dir = initDroppedInvariantRepo();
    const result = runCli(dir, "diff", "--git", "not-a-real-ref", "postulate.yaml");
    const combined = `${result.stdout}\n${result.stderr}`;
    expect(result.status).toBe(2);
    expect(combined).toContain("Git ref not found");
  });

  it("rejects empty refs with exit 2", () => {
    const dir = initDroppedInvariantRepo();
    const result = runCli(dir, "diff", "--git", "   ", "postulate.yaml");
    const combined = `${result.stdout}\n${result.stderr}`;
    expect(result.status).toBe(2);
    expect(combined).toContain("Git ref must not be empty");
  });

  it("works from nested cwd with relative path", () => {
    const dir = initDroppedInvariantRepo();
    const nested = path.join(dir, "packages", "nested");
    fs.mkdirSync(nested, { recursive: true });
    const result = runCli(nested, "diff", "--git", "HEAD", "../../postulate.yaml");
    expect(result.status).toBe(1);
    expect(result.stdout).toContain("does_not_mutate_input");
  });

  it("handles spaces in filename", () => {
    const dir = initDroppedInvariantRepo();
    const spaced = path.join(dir, "spec files", "my spec.yaml");
    fs.mkdirSync(path.dirname(spaced), { recursive: true });
    fs.writeFileSync(spaced, baseSpec, "utf8");
    runGit(dir, "add", "spec files/my spec.yaml");
    runGit(dir, "commit", "-m", "add spaced spec");
    fs.writeFileSync(spaced, droppedInvariantSpec, "utf8");

    const result = runCli(dir, "diff", "--git", "HEAD", "spec files/my spec.yaml");
    expect(result.status).toBe(1);
    expect(result.stdout).toContain("does_not_mutate_input");
  });

  it("accepts valid ..spec.yaml filename", () => {
    const dir = initDroppedInvariantRepo();
    const dotted = path.join(dir, "..spec.yaml");
    fs.writeFileSync(dotted, baseSpec, "utf8");
    runGit(dir, "add", "..spec.yaml");
    runGit(dir, "commit", "-m", "add dotted spec");
    fs.writeFileSync(dotted, droppedInvariantSpec, "utf8");

    const result = runCli(dir, "diff", "--git", "HEAD", "..spec.yaml");
    expect(result.status).toBe(1);
    expect(result.stdout).toContain("does_not_mutate_input");
  });

  it("rejects symlinked specs", () => {
    const dir = initDroppedInvariantRepo();
    const link = path.join(dir, "linked.yaml");
    fs.symlinkSync(path.join(dir, "postulate.yaml"), link);

    const result = runCli(dir, "diff", "--git", "HEAD", "linked.yaml");
    const combined = `${result.stdout}\n${result.stderr}`;
    expect(result.status).toBe(2);
    expect(combined.toLowerCase()).toContain("symlink");
  });

  it("rejects specs outside the repository", () => {
    const dir = initDroppedInvariantRepo();
    const outsideDir = fs.mkdtempSync(path.join(os.tmpdir(), "postulate-out-"));
    tempDirs.push(outsideDir);
    const outside = path.join(outsideDir, "outside.yaml");
    fs.writeFileSync(outside, baseSpec, "utf8");

    const result = runCli(dir, "diff", "--git", "HEAD", outside);
    const combined = `${result.stdout}\n${result.stderr}`;
    expect(result.status).toBe(2);
    expect(combined).toContain("outside the git repository");
  });

  it("G-05: missing working-tree spec exits 2", () => {
    const dir = initDroppedInvariantRepo();
    fs.unlinkSync(path.join(dir, "postulate.yaml"));

    const result = runCli(dir, "diff", "--git", "HEAD", "postulate.yaml");
    const combined = `${result.stdout}\n${result.stderr}`;
    expect(result.status).toBe(2);
    expect(combined).toContain("Spec file not found");
    expect(combined).not.toMatch(/Error: ENOENT.*lstat/);
  });

  it("G-06: missing Git executable exits 2", () => {
    const dir = initDroppedInvariantRepo();
    const nodeBin = path.dirname(process.execPath);
    const result = spawnSync(
      process.execPath,
      ["--import", tsxLoader, cliPath, "diff", "--git", "HEAD", "postulate.yaml"],
      {
        cwd: dir,
        encoding: "utf8",
        env: { PATH: nodeBin, NO_COLOR: "1" }
      }
    );
    const combined = `${result.stdout}\n${result.stderr}`;
    expect(result.status).toBe(2);
    expect(combined).toContain("Git executable not found");
    expect(combined).not.toMatch(/Error: ENOENT.*spawn/);
  });

  it("rejects HEAD~1 on a single-commit repo", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "postulate-one-"));
    tempDirs.push(dir);
    fs.writeFileSync(path.join(dir, "postulate.yaml"), baseSpec, "utf8");
    runGit(dir, "init");
    runGit(dir, "config", "user.email", "test@example.com");
    runGit(dir, "config", "user.name", "Test User");
    runGit(dir, "add", "postulate.yaml");
    runGit(dir, "commit", "-m", "only commit");
    fs.writeFileSync(path.join(dir, "postulate.yaml"), droppedInvariantSpec, "utf8");

    const result = runCli(dir, "diff", "--git", "HEAD~1", "postulate.yaml");
    const combined = `${result.stdout}\n${result.stderr}`;
    expect(result.status).toBe(2);
    expect(combined).toContain("Git ref not found");
  });

  it("does not mutate HEAD, index, or working file", () => {
    const dir = initDroppedInvariantRepo();
    const headBefore = runGit(dir, "rev-parse", "HEAD").stdout.trim();
    const statusBefore = runGit(dir, "status", "--porcelain").stdout;
    const workingBefore = fs.readFileSync(path.join(dir, "postulate.yaml"));

    const result = runCli(dir, "diff", "--git", "HEAD", "postulate.yaml");
    expect(result.status).toBe(1);

    expect(runGit(dir, "rev-parse", "HEAD").stdout.trim()).toBe(headBefore);
    expect(runGit(dir, "status", "--porcelain").stdout).toBe(statusBefore);
    expect(fs.readFileSync(path.join(dir, "postulate.yaml"))).toEqual(workingBefore);
  });

  it("reports invalid historical YAML", () => {
    const dir = initDroppedInvariantRepo();
    fs.writeFileSync(path.join(dir, "postulate.yaml"), "feature: [\n", "utf8");
    runGit(dir, "add", "postulate.yaml");
    runGit(dir, "commit", "-m", "bad yaml");
    fs.writeFileSync(path.join(dir, "postulate.yaml"), droppedInvariantSpec, "utf8");

    const result = runCli(dir, "diff", "--git", "HEAD", "postulate.yaml");
    const combined = `${result.stdout}\n${result.stderr}`;
    expect(result.status).toBe(2);
    expect(combined.toLowerCase()).toMatch(/yaml|invalid|parse/);
  });

  it("keeps two-file mode independent of git", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "postulate-two-"));
    tempDirs.push(dir);
    const before = path.join(dir, "before.yaml");
    const after = path.join(dir, "after.yaml");
    fs.writeFileSync(before, baseSpec, "utf8");
    fs.writeFileSync(after, droppedInvariantSpec, "utf8");

    const result = runCli(dir, "diff", before, after);
    expect(result.status).toBe(1);
    expect(result.stdout).toContain("does_not_mutate_input");
  });

  it("rejects mixed git and two-file arguments", () => {
    const dir = initDroppedInvariantRepo();
    const result = runCli(
      dir,
      "diff",
      "--git",
      "HEAD",
      "postulate.yaml",
      "extra.yaml"
    );
    const combined = `${result.stdout}\n${result.stderr}`;
    expect(result.status).toBe(2);
    expect(combined).toMatch(/either|Use either/i);
  });
});

describe("loadSpecsForGitDiff", () => {
  it("returns before/after for regression detection", () => {
    const dir = initDroppedInvariantRepo();
    const { before, after } = loadSpecsForGitDiff("HEAD", "postulate.yaml", dir);
    expect(before.invariants).toContain("does_not_mutate_input");
    expect(after.invariants).not.toContain("does_not_mutate_input");
  });
});
