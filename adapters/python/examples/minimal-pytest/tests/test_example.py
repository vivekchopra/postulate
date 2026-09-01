def test_example_case() -> None:
    assert 1 + 1 == 2


def test_deterministic_output() -> None:
    value = 3
    assert value * 2 == 6
    assert value * 2 == 6
