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

function runGit(args: string[], cwd: string): { ok: boolean; stdout: string; stderr: string } {
  const result = spawnSync("git", args, { cwd, encoding: "utf8" });
  return {
    ok: result.status === 0,
    stdout: result.stdout ?? "",
    stderr: result.stderr ?? ""
  };
}

function findGitRoot(start: string): string {
  const result = runGit(["rev-parse", "--show-toplevel"], start);
  if (!result.ok) {
    const detail = result.stderr.trim() || "git rev-parse failed";
    throw new GitDiffError(`Not a git repository: ${detail}`);
  }
  return result.stdout.trim();
}

function repoRelativeSpecPath(specPath: string, gitRoot: string): string {
  const resolved = fs.realpathSync(path.resolve(specPath));
  const resolvedRoot = fs.realpathSync(path.resolve(gitRoot));
  const relativePath = path.relative(resolvedRoot, resolved);
  if (relativePath.startsWith("..") || path.isAbsolute(relativePath)) {
    throw new GitDiffError(
      `Spec file ${specPath} is outside the git repository at ${gitRoot}`
    );
  }
  return relativePath.split(path.sep).join("/");
}

function gitShowAtRef(ref: string, repoRelativePath: string, cwd: string): string {
  const result = runGit(["show", `${ref}:${repoRelativePath}`], cwd);
  if (!result.ok) {
    const stderr = result.stderr.trim() || result.stdout.trim();
    if (/bad revision|unknown revision|invalid object name/i.test(stderr)) {
      throw new GitDiffError(`Git ref not found: ${ref}`);
    }
    if (
      /does not exist|exists on disk|pathspec/i.test(stderr)
    ) {
      throw new GitDiffError(`Spec not found at ${ref}:${repoRelativePath}`);
    }
    throw new GitDiffError(
      `git show ${ref}:${repoRelativePath} failed: ${stderr}`
    );
  }
  return result.stdout;
}

export function loadSpecAtGitRef(ref: string, specPath: string): PostulateSpec {
  const abs = path.resolve(specPath);
  const gitRoot = findGitRoot(path.dirname(abs));
  const repoPath = repoRelativeSpecPath(abs, gitRoot);
  const source = `${ref}:${repoPath}`;
  try {
    const content = gitShowAtRef(ref, repoPath, gitRoot);
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
  specPath: string
): { before: PostulateSpec; after: PostulateSpec } {
  return {
    before: loadSpecAtGitRef(ref, specPath),
    after: loadSpec(specPath)
  };
}
