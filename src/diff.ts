import pc from "picocolors";
import type { PostulateSpec } from "./spec.js";

const RISK_ORDER = { low: 0, medium: 1, high: 2, critical: 3 } as const;

export type DiffResult = {
  regressions: string[];
  improvements: string[];
};

export function diffSpecs(
  before: PostulateSpec,
  after: PostulateSpec
): DiffResult {
  const regressions: string[] = [];
  const improvements: string[] = [];

  // Risk weakening is a regression; strengthening is an improvement.
  const beforeRisk = RISK_ORDER[before.risk];
  const afterRisk = RISK_ORDER[after.risk];
  if (afterRisk < beforeRisk) {
    regressions.push(`Risk level weakened: ${before.risk} -> ${after.risk}`);
  } else if (afterRisk > beforeRisk) {
    improvements.push(
      `Risk level strengthened: ${before.risk} -> ${after.risk}`
    );
  }

  diffSets(
    "Invariant",
    before.invariants,
    after.invariants,
    regressions,
    improvements
  );

  diffSets(
    "Postcondition",
    before.contract.postconditions,
    after.contract.postconditions,
    regressions,
    improvements
  );

  diffSets(
    "BDD scenario",
    before.bdd.map((b) => b.name),
    after.bdd.map((b) => b.name),
    regressions,
    improvements
  );

  diffSets(
    "Policy",
    before.policies,
    after.policies,
    regressions,
    improvements
  );

  return { regressions, improvements };
}

function diffSets(
  label: string,
  beforeItems: string[],
  afterItems: string[],
  regressions: string[],
  improvements: string[]
): void {
  const before = new Set(beforeItems);
  const after = new Set(afterItems);
  for (const item of before) {
    if (!after.has(item)) regressions.push(`${label} removed: '${item}'`);
  }
  for (const item of after) {
    if (!before.has(item)) improvements.push(`${label} added: '${item}'`);
  }
}

export function printDiffResult(result: DiffResult): boolean {
  for (const r of result.regressions) console.log(pc.red(`- ${r}`));
  for (const i of result.improvements) console.log(pc.green(`+ ${i}`));
  if (result.regressions.length === 0 && result.improvements.length === 0) {
    console.log(pc.dim("No material spec changes."));
  } else if (result.regressions.length === 0) {
    console.log(pc.green(`✓ no regressions (${result.improvements.length} improvement(s))`));
  } else {
    console.log(
      pc.red(
        `✗ ${result.regressions.length} regression(s) detected`
      )
    );
  }
  return result.regressions.length === 0;
}
