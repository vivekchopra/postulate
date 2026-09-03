import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { loadSpec, loadSpecFromContent, SpecLoadError } from "./loadSpec.js";
import type { PostulateSpec } from "./spec.js";

export class GitDiffError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "GitDiffError";
  }
}

function isEnoent(err: unknown): boolean {
  return (
    typeof err === "object" &&
    err !== null &&
    "code" in err &&
    (err as { code?: string }).code === "ENOENT"
  );
}

function runGit(
  args: string[],
  cwd: string
): { ok: boolean; stdout: string; stderr: string } {
  const result = spawnSync("git", args, { cwd, encoding: "utf8" });
  if (result.error) {
    if (isEnoent(result.error)) {
      throw new GitDiffError("Git executable not found on PATH");
    }
    throw new GitDiffError(`Could not run git: ${result.error.message}`);
  }
  return {
    ok: result.status === 0,
    stdout: result.stdout ?? "",
    stderr: result.stderr ?? ""
  };
}

export function findGitRoot(cwd: string = process.cwd()): string {
  let start: string;
  try {
    start = path.resolve(cwd);
    if (!fs.statSync(start).isDirectory()) {
      throw new GitDiffError(`Working directory is not accessible: ${start}`);
    }
  } catch (err) {
    if (err instanceof GitDiffError) throw err;
    throw new GitDiffError(
      `Working directory is not accessible: ${path.resolve(cwd)}`
    );
  }

  const result = runGit(["rev-parse", "--show-toplevel"], start);
  if (!result.ok) {
    throw new GitDiffError(
      "Not a git repository (git rev-parse --show-toplevel failed)"
    );
  }
  return result.stdout.trim();
}

function resolveSpecPath(specPath: string, cwd: string): string {
  return path.isAbsolute(specPath) ? specPath : path.resolve(cwd, specPath);
}

/** Reject paths that escape root using path components (allows `..spec.yaml`). */
function isOutsideRepo(root: string, target: string): boolean {
  const relativePath = path.relative(root, target);
  return (
    relativePath === ".." ||
    relativePath.startsWith(`..${path.sep}`) ||
    path.isAbsolute(relativePath)
  );
}

export function validateWorkingSpecFile(
  specPath: string,
  gitRoot: string
): { resolved: string; repoRelative: string } {
  let lstat: fs.Stats;
  try {
    lstat = fs.lstatSync(specPath);
  } catch (err) {
    if (isEnoent(err)) {
      throw new SpecLoadError(`Spec file not found: ${specPath}`);
    }
    throw new GitDiffError(`Could not read spec path: ${specPath}`);
  }

  if (lstat.isSymbolicLink()) {
    throw new GitDiffError(
      `Spec file must be a regular file, not a symlink: ${specPath}`
    );
  }
  if (!lstat.isFile()) {
    throw new GitDiffError(`Spec path is not a regular file: ${specPath}`);
  }

  const resolved = fs.realpathSync(specPath);
  const root = fs.realpathSync(gitRoot);
  if (isOutsideRepo(root, resolved)) {
    throw new GitDiffError(
      `Spec file ${specPath} is outside the git repository at ${gitRoot}`
    );
  }

  const repoRelative = path.relative(root, resolved).split(path.sep).join("/");
  return { resolved, repoRelative };
}

export function resolveCommit(ref: string, cwd: string): string {
  const trimmed = ref.trim();
  if (!trimmed) {
    throw new GitDiffError("Git ref must not be empty");
  }

  const result = runGit(
    ["rev-parse", "--verify", "--end-of-options", `${trimmed}^{commit}`],
    cwd
  );
  if (!result.ok) {
    throw new GitDiffError(`Git ref not found: ${ref}`);
  }
  return result.stdout.trim();
}

function gitShowSpecAtCommit(
  commit: string,
  repoRelativePath: string,
  cwd: string
): string {
  const exists = runGit(["cat-file", "-e", `${commit}:${repoRelativePath}`], cwd);
  if (!exists.ok) {
    throw new GitDiffError(`Spec not found at ${commit}:${repoRelativePath}`);
  }

  const result = runGit(["show", `${commit}:${repoRelativePath}`], cwd);
  if (!result.ok) {
    throw new GitDiffError(
      `Could not read spec at ${commit}:${repoRelativePath}`
    );
  }
  return result.stdout;
}

export function loadSpecAtGitRef(
  ref: string,
  specPath: string,
  cwd: string = process.cwd()
): PostulateSpec {
  const invocationCwd = path.resolve(cwd);
  const gitRoot = findGitRoot(invocationCwd);
  const resolvedSpec = resolveSpecPath(specPath, invocationCwd);
  const { repoRelative } = validateWorkingSpecFile(resolvedSpec, gitRoot);
  const commit = resolveCommit(ref, gitRoot);
  const source = `${commit}:${repoRelative}`;
  try {
    const content = gitShowSpecAtCommit(commit, repoRelative, gitRoot);
    return loadSpecFromContent(content, source);
  } catch (err) {
    if (err instanceof GitDiffError) {
      throw new SpecLoadError(err.message);
    }
    throw err;
  }
}

export function loadSpecsForGitDiff(
  ref: string,
  specPath: string,
  cwd: string = process.cwd()
): { before: PostulateSpec; after: PostulateSpec } {
  const invocationCwd = path.resolve(cwd);
  const gitRoot = findGitRoot(invocationCwd);
  const resolvedSpec = resolveSpecPath(specPath, invocationCwd);
  const { resolved, repoRelative } = validateWorkingSpecFile(
    resolvedSpec,
    gitRoot
  );
  const commit = resolveCommit(ref, gitRoot);
  let content: string;
  try {
    content = gitShowSpecAtCommit(commit, repoRelative, gitRoot);
  } catch (err) {
    if (err instanceof GitDiffError) {
      throw new SpecLoadError(err.message);
    }
    throw err;
  }
  const before = loadSpecFromContent(content, `${commit}:${repoRelative}`);
  const after = loadSpec(resolved);
  return { before, after };
}
