from __future__ import annotations

from pathlib import Path

import pytest

from postulate.load_spec import SpecLoadError, load_spec
from postulate.mapping import _normalize_node_id, check_mapping_coverage


class PostulatePlugin:
    def __init__(self, config: pytest.Config) -> None:
        self.config = config
        self.spec_path = Path(config.getoption("--postulate-spec"))
        self.fail_on_warning = config.getoption("--postulate-fail-on-warning")
        self.project_root = Path(config.rootpath).resolve()
        self.ran_node_ids: set[str] = set()

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if report.when not in ("setup", "call"):
            return
        if report.when == "call" or report.skipped:
            self.ran_node_ids.add(
                _normalize_node_id(report.nodeid, self.project_root)
            )

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        terminal = session.config.pluginmanager.get_plugin("terminalreporter")
        try:
            spec = load_spec(self.spec_path)
        except SpecLoadError as err:
            session.exitstatus = 2
            terminal.write_line(f"✗ {err}", red=True)
            return

        errors, warnings = check_mapping_coverage(
            spec,
            self.ran_node_ids,
            failure_phrase="was not exercised in this session",
        )

        for message in warnings:
            terminal.write_line(f"! {message}", yellow=True)
        for message in errors:
            terminal.write_line(f"✗ {message}", red=True)

        if errors or (self.fail_on_warning and warnings):
            if errors:
                count = len(errors)
                suffix = "" if count == 1 else "s"
                terminal.write_line(
                    f"✗ postulate pytest plugin failed ({count} error{suffix})",
                    red=True,
                )
            else:
                terminal.write_line(
                    "✗ postulate pytest plugin failed (warnings treated as errors)",
                    red=True,
                )
            session.exitstatus = 1
        elif not warnings:
            terminal.write_line("✓ postulate pytest plugin passed", green=True)


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
    if config.getoption("--postulate-spec"):
        config.pluginmanager.register(
            PostulatePlugin(config), "postulate_exercise_session"
        )
