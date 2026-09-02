def test_leaks_secret_in_assertion():
    token = "sk-abcdefghijklmnopqrstuvwxyz123456"
    assert token == "sk-abcdefghijklmnopqrstuvwxyz123456"
