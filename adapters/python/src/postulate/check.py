from __future__ import annotations

from dataclasses import dataclass

from postulate.invariants import KNOWN_INVARIANT_NAMES
from postulate.models import PostulateSpec


@dataclass
class CheckResult:
    ok: bool
    errors: list[str]
    warnings: list[str]
    info: list[str]


def check_spec(spec: PostulateSpec) -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    high_risk = spec.risk in {"high", "critical"}
    if high_risk:
        if not spec.invariants:
            errors.append(
                f"Risk level '{spec.risk}' requires at least one invariant."
            )
        if not spec.correctness_argument:
            warnings.append(
                f"Risk level '{spec.risk}' should include a correctness_argument before merge."
            )

    for scenario in spec.bdd:
        if not scenario.then:
            errors.append(
                f"Scenario '{scenario.name}' must include at least one expected result in 'then'."
            )

    for invariant in spec.invariants:
        if invariant not in spec.test_mapping:
            errors.append(
                f"Invariant '{invariant}' has no entry in test_mapping — "
                "every named invariant must point to a test that exercises it."
            )

    bdd_names = {scenario.name for scenario in spec.bdd}
    for scenario in spec.bdd:
        if scenario.name not in spec.test_mapping:
            warnings.append(
                f"BDD scenario '{scenario.name}' has no entry in test_mapping."
            )

    if (
        len(spec.contract.preconditions) + len(spec.contract.postconditions)
        < 3
    ):
        warnings.append(
            "Contract is thin. Consider adding more precise preconditions or postconditions."
        )

    recognized = [name for name in spec.invariants if name in KNOWN_INVARIANT_NAMES]
    custom = [name for name in spec.invariants if name not in KNOWN_INVARIANT_NAMES]
    if recognized:
        info.append(f"Recognised invariants: {', '.join(recognized)}")
    if custom:
        info.append(
            f"Custom invariants (no built-in semantics yet): {', '.join(custom)}"
        )

    _ = bdd_names  # reserved for verify classification
    return CheckResult(ok=not errors, errors=errors, warnings=warnings, info=info)


def print_check_result(result: CheckResult) -> None:
    for message in result.info:
        print(f"i {message}")
    for message in result.warnings:
        print(f"! {message}")
    for message in result.errors:
        print(f"✗ {message}")
    if result.ok:
        print("✓ postulate checks passed")
    else:
        count = len(result.errors)
        suffix = "" if count == 1 else "s"
        print(f"✗ postulate checks failed ({count} error{suffix})")
