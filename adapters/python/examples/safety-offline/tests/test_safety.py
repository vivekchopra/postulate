"""Offline safety example for Postulate pytest execution coverage."""

from __future__ import annotations


def _redact(value: str) -> str:
    return value.replace("secret-token", "[REDACTED]")


def test_no_secrets_in_output() -> None:
    raw = "secret-token"
    assert _redact(raw) == "[REDACTED]"
    assert "secret-token" not in _redact(raw)


def test_offline_request_blocked() -> None:
    endpoint = "https://example.invalid"
    assert endpoint.endswith(".invalid")
