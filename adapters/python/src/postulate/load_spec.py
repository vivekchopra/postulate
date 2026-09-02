from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from postulate.models import PostulateSpec


class SpecLoadError(Exception):
    """Raised when a spec file cannot be loaded or validated."""


def _validate_parsed_spec(parsed: object, source: str) -> PostulateSpec:
    try:
        return PostulateSpec.model_validate(parsed)
    except ValidationError as err:
        issues = "\n".join(
            f"  - {'.'.join(str(part) for part in issue['loc']) or '<root>'}: {issue['msg']}"
            for issue in err.errors()
        )
        raise SpecLoadError(
            f"Spec {source} failed schema validation:\n{issues}"
        ) from err


def load_spec_from_content(content: str, source: str = "<string>") -> PostulateSpec:
    try:
        parsed = yaml.safe_load(content)
    except yaml.YAMLError as err:
        raise SpecLoadError(f"Invalid YAML in {source}: {err}") from err
    return _validate_parsed_spec(parsed, source)


def load_spec(spec_path: str | Path) -> PostulateSpec:
    path = Path(spec_path)
    abs_path = path.resolve()

    try:
        raw = abs_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SpecLoadError(f"Spec file not found: {abs_path}") from None
    except OSError as err:
        raise SpecLoadError(
            f"Could not read spec file {abs_path}: {err}"
        ) from err

    return load_spec_from_content(raw, str(spec_path))
