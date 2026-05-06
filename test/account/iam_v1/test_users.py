"""Tests for account IAM v1 users API."""

import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.iam_v1.users import (
    AccountUsersService,
    UserGroups,
    UserList,
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


async def test_users_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.iam_users, AccountUsersService)


async def test_users_list_returns_user_list(dt: DynatraceAsync):
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
        if (method, path) == ("GET", f"/iam/v1/accounts/{account_uuid}/users"):
            return MockResponse(
                {
                    "count": 2,
                    "items": [
                        {
                            "uid": "user-1",
                            "email": "user1@example.com",
                            "name": "John",
                            "surname": "Doe",
                            "userStatus": "ACTIVE",
                            "emergencyContact": False,
                        },
                        {
                            "uid": "user-2",
                            "email": "user2@example.com",
                            "name": "Jane",
                            "surname": "Smith",
                            "userStatus": "ACTIVE",
                            "emergencyContact": True,
                        },
                    ],
                }
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        users = await dt.account.iam_users.list(account_uuid)

    assert isinstance(users, UserList)
    assert users.count == 2
    assert len(users.items) == 2
    assert users.items[0].email == "user1@example.com"
    assert users.items[1].emergency_contact is True


async def test_users_create(dt: DynatraceAsync):
    account_uuid = "account-123"
    email = "newuser@example.com"

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
        if (method, path) == ("POST", f"/iam/v1/accounts/{account_uuid}/users"):
            assert json == {"email": email}
            return MockResponse({"userUuid": "new-user-uuid"}, 201)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        response = await dt.account.iam_users.create(account_uuid, email)

    assert response.user_uuid == "new-user-uuid"


async def test_users_get_groups(dt: DynatraceAsync):
    account_uuid = "account-123"
    email = "user@example.com"

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
        if (method, path) == ("GET", f"/iam/v1/accounts/{account_uuid}/users/{email}"):
            return MockResponse(
                {
                    "uid": "user-1",
                    "email": email,
                    "name": "John",
                    "surname": "Doe",
                    "userStatus": "ACTIVE",
                    "emergencyContact": False,
                    "groups": [
                        {
                            "groupName": "Group1",
                            "uuid": "group-1",
                            "owner": "LOCAL",
                            "accountUUID": account_uuid,
                            "accountName": "Test Account",
                            "description": "Test Group",
                            "createdAt": "2021-05-01T15:11:00Z",
                            "updatedAt": "2021-05-01T15:11:00Z",
                        }
                    ],
                }
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        user_groups = await dt.account.iam_users.get_groups(account_uuid, email)

    assert isinstance(user_groups, UserGroups)
    assert user_groups.email == email
    assert len(user_groups.groups) == 1
    assert user_groups.groups[0].group_name == "Group1"


async def test_users_add_to_groups(dt: DynatraceAsync):
    account_uuid = "account-123"
    email = "user@example.com"
    group_uuids = ["group-1", "group-2"]

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
        if (method, path) == ("POST", f"/iam/v1/accounts/{account_uuid}/users/{email}"):
            assert json == group_uuids
            return MockResponse({}, 201)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        response = await dt.account.iam_users.add_to_groups(
            account_uuid, email, group_uuids
        )

    assert response.status_code == 201


async def test_users_set_groups(dt: DynatraceAsync):
    account_uuid = "account-123"
    email = "user@example.com"
    group_uuids = ["group-1"]

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
        ) == ("PUT", f"/iam/v1/accounts/{account_uuid}/users/{email}/groups"):
            assert json == group_uuids
            return MockResponse({}, 200)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        response = await dt.account.iam_users.set_groups(
            account_uuid, email, group_uuids
        )

    assert response.status_code == 200


async def test_users_delete(dt: DynatraceAsync):
    account_uuid = "account-123"
    email = "user@example.com"

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
        ) == ("DELETE", f"/iam/v1/accounts/{account_uuid}/users/{email}"):
            return MockResponse({}, 200)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        response = await dt.account.iam_users.delete(account_uuid, email)

    assert response.status_code == 200
