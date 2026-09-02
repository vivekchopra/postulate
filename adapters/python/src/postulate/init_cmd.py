from __future__ import annotations

import re
from pathlib import Path

import yaml

from postulate.verify import collect_pytest_node_ids

NODE_ID_RE = re.compile(r"^(.+\.py)::(test_[\w]+)(?:\[.*\])?$")


class InitError(Exception):
    pass


def init_spec(
    output: Path,
    project_root: Path,
    test_paths: list[str] | None = None,
) -> Path:
    output = output.resolve()
    project_root = project_root.resolve()

    if output.exists():
        raise InitError(f"Refusing to overwrite existing file: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    feature = _feature_name_from_output(output)
    test_mapping = _suggest_test_mapping(project_root, test_paths)

    spec = {
        "feature": feature,
        "risk": "medium",
        "contract": {
            "preconditions": ["TODO: describe preconditions"],
            "postconditions": ["TODO: describe postconditions"],
            "failure_cases": [],
        },
        "invariants": [],
        "bdd": [
            {
                "name": "placeholder_scenario",
                "given": {},
                "when": {},
                "then": {"ok": True},
            }
        ],
        "policies": [],
        "test_mapping": test_mapping,
    }

    with output.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(
            spec,
            handle,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )

    return output


def _feature_name_from_output(output: Path) -> str:
    if output.stem == "postulate":
        parent = output.parent.name
        if parent and parent != ".":
            return parent
    return output.stem


def _suggest_test_mapping(
    project_root: Path,
    test_paths: list[str] | None,
) -> dict[str, str]:
    if not test_paths:
        return {}

    pytest_args = list(test_paths)
    try:
        node_ids, _ = collect_pytest_node_ids(project_root, pytest_args)
    except RuntimeError as err:
        raise InitError(str(err)) from err

    mapping: dict[str, str] = {}
    for node_id in sorted(node_ids):
        match = NODE_ID_RE.match(node_id)
        if not match:
            continue
        func_name = match.group(2)
        if not func_name.startswith("test_"):
            continue
        key = func_name.removeprefix("test_")
        mapping[key] = node_id
    return mapping
