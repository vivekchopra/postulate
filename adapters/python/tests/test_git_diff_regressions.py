"""G0 regressions for Git diff hardening (ADR 0021 / G-05, G-06).

These tests assert intended hardened behavior. They are marked ``g0_regression``
and are expected to fail on the baseline implementation until G1 (Python) and
G2 (TypeScript) land.

Run baseline suite:

    pytest tests/ -m "not g0_regression"

Run regressions only:

    pytest tests/ -m g0_regression
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from postulate.cli import app

pytestmark = pytest.mark.g0_regression

BASE_SPEC = """\
feature: git_g0_fixture
risk: high
contract:
  preconditions:
    - input exists
    - input is valid
  postconditions:
    - output exists
invariants:
  - deterministic_output
bdd:
  - name: example_scenario
    given: {}
    when: {}
    then:
      ok: true
test_mapping:
  deterministic_output: tests/test_example.py::test_one
  example_scenario: tests/test_example.py::test_two
"""


def _init_git_repo(repo: Path, spec_text: str = BASE_SPEC) -> Path:
    spec_path = repo / "postulate.yaml"
    for args in (
        ["git", "init"],
        ["git", "config", "user.email", "test@example.com"],
        ["git", "config", "user.name", "Test User"],
    ):
        subprocess.run(args, cwd=repo, check=True, capture_output=True, text=True)
    spec_path.write_text(spec_text, encoding="utf-8")
    subprocess.run(
        ["git", "add", "postulate.yaml"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "initial spec"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return spec_path


def test_g06_python_missing_git_executable_must_exit_two_with_readable_error(
    tmp_path: Path,
) -> None:
    """G-06: missing Git executable must be exit 2 without an uncaught traceback."""
    repo = tmp_path / "repo"
    repo.mkdir()
    spec_path = _init_git_repo(repo)

    env = os.environ.copy()
    env["PATH"] = "/nonexistent"

    runner = CliRunner(env=env)
    result = runner.invoke(app, ["diff", "--git", "HEAD", str(spec_path)])

    assert result.exit_code == 2
    combined = result.output
    assert "git" in combined.lower()
    assert "FileNotFoundError" not in combined
    assert "Traceback" not in combined


def test_g05_python_missing_working_tree_file_must_exit_two(tmp_path: Path) -> None:
    """G-05: deleted working spec must exit 2 with a load diagnostic."""
    repo = tmp_path / "repo"
    repo.mkdir()
    spec_path = _init_git_repo(repo)
    spec_path.unlink()

    runner = CliRunner()
    result = runner.invoke(app, ["diff", "--git", "HEAD", str(spec_path)])

    assert result.exit_code == 2
    assert "Spec file not found" in result.output
