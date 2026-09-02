pytest_plugins = ["pytester"]

# Fixture trees under tests/fixtures/ are scanned by policy/init tests, not pytest.
collect_ignore = ["fixtures"]
