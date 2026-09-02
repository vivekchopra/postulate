from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from postulate.check import CheckResult, check_spec
from postulate.mapping import _normalize_node_id, check_mapping_coverage
from postulate.models import PostulateSpec

NODE_ID_PATTERN = re.compile(r".+\.py::.+$")


@dataclass
class VerifyResult:
    check: CheckResult
    errors: list[str]
    warnings: list[str]


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
    mapping_errors, mapping_warnings = check_mapping_coverage(spec, node_ids)
    errors.extend(mapping_errors)
    warnings.extend(mapping_warnings)

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
