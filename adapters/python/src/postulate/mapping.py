from __future__ import annotations

from pathlib import Path

from postulate.models import PostulateSpec


def _normalize_node_id(node_id: str, project_root: Path) -> str:
    normalized = node_id.replace("\\", "/")
    root = str(project_root.resolve()).replace("\\", "/")
    if normalized.startswith(root + "/"):
        normalized = normalized[len(root) + 1 :]
    if "/tests/" in normalized:
        normalized = "tests/" + normalized.split("/tests/", 1)[1]
    return normalized


def resolve_locator(locator: str, node_ids: set[str]) -> bool:
    normalized = locator.replace("\\", "/")
    if normalized in node_ids:
        return True

    for node_id in node_ids:
        if node_id == normalized or node_id.endswith("/" + normalized):
            return True
        if "[" not in normalized and node_id.startswith(normalized + "["):
            return True

    return False


def check_mapping_coverage(
    spec: PostulateSpec,
    node_ids: set[str],
    *,
    failure_phrase: str = "does not resolve to a pytest node",
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    invariant_names = set(spec.invariants)
    bdd_names = {scenario.name for scenario in spec.bdd}

    for key, locator in spec.test_mapping.items():
        if resolve_locator(locator, node_ids):
            continue
        message = f"test_mapping '{key}' -> '{locator}' {failure_phrase}"
        if key in invariant_names:
            errors.append(message)
        elif key in bdd_names:
            warnings.append(message)
        else:
            warnings.append(f"Unmapped spec key '{key}': {message}")

    return errors, warnings
