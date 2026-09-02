from __future__ import annotations

import textwrap


def test_plugin_passes_when_mappings_exercised(pytester):
    pytester.makepyfile(
        test_example="""
        def test_one():
            assert True

        def test_two():
            assert True
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=textwrap.dedent(
            """\
            feature: plugin_example
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
              - name: example_scenario
                given: {}
                when: {}
                then:
                  ok: true
            test_mapping:
              deterministic_output: test_example.py::test_one
              example_scenario: test_example.py::test_two
            """
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")
    result.assert_outcomes(passed=2)
    assert result.ret == 0
    assert "postulate pytest plugin passed" in result.stdout.str()


def test_plugin_fails_when_invariant_not_exercised(pytester):
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
            feature: plugin_example
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
              - does_not_mutate_input
            bdd:
              - name: example_scenario
                given: {}
                when: {}
                then:
                  ok: true
            test_mapping:
              deterministic_output: test_example.py::test_one
              does_not_mutate_input: test_example.py::test_missing
            """
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")
    result.assert_outcomes(passed=1)
    assert result.ret == 1
    assert "was not exercised" in result.stdout.str()
    assert "does_not_mutate_input" in result.stdout.str()


def test_plugin_bdd_warning_only_by_default(pytester):
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
            feature: plugin_example
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
              - name: example_scenario
                given: {}
                when: {}
                then:
                  ok: true
            test_mapping:
              deterministic_output: test_example.py::test_one
              example_scenario: test_example.py::test_missing_bdd
            """
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")
    result.assert_outcomes(passed=1)
    assert result.ret == 0
    assert "example_scenario" in result.stdout.str()
    assert "!" in result.stdout.str()


def test_plugin_fail_on_warning(pytester):
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
            feature: plugin_example
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
              - name: example_scenario
                given: {}
                when: {}
                then:
                  ok: true
            test_mapping:
              deterministic_output: test_example.py::test_one
              example_scenario: test_example.py::test_missing_bdd
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
