import fs from "node:fs";
import path from "node:path";
import YAML from "yaml";
import { z } from "zod";
import { PostulateSchema, type PostulateSpec } from "./spec.js";

export class SpecLoadError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "SpecLoadError";
  }
}

export function loadSpec(specPath: string): PostulateSpec {
  const abs = path.resolve(specPath);

  let raw: string;
  try {
    raw = fs.readFileSync(abs, "utf8");
  } catch (err) {
    const code = (err as NodeJS.ErrnoException).code;
    if (code === "ENOENT") {
      throw new SpecLoadError(`Spec file not found: ${abs}`);
    }
    throw new SpecLoadError(
      `Could not read spec file ${abs}: ${(err as Error).message}`
    );
  }

  return loadSpecFromContent(raw, specPath);
}

export function loadSpecFromContent(raw: string, source: string): PostulateSpec {
  let parsed: unknown;
  try {
    parsed = YAML.parse(raw);
  } catch (err) {
    throw new SpecLoadError(
      `Invalid YAML in ${source}: ${(err as Error).message}`
    );
  }

  try {
    return PostulateSchema.parse(parsed);
  } catch (err) {
    if (err instanceof z.ZodError) {
      const issues = err.issues
        .map((issue) => {
          const where = issue.path.length > 0 ? issue.path.join(".") : "<root>";
          return `  - ${where}: ${issue.message}`;
        })
        .join("\n");
      throw new SpecLoadError(
        `Spec ${source} failed schema validation:\n${issues}`
      );
    }
    throw err;
  }
}
