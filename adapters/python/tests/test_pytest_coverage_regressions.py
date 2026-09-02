"""P0 regressions for pytest execution coverage (ADR 0020 / P-01, P-03, P-06).

These tests assert intended hardened behavior. They are marked ``p0_regression``
and are expected to fail on the baseline implementation at commit ``89d0048`` until
P1 (mapping) and P2 (report classification) land.

Run baseline suite (should pass):

    pytest tests/ -m "not p0_regression"

Run regressions only (expected failures):

    pytest tests/ -m p0_regression
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from postulate.mapping import _normalize_node_id, resolve_locator

pytestmark = pytest.mark.p0_regression


def test_p01_declared_invariant_without_mapping_must_fail_plugin(pytester) -> None:
    """P-01: plugin must evaluate declared claims, not only test_mapping keys."""
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
              preconditions:
                - a
                - b
                - c
              postconditions:
                - d
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
    assert "missing mapping" in output


def test_p03_skipped_mapped_test_must_not_count_as_exercised(pytester) -> None:
    """P-03: setup/call skips must not satisfy execution coverage."""
    pytester.makepyfile(
        test_example="""
        import pytest

        @pytest.mark.skip(reason="deliberate skip for P0 regression")
        def test_mapped_invariant():
            assert True
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=textwrap.dedent(
            """\
            feature: p03_skipped_mapping
            risk: medium
            contract:
              preconditions:
                - a
                - b
                - c
              postconditions:
                - d
            invariants:
              - deterministic_output
            bdd:
              - name: unused_scenario
                given: {}
                when: {}
                then:
                  ok: true
            test_mapping:
              deterministic_output: test_example.py::test_mapped_invariant
            """
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    result.assert_outcomes(skipped=1)
    assert result.ret == 1
    output = result.stdout.str().lower()
    assert "deterministic_output" in output
    assert "skipped" in output or "not exercised" in output


def test_p06_normalize_preserves_root_relative_path(tmp_path: Path) -> None:
    """P-06: path identity must not discard directories before ``tests/``."""
    project_root = tmp_path
    rel = "packages/b/tests/test_safety.py::test_secret"
    node_id = f"{project_root / 'packages/b/tests/test_safety.py'}::test_secret"

    normalized = _normalize_node_id(node_id, project_root)

    assert normalized == rel


def test_p06_shorthand_locator_must_not_suffix_match_different_package() -> None:
    """P-06: unrelated package path must not satisfy a ``tests/`` shorthand locator."""
    node_ids = {"packages/b/tests/test_safety.py::test_secret"}

    assert not resolve_locator("tests/test_safety.py::test_secret", node_ids)


def test_p06_plugin_shorthand_locator_must_not_match_nested_package_test(
    pytester,
) -> None:
    """P-06: only ``packages/b/...`` runs; ``tests/...`` shorthand must not match."""
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
              preconditions:
                - a
                - b
                - c
              postconditions:
                - d
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
    output = result.stdout.str().lower()
    assert "no_secrets_in_output" in output
    assert "not exercised" in output or "missing mapping" in output
