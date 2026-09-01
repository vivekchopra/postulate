from __future__ import annotations

import json

from postulate.models import PostulateSpec


def build_codegen_prompt(spec: PostulateSpec) -> str:
    return "\n".join(
        [
            "You are implementing code from a correctness contract.",
            "",
            "Do not invent behavior outside the spec. If the spec is ambiguous, list the ambiguity instead of guessing.",
            "",
            "Return:",
            "1. Implementation",
            "2. Tests generated from every BDD scenario",
            "3. Property tests or assertions for every invariant",
            "4. Correctness argument mapping code paths to postconditions",
            "5. Remaining assumptions",
            "",
            "SPEC:",
            json.dumps(spec.model_dump(mode="json"), indent=2),
            "",
        ]
    )
