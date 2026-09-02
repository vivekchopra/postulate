from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from postulate.cli import app
from postulate.git_diff import (
    GitDiffError,
    diff_specs_against_git_ref,
    find_git_root,
    load_spec_at_git_ref,
)
from postulate.load_spec import SpecLoadError, load_spec

BASE_SPEC = """\
feature: git_fixture
risk: high
contract:
  preconditions:
    - input exists
    - input is valid
  postconditions:
    - output exists
invariants:
  - deterministic_output
  - does_not_mutate_input
bdd:
  - name: example_scenario
    given: {}
    when: {}
    then:
      ok: true
test_mapping:
  deterministic_output: tests/test_example.py::test_one
  does_not_mutate_input: tests/test_example.py::test_two
  example_scenario: tests/test_example.py::test_three
"""

DROPPED_INVARIANT_SPEC = """\
feature: git_fixture
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
  example_scenario: tests/test_example.py::test_three
"""


def _run_git(args: list[str], cwd: Path) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


@pytest.fixture
def git_fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(["init"], repo)
    _run_git(["config", "user.email", "test@example.com"], repo)
    _run_git(["config", "user.name", "Test User"], repo)

    spec_path = repo / "postulate.yaml"
    spec_path.write_text(BASE_SPEC, encoding="utf-8")
    _run_git(["add", "postulate.yaml"], repo)
    _run_git(["commit", "-m", "initial spec"], repo)

    spec_path.write_text(DROPPED_INVARIANT_SPEC, encoding="utf-8")
    return repo


def test_find_git_root(git_fixture_repo: Path) -> None:
    root = find_git_root(git_fixture_repo / "postulate.yaml")
    assert root.resolve() == git_fixture_repo.resolve()


def test_find_git_root_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(GitDiffError, match="Not a git repository"):
        find_git_root(tmp_path)


def test_load_spec_at_git_ref(git_fixture_repo: Path) -> None:
    spec = load_spec_at_git_ref("HEAD", git_fixture_repo / "postulate.yaml")
    assert "does_not_mutate_input" in spec.invariants


def test_load_spec_at_git_ref_missing_at_ref(git_fixture_repo: Path) -> None:
    with pytest.raises(SpecLoadError, match="Spec not found"):
        load_spec_at_git_ref("HEAD", git_fixture_repo / "missing.yaml")


def test_diff_specs_against_git_ref_detects_dropped_invariant(
    git_fixture_repo: Path,
) -> None:
    before, after = diff_specs_against_git_ref("HEAD", git_fixture_repo / "postulate.yaml")
    assert "does_not_mutate_input" in before.invariants
    assert "does_not_mutate_input" not in after.invariants


def test_cli_diff_git_detects_regression(git_fixture_repo: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD", str(git_fixture_repo / "postulate.yaml")],
    )
    assert result.exit_code == 1
    assert "does_not_mutate_input" in result.stdout


def test_cli_diff_git_bad_ref(git_fixture_repo: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "not-a-real-ref", str(git_fixture_repo / "postulate.yaml")],
    )
    assert result.exit_code == 2
    assert "Git ref not found" in result.output


def test_cli_two_file_diff_still_works(git_fixture_repo: Path, tmp_path: Path) -> None:
    before = tmp_path / "before.yaml"
    after = tmp_path / "after.yaml"
    before.write_text(BASE_SPEC, encoding="utf-8")
    after.write_text(DROPPED_INVARIANT_SPEC, encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(app, ["diff", str(before), str(after)])
    assert result.exit_code == 1
    assert "does_not_mutate_input" in result.stdout

    before_spec = load_spec(before)
    after_spec = load_spec(after)
    assert "does_not_mutate_input" in before_spec.invariants
    assert "does_not_mutate_input" not in after_spec.invariants
