from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from postulate.cli import app
from postulate.init_cmd import InitError, init_spec
from postulate.load_spec import load_spec
from postulate.policies import (
    apply_fail_on_warnings,
    check_policies,
)

POLICY_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "policy-violations"
INIT_SAMPLE = Path(__file__).resolve().parent / "fixtures" / "init-sample"
runner = CliRunner()


def test_unit_tests_stay_offline_flags_bare_requests() -> None:
    spec = load_spec(POLICY_FIXTURE / "postulate.yaml")
    result = check_policies(spec, POLICY_FIXTURE)
    assert any(
        "unit_tests_stay_offline" in warning and "test_offline_violation.py" in warning
        for warning in result.warnings
    )


def test_unit_tests_stay_offline_allows_respx() -> None:
    spec = load_spec(POLICY_FIXTURE / "postulate.yaml")
    result = check_policies(spec, POLICY_FIXTURE)
    assert not any("test_offline_ok.py" in warning for warning in result.warnings)


def test_no_secrets_in_output_flags_literal_assertions() -> None:
    spec = load_spec(POLICY_FIXTURE / "postulate.yaml")
    result = check_policies(spec, POLICY_FIXTURE)
    assert any(
        "no_secrets_in_output" in warning and "test_secrets_violation.py" in warning
        for warning in result.warnings
    )


def test_no_secrets_in_output_allows_sanitizer() -> None:
    spec = load_spec(POLICY_FIXTURE / "postulate.yaml")
    result = check_policies(spec, POLICY_FIXTURE)
    assert not any("test_secrets_ok.py" in warning for warning in result.warnings)


def test_policies_check_cli_reports_violations() -> None:
    result = runner.invoke(
        app,
        [
            "policies",
            "check",
            str(POLICY_FIXTURE / "postulate.yaml"),
            "--project-root",
            str(POLICY_FIXTURE),
        ],
    )
    assert result.exit_code == 0
    assert "unit_tests_stay_offline" in result.stdout
    assert "no_secrets_in_output" in result.stdout


def test_policies_check_fail_on_warnings() -> None:
    result = runner.invoke(
        app,
        [
            "policies",
            "check",
            str(POLICY_FIXTURE / "postulate.yaml"),
            "--project-root",
            str(POLICY_FIXTURE),
            "--fail-on-warnings",
        ],
    )
    assert result.exit_code == 1
    assert "postulate policies check failed" in result.stdout


def test_apply_fail_on_warnings_promotes_messages() -> None:
    spec = load_spec(POLICY_FIXTURE / "postulate.yaml")
    result = check_policies(spec, POLICY_FIXTURE)
    strict = apply_fail_on_warnings(result)
    assert strict.warnings
    assert len(strict.errors) == len(strict.warnings)
    assert not strict.ok


def test_policies_not_in_spec_are_not_checked(tmp_path: Path) -> None:
    spec_path = tmp_path / "postulate.yaml"
    spec_path.write_text(
        "\n".join(
            [
                "feature: no_policies",
                "contract:",
                "  preconditions: [a]",
                "  postconditions: [b]",
                "bdd:",
                "  - name: s",
                "    then: { ok: true }",
            ]
        ),
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_bad.py").write_text(
        "import requests\n\ndef test_x():\n    requests.get('http://x')\n",
        encoding="utf-8",
    )
    spec = load_spec(spec_path)
    result = check_policies(spec, tmp_path)
    assert result.warnings == []


def test_init_creates_skeleton_spec(tmp_path: Path) -> None:
    output = tmp_path / "specs" / "demo" / "postulate.yaml"
    created = init_spec(output, tmp_path)
    assert created == output
    assert output.exists()
    data = yaml.safe_load(output.read_text(encoding="utf-8"))
    assert data["feature"] == "demo"
    assert data["bdd"][0]["name"] == "placeholder_scenario"
    assert data["test_mapping"] == {}


def test_init_suggests_test_mapping_from_collection(tmp_path: Path) -> None:
    output = tmp_path / "postulate.yaml"
    init_spec(
        output,
        INIT_SAMPLE,
        ["tests/test_sample.py"],
    )
    data = yaml.safe_load(output.read_text(encoding="utf-8"))
    assert data["test_mapping"]["example_case"] == "tests/test_sample.py::test_example_case"
    assert (
        data["test_mapping"]["deterministic_output"]
        == "tests/test_sample.py::test_deterministic_output"
    )


def test_init_refuses_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "postulate.yaml"
    output.write_text("feature: existing\n", encoding="utf-8")
    with pytest.raises(InitError, match="overwrite"):
        init_spec(output, tmp_path)


def test_init_cli_creates_file(tmp_path: Path) -> None:
    output = tmp_path / "specs" / "feature" / "postulate.yaml"
    result = runner.invoke(
        app,
        ["init", "--output", str(output), "--project-root", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert output.exists()
    assert "Created" in result.stdout
