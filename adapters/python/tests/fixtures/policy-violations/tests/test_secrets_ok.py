from postulate.sanitize import redact


def test_output_is_redacted():
    secret = "sk-abcdefghijklmnopqrstuvwxyz123456"
    assert redact(secret) not in secret
