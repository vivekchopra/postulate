from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer

from postulate.check import check_spec, print_check_result
from postulate.diff import diff_specs, print_diff_result
from postulate.load_spec import SpecLoadError, load_spec
from postulate.prompt import build_codegen_prompt
from postulate.verify import print_verify_result, verify_spec

app = typer.Typer(
    name="postulate",
    help="Spec-anchored development for AI-generated code.",
    add_completion=False,
    no_args_is_help=True,
)


def _exit_load_error(err: SpecLoadError) -> None:
    typer.secho(str(err), fg=typer.colors.RED, err=True)
    raise typer.Exit(code=2) from err


def _safe_load(spec_path: Path):
    try:
        return load_spec(spec_path)
    except SpecLoadError as err:
        _exit_load_error(err)


@app.command("check")
def check_command(spec_file: Path) -> None:
    """Validate a Postulate YAML spec."""
    spec = _safe_load(spec_file)
    result = check_spec(spec)
    print_check_result(result)
    if not result.ok:
        raise typer.Exit(code=1)


@app.command("prompt")
def prompt_command(spec_file: Path) -> None:
    """Build an LLM codegen prompt from a spec."""
    spec = _safe_load(spec_file)
    typer.echo(build_codegen_prompt(spec))


@app.command("ci")
def ci_command(
    spec_file: Path,
    fail_on_warnings: bool = typer.Option(
        False,
        "--fail-on-warnings",
        help="Exit non-zero if any warnings are reported.",
    ),
) -> None:
    """CI-oriented check with optional strict warnings."""
    spec = _safe_load(spec_file)
    result = check_spec(spec)
    print_check_result(result)
    warn_fail = fail_on_warnings and bool(result.warnings)
    if not result.ok or warn_fail:
        raise typer.Exit(code=1)


@app.command("diff")
def diff_command(before: Path, after: Path) -> None:
    """Show regressions between two specs."""
    before_spec = _safe_load(before)
    after_spec = _safe_load(after)
    result = diff_specs(before_spec, after_spec)
    ok = print_diff_result(result)
    if not ok:
        raise typer.Exit(code=1)


@app.command("verify")
def verify_command(
    spec_file: Path,
    project_root: Path = typer.Option(
        Path("."),
        "--project-root",
        help="Project root for pytest collection.",
    ),
    fail_on_warnings: bool = typer.Option(
        False,
        "--fail-on-warnings",
        help="Exit non-zero if any warnings are reported.",
    ),
    pytest_args: Optional[str] = typer.Option(
        None,
        "--pytest-args",
        help="Extra arguments passed to pytest after --collect-only -q.",
    ),
) -> None:
    """Structural check plus pytest test_mapping resolution."""
    spec = _safe_load(spec_file)
    extra_args = pytest_args.split() if pytest_args else None
    try:
        result = verify_spec(spec, project_root.resolve(), extra_args)
    except RuntimeError as err:
        typer.secho(str(err), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from err

    print_verify_result(result)
    warn_fail = fail_on_warnings and bool(result.warnings)
    if result.errors or warn_fail:
        raise typer.Exit(code=1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
