"""Tests for account IAM v1 platform tokens API."""

import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.iam_v1.platform_tokens import (
    AccountPlatformTokensService,
    PlatformTokenPage,
    PlatformTokenSecret,
)
from dynatrace.http_client import HttpClient


class MockResponse:
    def __init__(self, json_data=None, status_code=200):
        self._json_data = json_data
        self.headers = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = status_code

    def json(self):
        return self._json_data


async def test_platform_tokens_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.iam_platform_tokens, AccountPlatformTokensService)


async def test_platform_tokens_list(dt: DynatraceAsync):
    account_uuid = "account-123"

    async def fake_make_request(
        self,
        path,
        params=None,
        headers=None,
        method="GET",
        data=None,
        files=None,
        query_params=None,
        **kwargs,
    ):
        if (method, path) == (
            "GET",
            f"/iam/v1/accounts/{account_uuid}/platform-tokens",
        ):
            return MockResponse(
                {
                    "items": [
                        {
                            "tokenId": "token-123",
                            "name": "Test Token",
                            "status": "ACTIVE",
                            "createdBy": "user@example.com",
                            "createdAt": "2021-05-01T15:11:00Z",
                            "lastUsedAt": "2021-05-02T10:00:00Z",
                            "expirationDate": "2025-05-01T15:11:00Z",
                            "scopes": ["platform-token:tokens:manage"],
                        }
                    ],
                    "pageSize": 1,
                    "totalItems": 1,
                }
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        page = await dt.account.iam_platform_tokens.list(account_uuid)

    assert isinstance(page, PlatformTokenPage)
    assert len(page.items) == 1
    assert page.items[0].name == "Test Token"
    assert page.items[0].status == "ACTIVE"


async def test_platform_tokens_create(dt: DynatraceAsync):
    account_uuid = "account-123"
    name = "New Token"
    scopes = ["platform-token:tokens:manage"]

    async def fake_make_request(
        self,
        path,
        params=None,
        headers=None,
        method="GET",
        data=None,
        files=None,
        query_params=None,
        json=None,
        **kwargs,
    ):
        if (method, path) == (
            "POST",
            f"/iam/v1/accounts/{account_uuid}/platform-tokens",
        ):
            assert json == {"name": name, "scopes": scopes}
            return MockResponse(
                {
                    "tokenId": "token-456",
                    "secret": "secret_token_value",
                    "name": name,
                    "scopes": scopes,
                    "createdAt": "2021-05-01T15:11:00Z",
                },
                201,
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        token = await dt.account.iam_platform_tokens.create(account_uuid, name, scopes)

    assert isinstance(token, PlatformTokenSecret)
    assert token.token_id == "token-456"
    assert token.secret == "secret_token_value"


async def test_platform_tokens_delete(dt: DynatraceAsync):
    account_uuid = "account-123"
    token_id = "token-123"

    async def fake_make_request(
        self,
        path,
        params=None,
        headers=None,
        method="GET",
        data=None,
        files=None,
        query_params=None,
        **kwargs,
    ):
        if (
            method,
            path,
        ) == (
            "DELETE",
            f"/iam/v1/accounts/{account_uuid}/platform-tokens/{token_id}",
        ):
            return MockResponse({}, 200)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        response = await dt.account.iam_platform_tokens.delete(account_uuid, token_id)

    assert response.status_code == 200


async def test_platform_tokens_set_expiration_date(dt: DynatraceAsync):
    account_uuid = "account-123"
    token_id = "token-123"
    expiration_date = "2026-05-01T00:00:00Z"

    async def fake_make_request(
        self,
        path,
        params=None,
        headers=None,
        method="GET",
        data=None,
        files=None,
        query_params=None,
        json=None,
        **kwargs,
    ):
        if (
            method,
            path,
        ) == (
            "PUT",
            f"/iam/v1/accounts/{account_uuid}/platform-tokens/{token_id}/expiration-date",
        ):
            assert json == {"expirationDate": expiration_date}
            return MockResponse({}, 200)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        response = await dt.account.iam_platform_tokens.set_expiration_date(
            account_uuid, token_id, expiration_date
        )

    assert response.status_code == 200


async def test_platform_tokens_set_status(dt: DynatraceAsync):
    account_uuid = "account-123"
    token_id = "token-123"
    status = "INACTIVE"

    async def fake_make_request(
        self,
        path,
        params=None,
        headers=None,
        method="GET",
        data=None,
        files=None,
        query_params=None,
        json=None,
        **kwargs,
    ):
        if (
            method,
            path,
        ) == (
            "PUT",
            f"/iam/v1/accounts/{account_uuid}/platform-tokens/{token_id}/status",
        ):
            assert json == {"status": status}
            return MockResponse({}, 204)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        response = await dt.account.iam_platform_tokens.set_status(
            account_uuid, token_id, status
        )

    assert response.status_code == 204
