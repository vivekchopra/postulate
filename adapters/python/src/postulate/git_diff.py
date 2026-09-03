from __future__ import annotations

import os
import subprocess
from pathlib import Path

from postulate.load_spec import SpecLoadError, load_spec, load_spec_from_content
from postulate.models import PostulateSpec


class GitDiffError(Exception):
    """Raised when git-aware diff prerequisites fail."""


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as err:
        raise GitDiffError("Git executable not found on PATH") from err
    except OSError as err:
        raise GitDiffError(f"Could not run git: {err}") from err


def find_git_root(cwd: Path | None = None) -> Path:
    start = (cwd or Path.cwd()).resolve()
    if not start.is_dir():
        raise GitDiffError(f"Working directory is not accessible: {start}")

    result = _run_git(["rev-parse", "--show-toplevel"], start)
    if result.returncode != 0:
        raise GitDiffError(
            "Not a git repository (git rev-parse --show-toplevel failed)"
        )
    return Path(result.stdout.strip())


def resolve_spec_path(spec_path: Path | str, cwd: Path) -> Path:
    path = Path(spec_path)
    if not path.is_absolute():
        path = cwd / path
    return path


def validate_working_spec_file(
    spec_path: Path,
    git_root: Path,
) -> tuple[Path, str]:
    if os.path.lexists(spec_path) and spec_path.is_symlink():
        raise GitDiffError(
            f"Spec file must be a regular file, not a symlink: {spec_path}"
        )

    if not spec_path.exists():
        raise SpecLoadError(f"Spec file not found: {spec_path}")

    if not spec_path.is_file():
        raise GitDiffError(f"Spec path is not a regular file: {spec_path}")

    resolved = Path(os.path.realpath(spec_path))
    root = Path(os.path.realpath(git_root))
    try:
        repo_relative = resolved.relative_to(root).as_posix()
    except ValueError as err:
        raise GitDiffError(
            f"Spec file {spec_path} is outside the git repository at {git_root}"
        ) from err

    return resolved, repo_relative


def resolve_commit(ref: str, cwd: Path) -> str:
    trimmed = ref.strip()
    if not trimmed:
        raise GitDiffError("Git ref must not be empty")

    result = _run_git(
        ["rev-parse", "--verify", "--end-of-options", f"{trimmed}^{{commit}}"],
        cwd,
    )
    if result.returncode != 0:
        raise GitDiffError(f"Git ref not found: {ref}")
    return result.stdout.strip()


def git_show_spec_at_commit(
    commit: str,
    repo_relative_path: str,
    cwd: Path,
) -> str:
    exists = _run_git(["cat-file", "-e", f"{commit}:{repo_relative_path}"], cwd)
    if exists.returncode != 0:
        raise GitDiffError(f"Spec not found at {commit}:{repo_relative_path}")

    result = _run_git(["show", f"{commit}:{repo_relative_path}"], cwd)
    if result.returncode != 0:
        raise GitDiffError(
            f"Could not read spec at {commit}:{repo_relative_path}"
        )
    return result.stdout


def repo_relative_spec_path(spec_path: Path, git_root: Path) -> str:
    _, repo_relative = validate_working_spec_file(spec_path, git_root)
    return repo_relative


def git_show_spec_at_ref(ref: str, repo_relative_path: str, cwd: Path) -> str:
    commit = resolve_commit(ref, cwd)
    return git_show_spec_at_commit(commit, repo_relative_path, cwd)


def load_spec_at_git_ref(
    ref: str,
    spec_path: Path | str,
    *,
    cwd: Path | None = None,
) -> PostulateSpec:
    invocation_cwd = (cwd or Path.cwd()).resolve()
    git_root = find_git_root(invocation_cwd)
    resolved_spec = resolve_spec_path(spec_path, invocation_cwd)
    _, repo_path = validate_working_spec_file(resolved_spec, git_root)
    commit = resolve_commit(ref, git_root)
    source = f"{commit}:{repo_path}"
    try:
        content = git_show_spec_at_commit(commit, repo_path, git_root)
    except GitDiffError as err:
        raise SpecLoadError(str(err)) from err
    return load_spec_from_content(content, source)


def diff_specs_against_git_ref(
    ref: str,
    spec_path: Path | str,
    *,
    cwd: Path | None = None,
) -> tuple[PostulateSpec, PostulateSpec]:
    invocation_cwd = (cwd or Path.cwd()).resolve()
    git_root = find_git_root(invocation_cwd)
    resolved_spec = resolve_spec_path(spec_path, invocation_cwd)
    _, repo_path = validate_working_spec_file(resolved_spec, git_root)
    commit = resolve_commit(ref, git_root)
    try:
        content = git_show_spec_at_commit(commit, repo_path, git_root)
    except GitDiffError as err:
        raise SpecLoadError(str(err)) from err
    before = load_spec_from_content(content, f"{commit}:{repo_path}")
    after = load_spec(resolved_spec)
    return before, after
