from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from postulate.models import PostulateSpec


def _normalize_path_portion(path: str) -> str | None:
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("/"):
        return None

    parts: list[str] = []
    for part in normalized.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
        else:
            parts.append(part)
    return "/".join(parts)


def normalize_locator(locator: str) -> tuple[str | None, str | None]:
    stripped = locator.strip()
    if not stripped:
        return None, "empty locator"

    if "::" not in stripped:
        return None, "locator must include ::"

    path_part, qualname = stripped.split("::", 1)
    if not path_part or not qualname:
        return None, "locator must include a file path and node id"

    norm_path = _normalize_path_portion(path_part)
    if norm_path is None:
        return None, "locator path must be root-relative"

    return f"{norm_path}::{qualname}", None


def normalize_node_id(node_id: str, project_root: Path) -> str:
    if "::" not in node_id:
        return node_id.replace("\\", "/")

    raw = node_id.replace("\\", "/")
    path_part, qualname = raw.split("::", 1)
    root = str(project_root.resolve()).replace("\\", "/")

    if path_part.startswith(root + "/"):
        path_part = path_part[len(root) + 1 :]
    elif path_part.startswith("/"):
        norm_path = _normalize_path_portion(path_part)
        if norm_path is None:
            return raw
        return f"{norm_path}::{qualname}"

    norm_path = _normalize_path_portion(path_part)
    if norm_path is None:
        return raw
    return f"{norm_path}::{qualname}"


def _normalize_node_id(node_id: str, project_root: Path) -> str:
    return normalize_node_id(node_id, project_root)


def resolve_locator(locator: str, node_ids: set[str]) -> bool:
    normalized, _ = normalize_locator(locator)
    if normalized is None:
        return False

    if normalized in node_ids:
        return True

    if "[" not in normalized:
        prefix = normalized + "["
        return any(node_id.startswith(prefix) for node_id in node_ids)

    return False


def enumerate_claim_names(spec: PostulateSpec) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for name in spec.invariants:
        if name not in seen:
            ordered.append(name)
            seen.add(name)
    for scenario in spec.bdd:
        if scenario.name not in seen:
            ordered.append(scenario.name)
            seen.add(scenario.name)
    return ordered


def _claim_kinds(spec: PostulateSpec, name: str) -> set[str]:
    kinds: set[str] = set()
    if name in spec.invariants:
        kinds.add("invariant")
    if any(scenario.name == name for scenario in spec.bdd):
        kinds.add("bdd")
    return kinds


def _is_blank_locator(locator: str | None) -> bool:
    return locator is None or not locator.strip()


@dataclass(frozen=True)
class ExerciseSummary:
    invariants_declared: int
    invariants_exercised: int
    bdd_declared: int
    bdd_exercised: int


def _claim_is_exercised(
    spec: PostulateSpec,
    name: str,
    exercised_node_ids: set[str],
) -> bool:
    if name not in spec.test_mapping or _is_blank_locator(spec.test_mapping.get(name)):
        return False
    return resolve_locator(spec.test_mapping[name], exercised_node_ids)


def compute_exercise_summary(
    spec: PostulateSpec,
    exercised_node_ids: set[str],
) -> ExerciseSummary:
    return ExerciseSummary(
        invariants_declared=len(spec.invariants),
        invariants_exercised=sum(
            1 for name in spec.invariants if _claim_is_exercised(spec, name, exercised_node_ids)
        ),
        bdd_declared=len(spec.bdd),
        bdd_exercised=sum(
            1
            for scenario in spec.bdd
            if _claim_is_exercised(spec, scenario.name, exercised_node_ids)
        ),
    )


def _locator_exercise_reason(
    locator: str,
    node_hints: dict[str, str],
) -> str:
    for node_id, hint in sorted(node_hints.items()):
        if resolve_locator(locator, {node_id}):
            return hint
    return "no eligible call report"


def check_exercise_coverage(
    spec: PostulateSpec,
    exercised_node_ids: set[str],
    *,
    node_hints: dict[str, str] | None = None,
    spec_path: Path | None = None,
) -> tuple[list[str], list[str], ExerciseSummary]:
    hints = node_hints or {}
    errors: list[str] = []
    warnings: list[str] = []
    claim_names = set(enumerate_claim_names(spec))
    prefix = f"{spec_path}: " if spec_path else ""

    for name in enumerate_claim_names(spec):
        kinds = _claim_kinds(spec, name)
        locator = spec.test_mapping.get(name)
        is_invariant = "invariant" in kinds

        if name not in spec.test_mapping or _is_blank_locator(locator):
            message = f"{prefix}spec claims '{name}' but mapping is missing"
            if is_invariant:
                errors.append(message)
            else:
                warnings.append(message)
            continue

        assert locator is not None
        if not resolve_locator(locator, exercised_node_ids):
            reason = _locator_exercise_reason(locator, hints)
            message = (
                f"{prefix}spec claims '{name}' but no mapped test ran ({reason})"
            )
            if is_invariant:
                errors.append(message)
            else:
                warnings.append(message)

    for key in sorted(spec.test_mapping):
        if key in claim_names:
            continue
        locator = spec.test_mapping[key]
        if _is_blank_locator(locator):
            warnings.append(
                f"Unmapped spec key '{key}': test_mapping '{key}' has blank locator"
            )
            continue
        if resolve_locator(locator, exercised_node_ids):
            warnings.append(
                f"Unmapped spec key '{key}': test_mapping entry is not a "
                "declared invariant or BDD scenario"
            )
        else:
            warnings.append(
                f"Unmapped spec key '{key}': test_mapping '{key}' -> "
                f"'{locator.strip()}' was not exercised in this session"
            )

    summary = compute_exercise_summary(spec, exercised_node_ids)
    return errors, warnings, summary


def check_mapping_coverage(
    spec: PostulateSpec,
    node_ids: set[str],
    *,
    failure_phrase: str = "does not resolve to a pytest node",
    include_missing_claims: bool = True,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    claim_names = set(enumerate_claim_names(spec))

    for name in enumerate_claim_names(spec):
        kinds = _claim_kinds(spec, name)
        locator = spec.test_mapping.get(name)
        is_invariant = "invariant" in kinds

        if include_missing_claims and (
            name not in spec.test_mapping or _is_blank_locator(locator)
        ):
            message = f"spec claims '{name}' but mapping is missing"
            if is_invariant:
                errors.append(message)
            else:
                warnings.append(message)
            continue

        if not include_missing_claims and name not in spec.test_mapping:
            continue

        if _is_blank_locator(locator):
            message = f"test_mapping '{name}' has blank locator"
            if is_invariant:
                errors.append(message)
            else:
                warnings.append(message)
            continue

        assert locator is not None
        if not resolve_locator(locator, node_ids):
            message = (
                f"test_mapping '{name}' -> '{locator.strip()}' {failure_phrase}"
            )
            if is_invariant:
                errors.append(message)
            else:
                warnings.append(message)

    for key in sorted(spec.test_mapping):
        if key in claim_names:
            continue
        locator = spec.test_mapping[key]
        if _is_blank_locator(locator):
            warnings.append(
                f"Unmapped spec key '{key}': test_mapping '{key}' has blank locator"
            )
            continue
        if resolve_locator(locator, node_ids):
            warnings.append(
                f"Unmapped spec key '{key}': test_mapping entry is not a "
                "declared invariant or BDD scenario"
            )
        else:
            warnings.append(
                f"Unmapped spec key '{key}': test_mapping '{key}' -> "
                f"'{locator.strip()}' {failure_phrase}"
            )

    return errors, warnings
