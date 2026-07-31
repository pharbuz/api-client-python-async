import time
from urllib.parse import parse_qs

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


async def test_oauth_client_fetches_token_as_form_urlencoded_request():
    token_requests = []

    async def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == "https://sso.example.com/sso/oauth2/token":
            token_requests.append(request)
            return httpx.Response(
                200,
                json={
                    "access_token": "token-1",
                    "token_type": "Bearer",
                    "expires_in": 300,
                    "scope": "account-uac-read account-env-read",
                    "resource": "urn:dtaccount:account-uuid",
                },
                request=request,
            )

        return httpx.Response(200, request=request)

    client = DynatraceOAuthClient(
        token_url="https://sso.example.com/sso/oauth2/token",
        client_id="client-id",
        client_secret="client-secret",
        scope="account-uac-read account-env-read",
        resource="urn:dtaccount:account-uuid",
        verify_ssl=False,
        transport=httpx.MockTransport(handler),
    )

    response = await client.request("GET", "https://api.example.com/resources")

    assert response.status_code == 200
    assert len(token_requests) == 1
    token_request = token_requests[0]
    assert token_request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert parse_qs(token_request.content.decode()) == {
        "grant_type": ["client_credentials"],
        "client_id": ["client-id"],
        "client_secret": ["client-secret"],
        "scope": ["account-uac-read account-env-read"],
        "resource": ["urn:dtaccount:account-uuid"],
    }


async def test_oauth_client_handles_dynatrace_token_response_with_expires_in():
    token_requests = []
    resource_requests = []

    async def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == "https://sso.example.com/sso/oauth2/token":
            token_requests.append(request)
            return httpx.Response(
                200,
                json={
                    "scope": "account-uac-read account-env-read",
                    "token_type": "Bearer",
                    "expires_in": 300,
                    "access_token": "dynatrace-access-token",
                    "resource": "urn:dtaccount:account-uuid",
                },
                request=request,
            )

        resource_requests.append(request)
        return httpx.Response(200, request=request)

    client = DynatraceOAuthClient(
        token_url="https://sso.example.com/sso/oauth2/token",
        client_id="client-id",
        client_secret="client-secret",
        scope="account-uac-read account-env-read",
        resource="urn:dtaccount:account-uuid",
        verify_ssl=False,
        transport=httpx.MockTransport(handler),
    )

    first_response = await client.request("GET", "https://api.example.com/resources")
    second_response = await client.request("GET", "https://api.example.com/resources")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert len(token_requests) == 1
    assert len(resource_requests) == 2
    assert (
        resource_requests[0].headers["Authorization"] == "Bearer dynatrace-access-token"
    )
    assert (
        resource_requests[1].headers["Authorization"] == "Bearer dynatrace-access-token"
    )


async def test_oauth_client_rejects_unsupported_token_type():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "access_token": "token-1",
                "token_type": "MAC",
                "expires_in": 300,
            },
            request=request,
        )

    client = DynatraceOAuthClient(
        token_url="https://sso.example.com/sso/oauth2/token",
        client_id="client-id",
        client_secret="client-secret",
        scope="account-uac-read account-env-read",
        resource="urn:dtaccount:account-uuid",
        verify_ssl=False,
        transport=httpx.MockTransport(handler),
    )

    try:
        await client.request("GET", "https://api.example.com/resources")
    except RuntimeError as err:
        assert str(err) == "OAuth token response contains unsupported token_type"
    else:
        raise AssertionError("expected unsupported token_type to raise RuntimeError")


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
