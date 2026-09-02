#!/usr/bin/env node
import { Command } from "commander";
import pc from "picocolors";
import { loadSpec, SpecLoadError } from "./loadSpec.js";
import { GitDiffError, loadSpecsForGitDiff } from "./gitDiff.js";
import { checkSpec, printCheckResult } from "./check.js";
import { diffSpecs, printDiffResult } from "./diff.js";
import { buildCodegenPrompt } from "./prompt.js";
import type { PostulateSpec } from "./spec.js";

const program = new Command();

program
  .name("postulate")
  .description("Spec-anchored development for AI-generated code.")
  .version("0.1.0");

function safeLoad(specPath: string): PostulateSpec {
  try {
    return loadSpec(specPath);
  } catch (err) {
    if (err instanceof SpecLoadError) {
      console.error(pc.red(err.message));
      process.exit(2);
    }
    throw err;
  }
}

program
  .command("check")
  .argument("<spec-file>")
  .description("Validate a Postulate YAML spec.")
  .action((file: string) => {
    const spec = safeLoad(file);
    const result = checkSpec(spec);
    printCheckResult(result);
    if (!result.ok) process.exit(1);
  });

program
  .command("prompt")
  .argument("<spec-file>")
  .description("Build an LLM codegen prompt from a spec.")
  .action((file: string) => {
    const spec = safeLoad(file);
    console.log(buildCodegenPrompt(spec));
  });

program
  .command("ci")
  .argument("<spec-file>")
  .option(
    "--fail-on-warnings",
    "Exit non-zero if any warnings are reported.",
    false
  )
  .description(
    "CI-oriented check: same as 'check', but optionally treats warnings as failures."
  )
  .action((file: string, opts: { failOnWarnings: boolean }) => {
    const spec = safeLoad(file);
    const result = checkSpec(spec);
    printCheckResult(result);
    const warnFail = opts.failOnWarnings && result.warnings.length > 0;
    if (!result.ok || warnFail) process.exit(1);
  });

program
  .command("diff")
  .option(
    "--git <ref>",
    "Compare the spec at a git ref to the working tree version."
  )
  .argument("<before-or-spec>", "Before path, or spec path when using --git")
  .argument("[after]", "After path when not using --git")
  .description(
    "Show regressions between two specs (dropped invariants, weakened risk, removed postconditions)."
  )
  .action((beforeOrSpec: string, afterPath: string | undefined, opts: { git?: string }) => {
    if (opts.git) {
      if (afterPath) {
        console.error(
          pc.red(
            "Use either 'diff <before> <after>' or 'diff --git <ref> <spec-file>'."
          )
        );
        process.exit(2);
      }
      let before: PostulateSpec;
      let after: PostulateSpec;
      try {
        ({ before, after } = loadSpecsForGitDiff(opts.git, beforeOrSpec));
      } catch (err) {
        if (err instanceof SpecLoadError || err instanceof GitDiffError) {
          console.error(pc.red(err.message));
          process.exit(2);
        }
        throw err;
      }
      const result = diffSpecs(before, after);
      const ok = printDiffResult(result);
      if (!ok) process.exit(1);
      return;
    }

    if (!afterPath) {
      console.error(pc.red("diff requires two file paths unless --git is used."));
      process.exit(2);
    }

    const before = safeLoad(beforeOrSpec);
    const after = safeLoad(afterPath);
    const result = diffSpecs(before, after);
    const ok = printDiffResult(result);
    if (!ok) process.exit(1);
  });

program.parse();
