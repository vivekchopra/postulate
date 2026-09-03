from __future__ import annotations

import os
import textwrap


def _spec_yaml(*, invariants, bdd, mapping) -> str:
    return textwrap.dedent(
        f"""\
        feature: lifecycle_example
        risk: medium
        contract:
          preconditions: [a, b, c]
          postconditions: [d]
        invariants:
{invariants}
        bdd:
{bdd}
        test_mapping:
{mapping}
        """
    )


def test_p08_setup_failure_is_not_exercised(pytester) -> None:
    pytester.makeconftest(
        """
        import pytest

        @pytest.fixture
        def boom():
            pytest.fail("setup failed")
        """
    )
    pytester.makepyfile(
        test_example="""
        def test_mapped(boom):
            assert True
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping="          deterministic_output: test_example.py::test_mapped",
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    assert result.ret == 1
    output = result.stdout.str().lower()
    assert "deterministic_output" in output
    assert "setup failed" in output


def test_p08_call_failure_still_counts_as_exercised(pytester) -> None:
    pytester.makepyfile(
        test_example="""
        def test_mapped():
            assert False
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping="          deterministic_output: test_example.py::test_mapped",
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    result.assert_outcomes(failed=1)
    assert result.ret == 1
    assert "invariants exercised 1/1" in result.stdout.str()
    assert "mapping execution check satisfied" in result.stdout.str()


def test_p08_teardown_failure_still_counts_as_exercised(pytester) -> None:
    pytester.makeconftest(
        """
        import pytest

        @pytest.fixture
        def resource():
            yield
            pytest.fail("teardown failed")
        """
    )
    pytester.makepyfile(
        test_example="""
        def test_mapped(resource):
            assert True
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping="          deterministic_output: test_example.py::test_mapped",
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    assert result.ret == 1
    assert "invariants exercised 1/1" in result.stdout.str()
    assert "mapping execution check satisfied" in result.stdout.str()


def test_p09_xfail_skip_does_not_satisfy_mapping(pytester) -> None:
    pytester.makepyfile(
        test_example="""
        import pytest

        @pytest.mark.xfail(reason="expected failure")
        def test_mapped():
            assert False
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping="          deterministic_output: test_example.py::test_mapped",
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    assert result.ret == 1
    output = result.stdout.str().lower()
    assert "deterministic_output" in output
    assert "skipped" in output or "no mapped test ran" in output


def test_p09_xpass_counts_as_exercised(pytester) -> None:
    pytester.makepyfile(
        test_example="""
        import pytest

        @pytest.mark.xfail(reason="expected failure")
        def test_mapped():
            assert True
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping="          deterministic_output: test_example.py::test_mapped",
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    result.assert_outcomes(xpassed=1)
    assert result.ret == 0
    assert "invariants exercised 1/1" in result.stdout.str()


def test_p10_partial_selection_reports_missing_execution(pytester) -> None:
    pytester.makepyfile(
        test_example="""
        def test_mapped():
            assert True

        def test_other():
            assert True
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output\n          - does_not_mutate_input",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping=(
                "          deterministic_output: test_example.py::test_mapped\n"
                "          does_not_mutate_input: test_example.py::test_other"
            ),
        ),
    )

    result = pytester.runpytest(
        "--postulate-spec",
        "postulate.yaml",
        "test_example.py::test_mapped",
    )

    result.assert_outcomes(passed=1)
    assert result.ret == 1
    assert "does_not_mutate_input" in result.stdout.str()


def test_p11_pytest_failure_status_is_preserved(pytester) -> None:
    pytester.makepyfile(
        test_example="""
        def test_mapped():
            assert False
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping="          deterministic_output: test_example.py::test_mapped",
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    result.assert_outcomes(failed=1)
    assert result.ret == 1
    assert "mapping execution check satisfied" in result.stdout.str()
    assert "postulate pytest plugin passed" not in result.stdout.str()


def test_p12_invalid_spec_is_usage_error_before_tests(pytester) -> None:
    pytester.makepyfile(test_example="def test_one(): assert True")
    pytester.makefile(".yaml", postulate="feature: [\n")

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    assert result.ret == 4
    assert "Invalid YAML" in result.stdout.str() + result.stderr.str()


def test_p12_missing_spec_is_usage_error_before_tests(pytester) -> None:
    pytester.makepyfile(test_example="def test_one(): assert True")

    result = pytester.runpytest("--postulate-spec", "missing-postulate.yaml")

    assert result.ret == 4
    assert "Spec file not found" in result.stdout.str() + result.stderr.str()


def test_p13_without_flag_has_no_postulate_output(pytester) -> None:
    pytester.makepyfile(test_example="def test_one(): assert True")

    result = pytester.runpytest()

    assert result.ret == 0
    assert "postulate pytest plugin" not in result.stdout.str()


def test_p13_missing_terminal_reporter_does_not_crash(pytester, capsys) -> None:
    pytester.makepyfile(test_example="def test_one(): assert True")
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping="          deterministic_output: test_example.py::test_one",
        ),
    )

    result = pytester.runpytest(
        "--postulate-spec",
        "postulate.yaml",
        "-p",
        "no:terminalreport",
    )

    assert result.ret == 0
    combined = result.stdout.str() + result.stderr.str()
    assert "invariants exercised 1/1" in combined


def test_p14_collect_only_with_flag_is_usage_error(pytester) -> None:
    pytester.makepyfile(test_example="def test_one(): assert True")
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping="          deterministic_output: test_example.py::test_one",
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml", "--collect-only")

    assert result.ret == 4
    assert "postulate verify" in result.stdout.str() + result.stderr.str()


def test_p14_xdist_worker_is_rejected(pytester, monkeypatch) -> None:
    pytester.makepyfile(test_example="def test_one(): assert True")
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping="          deterministic_output: test_example.py::test_one",
        ),
    )
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw0")

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    assert result.ret == 4


def test_p14_no_tests_session_preserves_exit_code_five(pytester) -> None:
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping="          deterministic_output: test_example.py::test_missing",
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    assert result.ret == 5
    assert "deterministic_output" in result.stdout.str()


def test_p03_skipped_mapped_test_is_not_exercised(pytester) -> None:
    pytester.makepyfile(
        test_example="""
        import pytest

        @pytest.mark.skip(reason="deliberate skip")
        def test_mapped_invariant():
            assert True
        """
    )
    pytester.makefile(
        ".yaml",
        postulate=_spec_yaml(
            invariants="          - deterministic_output",
            bdd="          - name: unused_scenario\n            given: {}\n            when: {}\n            then:\n              ok: true",
            mapping="          deterministic_output: test_example.py::test_mapped_invariant",
        ),
    )

    result = pytester.runpytest("--postulate-spec", "postulate.yaml")

    result.assert_outcomes(skipped=1)
    assert result.ret == 1
    output = result.stdout.str().lower()
    assert "deterministic_output" in output
    assert "skipped" in output
