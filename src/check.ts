import pc from "picocolors";
import type { PostulateSpec } from "./spec.js";
import { KNOWN_INVARIANT_NAMES } from "./invariants.js";

export type CheckResult = {
  ok: boolean;
  errors: string[];
  warnings: string[];
  info: string[];
};

export function checkSpec(spec: PostulateSpec): CheckResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  const info: string[] = [];

  // Risk-based rules.
  const highRisk = spec.risk === "high" || spec.risk === "critical";
  if (highRisk) {
    if (spec.invariants.length === 0) {
      errors.push(
        `Risk level '${spec.risk}' requires at least one invariant.`
      );
    }
    if (!spec.correctness_argument) {
      warnings.push(
        `Risk level '${spec.risk}' should include a correctness_argument before merge.`
      );
    }
  }

  // Every BDD scenario must specify expected outcomes.
  for (const scenario of spec.bdd) {
    if (Object.keys(scenario.then).length === 0) {
      errors.push(
        `Scenario '${scenario.name}' must include at least one expected result in 'then'.`
      );
    }
  }

  // Core enforcement: every named invariant must point at a test.
  // This is the rule that turns "list it in YAML and ignore it in code"
  // from a silent failure into a CI failure.
  for (const invariant of spec.invariants) {
    if (!(invariant in spec.test_mapping)) {
      errors.push(
        `Invariant '${invariant}' has no entry in test_mapping — ` +
          `every named invariant must point to a test that exercises it.`
      );
    }
  }

  // Every BDD scenario should also map to a test, but at warning level
  // since the scenario itself can sometimes be the test in some frameworks.
  for (const scenario of spec.bdd) {
    if (!(scenario.name in spec.test_mapping)) {
      warnings.push(
        `BDD scenario '${scenario.name}' has no entry in test_mapping.`
      );
    }
  }

  // Thin-contract warning.
  if (
    spec.contract.preconditions.length + spec.contract.postconditions.length <
    3
  ) {
    warnings.push(
      "Contract is thin. Consider adding more precise preconditions or postconditions."
    );
  }

  // Informational: surface which invariants Postulate recognises and which
  // are custom (so the author knows when they're on their own).
  const recognized = spec.invariants.filter((i) =>
    KNOWN_INVARIANT_NAMES.has(i)
  );
  const custom = spec.invariants.filter((i) => !KNOWN_INVARIANT_NAMES.has(i));
  if (recognized.length > 0) {
    info.push(`Recognised invariants: ${recognized.join(", ")}`);
  }
  if (custom.length > 0) {
    info.push(
      `Custom invariants (no built-in semantics yet): ${custom.join(", ")}`
    );
  }

  return { ok: errors.length === 0, errors, warnings, info };
}

export function printCheckResult(result: CheckResult): void {
  for (const i of result.info) console.log(pc.dim(`i ${i}`));
  for (const w of result.warnings) console.warn(pc.yellow(`! ${w}`));
  for (const e of result.errors) console.error(pc.red(`✗ ${e}`));
  if (result.ok) {
    console.log(pc.green("✓ postulate checks passed"));
  } else {
    const n = result.errors.length;
    console.log(pc.red(`✗ postulate checks failed (${n} error${n === 1 ? "" : "s"})`));
  }
}
