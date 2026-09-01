from typing import Final

KNOWN_INVARIANT_NAMES: Final[frozenset[str]] = frozenset(
    {
        "does_not_mutate_input",
        "deterministic_output",
        "deterministic_for_same_input",
        "pure",
        "idempotent",
        "total",
    }
)
