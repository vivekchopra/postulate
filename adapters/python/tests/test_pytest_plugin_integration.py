from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
SAFETY_OFFLINE = EXAMPLES / "safety-offline"
MINIMAL_PYTEST = EXAMPLES / "minimal-pytest"


def _run_pytest(
    cwd: Path,
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, "-m", "pytest", *args]
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_p15_installed_plugin_entry_point_full_session() -> None:
    result = _run_pytest(SAFETY_OFFLINE, "--postulate-spec", "postulate.yaml", "-q")

    combined = result.stdout + result.stderr
    assert result.returncode == 0, combined
    assert "invariants exercised 1/1" in combined
    assert "BDD scenarios exercised 1/1" in combined
    assert "postulate pytest plugin passed" in combined


def test_p15_installed_plugin_targeted_run_warns_on_unexercised_bdd() -> None:
    result = _run_pytest(
        SAFETY_OFFLINE,
        "--postulate-spec",
        "postulate.yaml",
        "tests/test_safety.py::test_no_secrets_in_output",
        "-q",
    )

    combined = result.stdout + result.stderr
    assert result.returncode == 0, combined
    assert "offline_request_blocked" in combined


def test_p15_installed_plugin_failed_test_preserves_pytest_exit_code(
    tmp_path: Path,
) -> None:
    project = tmp_path / "failed"
    tests = project / "tests"
    tests.mkdir(parents=True)
    (tests / "test_fail.py").write_text(
        textwrap.dedent(
            """\
            def test_no_secrets_in_output():
                assert False
            """
        ),
        encoding="utf-8",
    )
    (project / "postulate.yaml").write_text(
        textwrap.dedent(
            """\
            feature: failed_example
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
              no_secrets_in_output: tests/test_fail.py::test_no_secrets_in_output
            """
        ),
        encoding="utf-8",
    )

    result = _run_pytest(project, "--postulate-spec", "postulate.yaml", "-q")

    combined = result.stdout + result.stderr
    assert result.returncode == 1, combined
    assert "mapping execution check satisfied" in combined
    assert "invariants exercised 1/1" in combined


def test_p15_installed_plugin_demonstrates_missing_mapping_diagnostic(
    tmp_path: Path,
) -> None:
    project = tmp_path / "missing-mapping"
    tests = project / "tests"
    tests.mkdir(parents=True)
    (tests / "test_other.py").write_text(
        "def test_unrelated():\n    assert True\n",
        encoding="utf-8",
    )
    (project / "postulate.yaml").write_text(
        textwrap.dedent(
            """\
            feature: diagnostic_example
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
        encoding="utf-8",
    )

    result = _run_pytest(project, "--postulate-spec", "postulate.yaml", "-q")

    combined = result.stdout + result.stderr
    assert result.returncode == 1, combined
    assert "no_secrets_in_output" in combined
    assert "mapping is missing" in combined


def test_p15_installed_plugin_skipped_test_not_exercised(tmp_path: Path) -> None:
    project = tmp_path / "skipped"
    tests = project / "tests"
    tests.mkdir(parents=True)
    (tests / "test_skip.py").write_text(
        textwrap.dedent(
            """\
            import pytest

            @pytest.mark.skip(reason="offline maintenance")
            def test_no_secrets_in_output():
                assert True
            """
        ),
        encoding="utf-8",
    )
    (project / "postulate.yaml").write_text(
        textwrap.dedent(
            """\
            feature: skipped_example
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
              no_secrets_in_output: tests/test_skip.py::test_no_secrets_in_output
            """
        ),
        encoding="utf-8",
    )

    result = _run_pytest(project, "--postulate-spec", "postulate.yaml", "-q")

    combined = result.stdout + result.stderr
    assert result.returncode == 1, combined
    assert "skipped" in combined.lower()


def test_p15_installed_plugin_no_tests_preserves_exit_code_five(tmp_path: Path) -> None:
    project = tmp_path / "no-tests"
    project.mkdir()
    (project / "postulate.yaml").write_text(
        textwrap.dedent(
            """\
            feature: no_tests
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
              no_secrets_in_output: tests/test_missing.py::test_missing
            """
        ),
        encoding="utf-8",
    )

    result = _run_pytest(project, "--postulate-spec", "postulate.yaml", "-q")

    combined = result.stdout + result.stderr
    assert result.returncode == 5, combined
    assert "no_secrets_in_output" in combined


def test_p15_minimal_example_verify_and_plugin() -> None:
    postulate_bin = Path(sys.executable).parent / "postulate"
    verify = subprocess.run(
        [
            str(postulate_bin),
            "verify",
            "postulate.yaml",
            "--project-root",
            ".",
        ],
        cwd=MINIMAL_PYTEST,
        capture_output=True,
        text=True,
        check=False,
    )
    assert verify.returncode == 0, verify.stdout + verify.stderr

    plugin = _run_pytest(MINIMAL_PYTEST, "--postulate-spec", "postulate.yaml", "-q")
    combined = plugin.stdout + plugin.stderr
    assert plugin.returncode == 0, combined
