from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from postulate.mapping import (
    check_mapping_coverage,
    enumerate_claim_names,
    normalize_locator,
    normalize_node_id,
    resolve_locator,
)
from postulate.models import Contract, PostulateSpec, Scenario


def _minimal_spec(**updates) -> PostulateSpec:
    base = PostulateSpec(
        feature="mapping_test",
        contract=Contract(
            preconditions=["a", "b", "c"],
            postconditions=["d"],
        ),
        invariants=["deterministic_output"],
        bdd=[Scenario(name="example_scenario", then={"ok": True})],
        test_mapping={
            "deterministic_output": "tests/test_example.py::test_one",
            "example_scenario": "tests/test_example.py::test_two",
        },
    )
    return base.model_copy(update=updates)


def test_enumerate_claim_names_orders_invariants_then_bdd() -> None:
    spec = _minimal_spec(
        invariants=["z_inv", "a_inv"],
        bdd=[
            Scenario(name="a_inv", then={"ok": True}),
            Scenario(name="bdd_only", then={"ok": True}),
        ],
    )

    assert enumerate_claim_names(spec) == ["z_inv", "a_inv", "bdd_only"]


def test_p02_bdd_missing_mapping_warns() -> None:
    spec = _minimal_spec(
        invariants=["deterministic_output"],
        bdd=[Scenario(name="example_scenario", then={"ok": True})],
        test_mapping={"deterministic_output": "tests/test_example.py::test_one"},
    )
    node_ids = {"tests/test_example.py::test_one"}

    errors, warnings = check_mapping_coverage(spec, node_ids)

    assert not errors
    assert any("example_scenario" in message and "missing" in message for message in warnings)


def test_p02_bdd_blank_locator_warns() -> None:
    spec = _minimal_spec(
        test_mapping={
            "deterministic_output": "tests/test_example.py::test_one",
            "example_scenario": "   ",
        }
    )
    node_ids = {"tests/test_example.py::test_one"}

    errors, warnings = check_mapping_coverage(spec, node_ids)

    assert not errors
    assert any("example_scenario" in message for message in warnings)


def test_p02_bdd_unresolved_locator_warns() -> None:
    spec = _minimal_spec(
        test_mapping={
            "deterministic_output": "tests/test_example.py::test_one",
            "example_scenario": "tests/test_example.py::test_missing",
        }
    )
    node_ids = {"tests/test_example.py::test_one"}

    errors, warnings = check_mapping_coverage(spec, node_ids)

    assert not errors
    assert any("example_scenario" in message for message in warnings)


def test_p02_verify_skips_duplicate_missing_bdd_mapping() -> None:
    spec = _minimal_spec(
        test_mapping={"deterministic_output": "tests/test_example.py::test_one"},
    )
    node_ids = {"tests/test_example.py::test_one"}

    errors, warnings = check_mapping_coverage(
        spec,
        node_ids,
        include_missing_claims=False,
    )

    assert not errors
    assert not any("example_scenario" in message for message in warnings)


def test_p04_shared_name_missing_mapping_emits_one_invariant_error() -> None:
    spec = _minimal_spec(
        invariants=["shared_claim"],
        bdd=[Scenario(name="shared_claim", then={"ok": True})],
        test_mapping={},
    )

    errors, warnings = check_mapping_coverage(spec, set())

    assert len(errors) == 1
    assert "shared_claim" in errors[0]
    assert not warnings


def test_p05_unknown_mapping_key_warns_even_when_target_exists() -> None:
    spec = _minimal_spec(
        test_mapping={
            "deterministic_output": "tests/test_example.py::test_one",
            "example_scenario": "tests/test_example.py::test_two",
            "orphan_key": "tests/test_example.py::test_one",
        }
    )
    node_ids = {
        "tests/test_example.py::test_one",
        "tests/test_example.py::test_two",
    }

    errors, warnings = check_mapping_coverage(spec, node_ids)

    assert not errors
    assert any("orphan_key" in message for message in warnings)


def test_p06_wrong_package_paths_do_not_resolve() -> None:
    node_ids = {"packages/b/tests/test_safety.py::test_secret"}

    assert not resolve_locator(
        "packages/a/tests/test_safety.py::test_secret", node_ids
    )
    assert not resolve_locator("tests/test_safety.py::test_secret", node_ids)


