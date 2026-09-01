from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from postulate.models import PostulateSpec


class SpecLoadError(Exception):
    """Raised when a spec file cannot be loaded or validated."""


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

    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError as err:
        raise SpecLoadError(
            f"Invalid YAML in {spec_path}: {err}"
        ) from err

    try:
        return PostulateSpec.model_validate(parsed)
    except ValidationError as err:
        issues = "\n".join(
            f"  - {'.'.join(str(part) for part in issue['loc']) or '<root>'}: {issue['msg']}"
            for issue in err.errors()
        )
        raise SpecLoadError(
            f"Spec {spec_path} failed schema validation:\n{issues}"
        ) from err
