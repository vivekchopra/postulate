from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from postulate.check import CheckResult, check_spec
from postulate.models import PostulateSpec

NODE_ID_PATTERN = re.compile(r".+\.py::.+$")


@dataclass
class VerifyResult:
    check: CheckResult
    errors: list[str]
    warnings: list[str]


def _normalize_node_id(node_id: str, project_root: Path) -> str:
    normalized = node_id.replace("\\", "/")
    root = str(project_root.resolve()).replace("\\", "/")
    if normalized.startswith(root + "/"):
        normalized = normalized[len(root) + 1 :]
    if "/tests/" in normalized:
        normalized = "tests/" + normalized.split("/tests/", 1)[1]
    return normalized


def collect_pytest_node_ids(
    project_root: Path,
    pytest_args: list[str] | None = None,
) -> tuple[set[str], str]:
    project_root = project_root.resolve()
    command = [sys.executable, "-m", "pytest", "--collect-only", "-q"]
    if (project_root / "tests").is_dir():
        command.append("tests")
    if pytest_args:
        command.extend(pytest_args)

    completed = subprocess.run(
        command,
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(
            f"pytest collection failed (exit {completed.returncode}): {stderr}"
        )

    node_ids: set[str] = set()
    for line in completed.stdout.splitlines():
        candidate = line.strip()
        if NODE_ID_PATTERN.match(candidate):
            node_ids.add(_normalize_node_id(candidate, project_root))
    return node_ids, completed.stdout


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


def verify_spec(
    spec: PostulateSpec,
    project_root: Path,
    pytest_args: list[str] | None = None,
) -> VerifyResult:
    check = check_spec(spec)
    errors = list(check.errors)
    warnings = list(check.warnings)

    if not check.ok:
        return VerifyResult(check=check, errors=errors, warnings=warnings)

    node_ids, _ = collect_pytest_node_ids(project_root, pytest_args)
    invariant_names = set(spec.invariants)
    bdd_names = {scenario.name for scenario in spec.bdd}

    for key, locator in spec.test_mapping.items():
        if not resolve_locator(locator, node_ids):
            message = (
                f"test_mapping '{key}' -> '{locator}' does not resolve to a collected pytest node"
            )
            if key in invariant_names:
                errors.append(message)
            elif key in bdd_names:
                warnings.append(message)
            else:
                warnings.append(f"Unmapped spec key '{key}': {message}")

    return VerifyResult(check=check, errors=errors, warnings=warnings)


def print_verify_result(result: VerifyResult) -> None:
    for message in result.check.info:
        print(f"i {message}")
    for message in result.warnings:
        print(f"! {message}")
    for message in result.errors:
        print(f"✗ {message}")
    if not result.errors:
        print("✓ postulate verify passed")
    else:
        count = len(result.errors)
        suffix = "" if count == 1 else "s"
        print(f"✗ postulate verify failed ({count} error{suffix})")
