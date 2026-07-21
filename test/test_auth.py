import time

import httpx

from dynatrace.auth import DynatraceOAuthClient


async def test_oauth_client_fetches_token_before_first_request(monkeypatch):
    fetch_calls = []
    request_calls = []

    async def fake_request(self, method, url, **kwargs):
        if url == "https://sso.example.com/sso/oauth2/token":
            fetch_calls.append((url, kwargs))
            token = {
                "access_token": f"token-{len(fetch_calls)}",
                "token_type": "Bearer",
                "expires_at": time.time() + 3600,
            }
            return httpx.Response(200, json=token, request=httpx.Request(method, url))

        request_calls.append((method, url, kwargs))
        return httpx.Response(200, request=httpx.Request(method, url))

    monkeypatch.setattr(httpx.AsyncClient, "request", fake_request)

    client = DynatraceOAuthClient(
        token_url="https://sso.example.com/sso/oauth2/token",
        client_id="client-id",
        client_secret="client-secret",
        scope="account-uac-read",
        resource="urn:dtaccount:account-uuid",
        verify_ssl=False,
    )

    response = await client.request("GET", "https://api.example.com/resources")

    assert response.status_code == 200
    assert len(fetch_calls) == 1
    assert fetch_calls[0][0] == "https://sso.example.com/sso/oauth2/token"
    assert fetch_calls[0][1]["data"]["resource"] == "urn:dtaccount:account-uuid"
    assert request_calls[0][2]["headers"]["Authorization"] == "Bearer token-1"


async def test_oauth_client_refetches_token_after_401(monkeypatch):
    fetch_calls = []
    request_calls = []

    async def fake_request(self, method, url, **kwargs):
        if url == "https://sso.example.com/sso/oauth2/token":
            fetch_calls.append((url, kwargs))
            token = {
                "access_token": f"token-{len(fetch_calls)}",
                "token_type": "Bearer",
                "expires_at": time.time() + 3600,
            }
            return httpx.Response(200, json=token, request=httpx.Request(method, url))

        request_calls.append((method, url, kwargs))
        status_code = 401 if len(request_calls) == 1 else 200
        return httpx.Response(status_code, request=httpx.Request(method, url))

    monkeypatch.setattr(httpx.AsyncClient, "request", fake_request)

    client = DynatraceOAuthClient(
        token_url="https://sso.example.com/sso/oauth2/token",
        client_id="client-id",
        client_secret="client-secret",
        scope="account-uac-read",
        resource="urn:dtaccount:account-uuid",
        verify_ssl=False,
    )

    response = await client.request("GET", "https://api.example.com/resources")

    assert response.status_code == 200
    assert len(fetch_calls) == 2
    assert request_calls[0][2]["headers"]["Authorization"] == "Bearer token-1"
    assert request_calls[1][2]["headers"]["Authorization"] == "Bearer token-2"


async def test_oauth_client_refetches_expired_token_before_request(monkeypatch):
    fetch_calls = []
    request_calls = []

    async def fake_request(self, method, url, **kwargs):
        if url == "https://sso.example.com/sso/oauth2/token":
            fetch_calls.append((url, kwargs))
            expires_in = -1 if len(fetch_calls) == 1 else 3600
            token = {
                "access_token": f"token-{len(fetch_calls)}",
                "token_type": "Bearer",
                "expires_in": expires_in,
            }
            return httpx.Response(200, json=token, request=httpx.Request(method, url))

        request_calls.append((method, url, kwargs))
        return httpx.Response(200, request=httpx.Request(method, url))

    monkeypatch.setattr(httpx.AsyncClient, "request", fake_request)

    client = DynatraceOAuthClient(
        token_url="https://sso.example.com/sso/oauth2/token",
        client_id="client-id",
        client_secret="client-secret",
        scope="account-uac-read",
        resource="urn:dtaccount:account-uuid",
        verify_ssl=False,
    )

    first_response = await client.request("GET", "https://api.example.com/resources")
    second_response = await client.request("GET", "https://api.example.com/resources")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert len(fetch_calls) == 2
    assert request_calls[0][2]["headers"]["Authorization"] == "Bearer token-1"
    assert request_calls[1][2]["headers"]["Authorization"] == "Bearer token-2"