def test_p06_normalize_preserves_package_prefix(tmp_path: Path) -> None:
    project_root = tmp_path
    rel = "packages/b/tests/test_safety.py::test_secret"
    node_id = f"{project_root / 'packages/b/tests/test_safety.py'}::test_secret"

    assert normalize_node_id(node_id, project_root) == rel


def test_p07_exact_parametrized_locator_matches_only_itself() -> None:
    assert resolve_locator(
        "tests/test_example.py::test_values[1]",
        {"tests/test_example.py::test_values[1]"},
    )
    assert not resolve_locator(
        "tests/test_example.py::test_values[1]",
        {"tests/test_example.py::test_values[2]"},
    )


def test_p07_base_locator_matches_one_parametrized_case() -> None:
    node_ids = {"tests/test_example.py::test_values[case-a]"}

    assert resolve_locator("tests/test_example.py::test_values", node_ids)


def test_p07_parameter_text_with_path_like_characters_is_preserved() -> None:
    param = "tests/foo[bar]"
    locator = f"tests/test_example.py::test_values[{param}]"
    normalized, error = normalize_locator(locator)

    assert error is None
    assert normalized == locator
    assert resolve_locator(locator, {locator})


def test_p07_class_node_requires_exact_match() -> None:
    node_ids = {"tests/test_example.py::TestCase::test_method"}

    assert resolve_locator("tests/test_example.py::TestCase::test_method", node_ids)
    assert not resolve_locator("tests/test_example.py::test_method", node_ids)


def test_p01_missing_invariant_mapping_errors(pytester) -> None:
    pytester.makepyfile(
        test_unrelated="""
        def test_unrelated_passes():
            assert True
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=textwrap.dedent(
            """\
            feature: p01_missing_mapping
            risk: medium
            contract:
              preconditions: [a, b, c]
              postconditions: [d]
            invariants:
              - no_secrets_in_output
            bdd:
              - name: unused_scenario
                given: {}
                when: {}
                then:
                  ok: true
            test_mapping: {}
            """
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    result.assert_outcomes(passed=1)
    assert result.ret == 1
    output = result.stdout.str().lower()
    assert "no_secrets_in_output" in output
    assert "missing" in output


def test_p02_plugin_bdd_warning_only_by_default(pytester) -> None:
    pytester.makepyfile(
        test_example="""
        def test_one():
            assert True
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=textwrap.dedent(
            """\
            feature: p02_bdd_warning
            risk: medium
            contract:
              preconditions: [a, b, c]
              postconditions: [d]
            invariants:
              - deterministic_output
            bdd:
              - name: example_scenario
                given: {}
                when: {}
                then:
                  ok: true
            test_mapping:
              deterministic_output: test_example.py::test_one
            """
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    result.assert_outcomes(passed=1)
    assert result.ret == 0
    assert "example_scenario" in result.stdout.str()


def test_p02_plugin_fail_on_warning_for_missing_bdd(pytester) -> None:
    pytester.makepyfile(
        test_example="""
        def test_one():
            assert True
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=textwrap.dedent(
            """\
            feature: p02_bdd_strict
            risk: medium
            contract:
              preconditions: [a, b, c]
              postconditions: [d]
            invariants:
              - deterministic_output
            bdd:
              - name: example_scenario
                given: {}
                when: {}
                then:
                  ok: true
            test_mapping:
              deterministic_output: test_example.py::test_one
            """
        ),
    )

    result = pytester.runpytest(
        "--postulate-spec",
        "postulate.yaml",
        "--postulate-fail-on-warning",
    )

    result.assert_outcomes(passed=1)
    assert result.ret == 1


def test_p06_plugin_shorthand_locator_does_not_match_nested_package_test(
    pytester,
) -> None:
    pytester.makepyfile(
        **{
            "packages/b/tests/test_safety": """
            def test_secret():
                assert True
            """
        }
    )
    pytester.makefile(
        ".yaml",
        postulate=textwrap.dedent(
            """\
            feature: p06_path_collision
            risk: medium
            contract:
              preconditions: [a, b, c]
              postconditions: [d]
            invariants:
              - no_secrets_in_output
            bdd:
              - name: unused_scenario
                given: {}
                when: {}
                then:
                  ok: true
            test_mapping:
              no_secrets_in_output: tests/test_safety.py::test_secret
            """
        ),
    )

    result = pytester.runpytest(
        "packages/b/tests/test_safety.py",
        "--postulate-spec",
        "postulate.yaml",
    )

    result.assert_outcomes(passed=1)
    assert result.ret == 1
    assert "no_secrets_in_output" in result.stdout.str().lower()
