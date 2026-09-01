from __future__ import annotations

from dataclasses import dataclass

from postulate.models import PostulateSpec

RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


@dataclass
class DiffResult:
    regressions: list[str]
    improvements: list[str]


def diff_specs(before: PostulateSpec, after: PostulateSpec) -> DiffResult:
    regressions: list[str] = []
    improvements: list[str] = []

    before_risk = RISK_ORDER[before.risk]
    after_risk = RISK_ORDER[after.risk]
    if after_risk < before_risk:
        regressions.append(f"Risk level weakened: {before.risk} -> {after.risk}")
    elif after_risk > before_risk:
        improvements.append(
            f"Risk level strengthened: {before.risk} -> {after.risk}"
        )

    _diff_sets("Invariant", before.invariants, after.invariants, regressions, improvements)
    _diff_sets(
        "Postcondition",
        before.contract.postconditions,
        after.contract.postconditions,
        regressions,
        improvements,
    )
    _diff_sets(
        "BDD scenario",
        [scenario.name for scenario in before.bdd],
        [scenario.name for scenario in after.bdd],
        regressions,
        improvements,
    )
    _diff_sets("Policy", before.policies, after.policies, regressions, improvements)

    return DiffResult(regressions=regressions, improvements=improvements)


def _diff_sets(
    label: str,
    before_items: list[str],
    after_items: list[str],
    regressions: list[str],
    improvements: list[str],
) -> None:
    before = set(before_items)
    after = set(after_items)
    for item in before:
        if item not in after:
            regressions.append(f"{label} removed: '{item}'")
    for item in after:
        if item not in before:
            improvements.append(f"{label} added: '{item}'")


def print_diff_result(result: DiffResult) -> bool:
    for regression in result.regressions:
        print(f"- {regression}")
    for improvement in result.improvements:
        print(f"+ {improvement}")
    if not result.regressions and not result.improvements:
        print("No material spec changes.")
    elif not result.regressions:
        count = len(result.improvements)
        print(f"✓ no regressions ({count} improvement(s))")
    else:
        count = len(result.regressions)
        print(f"✗ {count} regression(s) detected")
    return not result.regressions
