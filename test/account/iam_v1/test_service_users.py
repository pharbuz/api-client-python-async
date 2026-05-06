"""Tests for account IAM v1 service users API."""

import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.iam_v1.service_users import (
    AccountServiceUsersService,
    ServiceUser,
    ServiceUsersPage,
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


async def test_service_users_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.iam_service_users, AccountServiceUsersService)


async def test_service_users_create(dt: DynatraceAsync):
    account_uuid = "account-123"
    name = "test-service-user"
    description = "Test Service User"

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
            f"/iam/v1/accounts/{account_uuid}/service-users",
        ):
            assert json == {"name": name, "description": description}
            return MockResponse(
                {
                    "userUuid": "service-user-123",
                    "name": name,
                    "description": description,
                    "createdAt": "2021-05-01T15:11:00Z",
                    "createdBy": "user@example.com",
                    "updatedAt": "2021-05-01T15:11:00Z",
                    "updatedBy": "user@example.com",
                    "groupUuids": [],
                },
                201,
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        service_user = await dt.account.iam_service_users.create(
            account_uuid, name, description
        )

    assert isinstance(service_user, ServiceUser)
    assert service_user.user_uuid == "service-user-123"
    assert service_user.name == name


async def test_service_users_list(dt: DynatraceAsync):
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
            f"/iam/v1/accounts/{account_uuid}/service-users",
        ):
            return MockResponse(
                {
                    "items": [
                        {
                            "userUuid": "service-user-1",
                            "name": "Test Service User",
                            "description": "Test",
                            "createdAt": "2021-05-01T15:11:00Z",
                            "createdBy": "user@example.com",
                            "updatedAt": "2021-05-01T15:11:00Z",
                            "updatedBy": "user@example.com",
                            "groupUuids": [],
                        }
                    ],
                    "pageSize": 1,
                }
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        page = await dt.account.iam_service_users.list(account_uuid)

    assert isinstance(page, ServiceUsersPage)
    assert len(page.items) == 1
    assert page.items[0].name == "Test Service User"


async def test_service_users_get(dt: DynatraceAsync):
    account_uuid = "account-123"
    user_uuid = "service-user-123"

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
            f"/iam/v1/accounts/{account_uuid}/service-users/{user_uuid}",
        ):
            return MockResponse(
                {
                    "userUuid": user_uuid,
                    "name": "Test Service User",
                    "description": "Test",
                    "createdAt": "2021-05-01T15:11:00Z",
                    "createdBy": "user@example.com",
                    "updatedAt": "2021-05-01T15:11:00Z",
                    "updatedBy": "user@example.com",
                    "groupUuids": [],
                }
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        service_user = await dt.account.iam_service_users.get(account_uuid, user_uuid)

    assert isinstance(service_user, ServiceUser)
    assert service_user.user_uuid == user_uuid


async def test_service_users_update(dt: DynatraceAsync):
    account_uuid = "account-123"
    user_uuid = "service-user-123"
    new_name = "Updated Service User"

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
            f"/iam/v1/accounts/{account_uuid}/service-users/{user_uuid}",
        ):
            assert json == {"name": new_name}
            return MockResponse({}, 200)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        response = await dt.account.iam_service_users.update(
            account_uuid, user_uuid, name=new_name
        )

    assert response.status_code == 200


async def test_service_users_delete(dt: DynatraceAsync):
    account_uuid = "account-123"
    user_uuid = "service-user-123"

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
            f"/iam/v1/accounts/{account_uuid}/service-users/{user_uuid}",
        ):
            return MockResponse({}, 200)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        response = await dt.account.iam_service_users.delete(account_uuid, user_uuid)

    assert response.status_code == 200
