import time

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client

from dynatrace.auth import AutoRefreshingOAuth2Client


async def test_oauth_client_fetches_token_before_first_request(monkeypatch):
    fetch_calls = []
    request_calls = []

    async def fake_fetch_token(self, url=None, **kwargs):
        fetch_calls.append((url, kwargs))
        self.token = {
            "access_token": f"token-{len(fetch_calls)}",
            "token_type": "Bearer",
            "expires_at": time.time() + 3600,
        }
        return self.token

    async def fake_request(self, method, url, auth=..., **kwargs):
        request_calls.append((method, url, auth, dict(self.token)))
        return httpx.Response(200, request=httpx.Request(method, url))

    monkeypatch.setattr(AsyncOAuth2Client, "fetch_token", fake_fetch_token)
    monkeypatch.setattr(AsyncOAuth2Client, "request", fake_request)

    client = AutoRefreshingOAuth2Client(
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
    assert fetch_calls[0][1]["resource"] == "urn:dtaccount:account-uuid"
    assert request_calls[0][3]["access_token"] == "token-1"


async def test_oauth_client_refetches_token_after_401(monkeypatch):
    fetch_calls = []
    request_calls = []

    async def fake_fetch_token(self, url=None, **kwargs):
        fetch_calls.append((url, kwargs))
        self.token = {
            "access_token": f"token-{len(fetch_calls)}",
            "token_type": "Bearer",
            "expires_at": time.time() + 3600,
        }
        return self.token

    async def fake_request(self, method, url, auth=..., **kwargs):
        request_calls.append((method, url, auth, dict(self.token)))
        status_code = 401 if len(request_calls) == 1 else 200
        return httpx.Response(status_code, request=httpx.Request(method, url))

    monkeypatch.setattr(AsyncOAuth2Client, "fetch_token", fake_fetch_token)
    monkeypatch.setattr(AsyncOAuth2Client, "request", fake_request)

    client = AutoRefreshingOAuth2Client(
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
    assert request_calls[0][3]["access_token"] == "token-1"
    assert request_calls[1][3]["access_token"] == "token-2"
