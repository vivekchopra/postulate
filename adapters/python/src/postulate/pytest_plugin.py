from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from postulate.load_spec import SpecLoadError, load_spec
from postulate.mapping import check_exercise_coverage, normalize_node_id
from postulate.models import PostulateSpec


def _xdist_active(config: pytest.Config) -> bool:
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return True
    numprocesses = getattr(config.option, "numprocesses", None)
    return numprocesses not in (None, 0, "0", "no")


def _write_line(config: pytest.Config, message: str, **kwargs) -> None:
    terminal = config.pluginmanager.get_plugin("terminalreporter")
    if terminal is not None:
        terminal.write_line(message, **kwargs)
        return
    stream = sys.stderr
    if kwargs.get("red"):
        stream.write(message + "\n")
    elif kwargs.get("yellow"):
        stream.write(message + "\n")
    elif kwargs.get("green"):
        stream.write(message + "\n")
    else:
        stream.write(message + "\n")


class PostulatePlugin:
    def __init__(self, config: pytest.Config) -> None:
        self.config = config
        self.spec: PostulateSpec = config._postulate_spec
        self.spec_path: Path = config._postulate_spec_path
        self.fail_on_warning = config.getoption("--postulate-fail-on-warning")
        self.project_root = Path(config.rootpath).resolve()
        self.exercised_node_ids: set[str] = set()
        self.node_hints: dict[str, str] = {}

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        node_id = normalize_node_id(report.nodeid, self.project_root)

        if report.when == "setup":
            if report.failed:
                self.node_hints[node_id] = "setup failed"
            elif report.skipped:
                self.node_hints[node_id] = "skipped"
            return

        if report.when != "call":
            return

        if report.skipped:
            self.node_hints[node_id] = "skipped"
            return

        if report.passed or report.failed:
            self.exercised_node_ids.add(node_id)

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        incoming_status = session.exitstatus

        errors, warnings, summary = check_exercise_coverage(
            self.spec,
            self.exercised_node_ids,
            node_hints=self.node_hints,
            spec_path=self.spec_path,
        )

        _write_line(
            self.config,
            (
                "i invariants exercised "
                f"{summary.invariants_exercised}/{summary.invariants_declared}"
            ),
        )
        _write_line(
            self.config,
            f"i BDD scenarios exercised {summary.bdd_exercised}/{summary.bdd_declared}",
        )

        for message in warnings:
            _write_line(self.config, f"! {message}", yellow=True)
        for message in errors:
            _write_line(self.config, f"✗ {message}", red=True)

        coverage_failed = bool(errors) or (self.fail_on_warning and warnings)

        if coverage_failed:
            if errors:
                count = len(errors)
                suffix = "" if count == 1 else "s"
                _write_line(
                    self.config,
                    f"✗ postulate pytest plugin failed ({count} error{suffix})",
                    red=True,
                )
            else:
                _write_line(
                    self.config,
                    "✗ postulate pytest plugin failed (warnings treated as errors)",
                    red=True,
                )
            if incoming_status == 0:
                session.exitstatus = 1
            return

        if incoming_status != 0:
            _write_line(
                self.config,
                "i mapping execution check satisfied; pytest session failed",
            )
            return

        if not warnings:
            _write_line(
                self.config,
                "✓ postulate pytest plugin passed",
                green=True,
            )


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("postulate", "Postulate spec exercise checks")
    group.addoption(
        "--postulate-spec",
        action="store",
        default=None,
        metavar="PATH",
        help="Postulate YAML spec; fail if mapped tests were not exercised",
    )
    group.addoption(
        "--postulate-fail-on-warning",
        action="store_true",
        default=False,
        help="Treat unexercised BDD test_mapping entries as failures",
    )


def pytest_configure(config: pytest.Config) -> None:
    spec_option = config.getoption("--postulate-spec")
    if not spec_option:
        return

    if config.getoption("collectonly"):
        raise pytest.UsageError(
            "--postulate-spec cannot be used with --collect-only; "
            "use 'postulate verify' for collection-only mapping checks."
        )

    if _xdist_active(config):
        raise pytest.UsageError(
            "--postulate-spec does not support parallel pytest-xdist execution; "
            "run without -n/--numprocesses or use 'postulate verify' first."
        )

    spec_path = Path(spec_option)
    if not spec_path.is_absolute():
        spec_path = Path.cwd() / spec_path
    spec_path = spec_path.resolve()

    try:
        spec = load_spec(spec_path)
    except SpecLoadError as err:
        raise pytest.UsageError(str(err)) from err

    config._postulate_spec = spec
    config._postulate_spec_path = spec_path
    config.pluginmanager.register(PostulatePlugin(config), "postulate_exercise_session")
