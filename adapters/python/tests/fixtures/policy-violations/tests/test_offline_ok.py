import respx
import httpx


@respx.mock
def test_fetch_data_offline():
    respx.get("https://example.com/api").mock(return_value=httpx.Response(200))
    response = httpx.get("https://example.com/api")
    assert response.status_code == 200
