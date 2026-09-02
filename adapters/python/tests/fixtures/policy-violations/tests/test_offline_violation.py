import requests


def test_fetch_data():
    response = requests.get("https://example.com/api")
    assert response.status_code == 200
