from __future__ import annotations

import os
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
    root = find_git_root(git_fixture_repo)
    assert root.resolve() == git_fixture_repo.resolve()


def test_find_git_root_from_nested_cwd(git_fixture_repo: Path) -> None:
    nested = git_fixture_repo / "packages" / "nested"
    nested.mkdir(parents=True)
    root = find_git_root(nested)
    assert root.resolve() == git_fixture_repo.resolve()


def test_find_git_root_not_a_repo(tmp_path: Path) -> None:
    with pytest.raises(GitDiffError, match="Not a git repository"):
        find_git_root(tmp_path)


def test_load_spec_at_git_ref(git_fixture_repo: Path) -> None:
    spec = load_spec_at_git_ref(
        "HEAD",
        git_fixture_repo / "postulate.yaml",
        cwd=git_fixture_repo,
    )
    assert "does_not_mutate_input" in spec.invariants


def test_load_spec_at_git_ref_missing_at_ref(git_fixture_repo: Path) -> None:
    new_spec = git_fixture_repo / "specs" / "new.yaml"
    new_spec.parent.mkdir()
    new_spec.write_text(BASE_SPEC, encoding="utf-8")

    with pytest.raises(SpecLoadError, match="Spec not found"):
        load_spec_at_git_ref("HEAD", new_spec, cwd=git_fixture_repo)


def test_diff_specs_against_git_ref_detects_dropped_invariant(
    git_fixture_repo: Path,
) -> None:
    before, after = diff_specs_against_git_ref(
        "HEAD",
        git_fixture_repo / "postulate.yaml",
        cwd=git_fixture_repo,
    )
    assert "does_not_mutate_input" in before.invariants
    assert "does_not_mutate_input" not in after.invariants


def test_cli_diff_git_detects_regression(
    git_fixture_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(git_fixture_repo)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD", "postulate.yaml"],
    )
    assert result.exit_code == 1
    assert "does_not_mutate_input" in result.stdout


def test_cli_diff_git_bad_ref(
    git_fixture_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(git_fixture_repo)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "not-a-real-ref", "postulate.yaml"],
    )
    assert result.exit_code == 2
    assert "Git ref not found" in result.output


def test_cli_diff_git_empty_ref(
    git_fixture_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(git_fixture_repo)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "   ", "postulate.yaml"],
    )
    assert result.exit_code == 2
    assert "Git ref must not be empty" in result.output


def test_cli_diff_git_from_nested_cwd(
    git_fixture_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    nested = git_fixture_repo / "packages" / "nested"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD", "../../postulate.yaml"],
    )
    assert result.exit_code == 1
    assert "does_not_mutate_input" in result.stdout


def test_cli_diff_git_spaces_in_filename(
    git_fixture_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(git_fixture_repo)
    spaced = git_fixture_repo / "spec files" / "my spec.yaml"
    spaced.parent.mkdir()
    spaced.write_text(BASE_SPEC, encoding="utf-8")
    _run_git(["add", "spec files/my spec.yaml"], git_fixture_repo)
    _run_git(["commit", "-m", "add spaced spec"], git_fixture_repo)
    spaced.write_text(DROPPED_INVARIANT_SPEC, encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD", "spec files/my spec.yaml"],
    )
    assert result.exit_code == 1
    assert "does_not_mutate_input" in result.stdout


def test_cli_diff_git_valid_dotted_filename(
    git_fixture_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(git_fixture_repo)
    dotted = git_fixture_repo / "..spec.yaml"
    dotted.write_text(BASE_SPEC, encoding="utf-8")
    _run_git(["add", "..spec.yaml"], git_fixture_repo)
    _run_git(["commit", "-m", "add dotted spec"], git_fixture_repo)
    dotted.write_text(DROPPED_INVARIANT_SPEC, encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD", "..spec.yaml"],
    )
    assert result.exit_code == 1
    assert "does_not_mutate_input" in result.stdout


def test_cli_diff_git_rejects_symlink_spec(
    git_fixture_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(git_fixture_repo)
    target = git_fixture_repo / "postulate.yaml"
    link = git_fixture_repo / "linked.yaml"
    if link.exists():
        link.unlink()
    os.symlink(target, link)

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD", "linked.yaml"],
    )
    assert result.exit_code == 2
    assert "symlink" in result.output.lower()


def test_cli_diff_git_rejects_spec_outside_repo(
    git_fixture_repo: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(git_fixture_repo)
    outside = tmp_path / "outside.yaml"
    outside.write_text(BASE_SPEC, encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD", str(outside)],
    )
    assert result.exit_code == 2
    assert "outside the git repository" in result.output


def test_cli_diff_git_missing_working_file(
    git_fixture_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(git_fixture_repo)
    spec_path = git_fixture_repo / "postulate.yaml"
    contents = spec_path.read_text(encoding="utf-8")
    spec_path.unlink()

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD", "postulate.yaml"],
    )
    assert result.exit_code == 2
    assert "Spec file not found" in result.output

    spec_path.write_text(contents, encoding="utf-8")


def test_cli_diff_git_missing_git_on_path(
    git_fixture_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(git_fixture_repo)
    runner = CliRunner(env={"PATH": "/nonexistent"})
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD", "postulate.yaml"],
    )
    assert result.exit_code == 2
    assert "Git executable not found" in result.output
    assert "Traceback" not in result.output


def test_cli_diff_git_head_tilde_one_on_first_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "single-commit"
    repo.mkdir()
    _run_git(["init"], repo)
    _run_git(["config", "user.email", "test@example.com"], repo)
    _run_git(["config", "user.name", "Test User"], repo)
    spec_path = repo / "postulate.yaml"
    spec_path.write_text(BASE_SPEC, encoding="utf-8")
    _run_git(["add", "postulate.yaml"], repo)
    _run_git(["commit", "-m", "only commit"], repo)
    spec_path.write_text(DROPPED_INVARIANT_SPEC, encoding="utf-8")

    monkeypatch.chdir(repo)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD~1", "postulate.yaml"],
    )
    assert result.exit_code == 2
    assert "Git ref not found" in result.output


def test_cli_diff_git_does_not_mutate_repo_state(
    git_fixture_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(git_fixture_repo)
    head_before = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=git_fixture_repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    status_before = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=git_fixture_repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    working_before = (git_fixture_repo / "postulate.yaml").read_bytes()

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD", "postulate.yaml"],
    )
    assert result.exit_code == 1
    assert "does_not_mutate_input" in result.stdout

    head_after = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=git_fixture_repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    status_after = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=git_fixture_repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    working_after = (git_fixture_repo / "postulate.yaml").read_bytes()

    assert head_before == head_after
    assert status_before == status_after
    assert working_before == working_after


def test_cli_diff_git_bad_historical_yaml(
    git_fixture_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(git_fixture_repo)
    spec_path = git_fixture_repo / "postulate.yaml"
    spec_path.write_text("feature: [\n", encoding="utf-8")
    _run_git(["add", "postulate.yaml"], git_fixture_repo)
    _run_git(["commit", "-m", "bad yaml"], git_fixture_repo)
    spec_path.write_text(DROPPED_INVARIANT_SPEC, encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["diff", "--git", "HEAD", "postulate.yaml"],
    )
    assert result.exit_code == 2
    assert "Invalid YAML" in result.output


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
