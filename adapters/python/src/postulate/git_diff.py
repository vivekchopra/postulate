from __future__ import annotations

import os
import subprocess
from pathlib import Path

from postulate.load_spec import SpecLoadError, load_spec, load_spec_from_content
from postulate.models import PostulateSpec


class GitDiffError(Exception):
    """Raised when git-aware diff prerequisites fail."""


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def find_git_root(start: Path) -> Path:
    cwd = start if start.is_dir() else start.parent
    result = _run_git(["rev-parse", "--show-toplevel"], cwd)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "git rev-parse failed"
        raise GitDiffError(f"Not a git repository: {stderr}")
    return Path(result.stdout.strip())


def repo_relative_spec_path(spec_path: Path, git_root: Path) -> str:
    resolved = Path(os.path.realpath(spec_path))
    root = Path(os.path.realpath(git_root))
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError as err:
        raise GitDiffError(
            f"Spec file {spec_path} is outside the git repository at {git_root}"
        ) from err


def git_show_spec_at_ref(ref: str, repo_relative_path: str, cwd: Path) -> str:
    result = _run_git(["show", f"{ref}:{repo_relative_path}"], cwd)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        if (
            "bad revision" in stderr
            or "unknown revision" in stderr
            or "invalid object name" in stderr
        ):
            raise GitDiffError(f"Git ref not found: {ref}")
        if (
            "does not exist" in stderr
            or "exists on disk" in stderr
            or "pathspec" in stderr
        ):
            raise GitDiffError(
                f"Spec not found at {ref}:{repo_relative_path}"
            )
        raise GitDiffError(
            f"git show {ref}:{repo_relative_path} failed: {stderr}"
        )
    return result.stdout


def load_spec_at_git_ref(ref: str, spec_path: Path) -> PostulateSpec:
    spec_path = spec_path.resolve()
    git_root = find_git_root(spec_path.parent)
    repo_path = repo_relative_spec_path(spec_path, git_root)
    source = f"{ref}:{repo_path}"
    try:
        content = git_show_spec_at_ref(ref, repo_path, git_root)
    except GitDiffError as err:
        raise SpecLoadError(str(err)) from err
    return load_spec_from_content(content, source)


def diff_specs_against_git_ref(ref: str, spec_path: Path) -> tuple[PostulateSpec, PostulateSpec]:
    before = load_spec_at_git_ref(ref, spec_path)
    after = load_spec(spec_path)
    return before, after
