from __future__ import annotations

from pathlib import Path

import pytest

from postulate.check import check_spec
from postulate.diff import diff_specs
from postulate.load_spec import SpecLoadError, load_spec
from postulate.models import Contract, PostulateSpec, Scenario
from postulate.prompt import build_codegen_prompt
from postulate.verify import collect_pytest_node_ids, resolve_locator, verify_spec

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "specs"
MINIMAL_EXAMPLE = (
    Path(__file__).resolve().parent.parent / "examples" / "minimal-pytest"
)


def test_load_valid_fixture() -> None:
    spec = load_spec(FIXTURES / "valid-medium.yaml")
    assert spec.feature == "parity_base"


def test_missing_file_raises() -> None:
    with pytest.raises(SpecLoadError, match="Spec file not found"):
        load_spec(FIXTURES / "missing.yaml")


def test_invalid_yaml_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("feature: [\n", encoding="utf-8")
    with pytest.raises(SpecLoadError, match="Invalid YAML"):
        load_spec(bad)


def test_schema_error_includes_field_path(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("feature: example\n", encoding="utf-8")
    with pytest.raises(SpecLoadError, match="contract"):
        load_spec(bad)


def test_check_parity_valid_medium() -> None:
    spec = load_spec(FIXTURES / "valid-medium.yaml")
    result = check_spec(spec)
    assert result.ok


def test_check_parity_high_risk_requires_invariants() -> None:
    spec = load_spec(FIXTURES / "high-risk-no-invariants.yaml")
    result = check_spec(spec)
    assert not result.ok
    assert any("requires at least one invariant" in error for error in result.errors)


def test_check_parity_missing_invariant_mapping() -> None:
    spec = load_spec(FIXTURES / "missing-invariant-mapping.yaml")
    result = check_spec(spec)
    assert not result.ok
    assert any("deterministic_output" in error for error in result.errors)


def test_prompt_contains_required_sections() -> None:
    spec = load_spec(FIXTURES / "valid-medium.yaml")
    prompt = build_codegen_prompt(spec)
    assert "Do not invent behavior outside the spec" in prompt
    assert "Tests generated from every BDD scenario" in prompt
    assert "Property tests or assertions for every invariant" in prompt
    assert "Correctness argument" in prompt
    assert "Remaining assumptions" in prompt
    assert '"feature": "parity_base"' in prompt


def test_diff_detects_dropped_invariant() -> None:
    base = PostulateSpec(
        feature="example",
        contract=Contract(preconditions=["a"], postconditions=["b", "c"]),
        invariants=["deterministic_output", "does_not_mutate_input"],
        bdd=[Scenario(name="scenario_a", then={"ok": True})],
        policies=["no_network_calls"],
        risk="high",
    )
    after = base.model_copy(
        update={"invariants": ["deterministic_output"]},
    )
    result = diff_specs(base, after)
    assert any("does_not_mutate_input" in item for item in result.regressions)


def test_resolve_locator_supports_parametrized_prefix() -> None:
    node_ids = {"tests/test_example.py::test_values[1]"}
    assert resolve_locator("tests/test_example.py::test_values", node_ids)


def test_verify_passes_minimal_example() -> None:
    spec = load_spec(MINIMAL_EXAMPLE / "postulate.yaml")
    result = verify_spec(spec, MINIMAL_EXAMPLE)
    assert not result.errors


def test_verify_fails_missing_locator() -> None:
    spec = load_spec(MINIMAL_EXAMPLE / "postulate.yaml")
    spec.test_mapping["deterministic_output"] = "tests/test_example.py::test_missing"
    result = verify_spec(spec, MINIMAL_EXAMPLE)
    assert any("does not resolve" in error for error in result.errors)


def test_collect_pytest_node_ids_from_minimal_example() -> None:
    node_ids, _ = collect_pytest_node_ids(MINIMAL_EXAMPLE)
    assert "tests/test_example.py::test_example_case" in node_ids
