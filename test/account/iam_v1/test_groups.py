"""Tests for account IAM v1 groups API."""

import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.iam_v1.groups import (
    AccountGroupsService,
    Group,
    GroupList,
    GroupMembers,
    GroupUpdateRequest,
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


async def test_groups_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.iam_groups, AccountGroupsService)


async def test_groups_list(dt: DynatraceAsync):
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
        if (method, path) == ("GET", f"/iam/v1/accounts/{account_uuid}/groups"):
            return MockResponse(
                {
                    "count": 1,
                    "items": [
                        {
                            "uuid": "group-1",
                            "name": "Admins",
                            "description": "Admin group",
                            "federatedAttributeValues": [],
                            "owner": "LOCAL",
                            "createdAt": "2021-05-01T15:11:00Z",
                            "updatedAt": "2021-05-01T15:11:00Z",
                        }
                    ],
                }
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        groups = await dt.account.iam_groups.list(account_uuid)

    assert isinstance(groups, GroupList)
    assert groups.count == 1
    assert len(groups.items) == 1
    assert groups.items[0].name == "Admins"


async def test_groups_create(dt: DynatraceAsync):
    account_uuid = "account-123"
    group_config = [{"name": "TestGroup", "description": "Test Group"}]

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
        if (method, path) == ("POST", f"/iam/v1/accounts/{account_uuid}/groups"):
            assert json == group_config
            return MockResponse(
                [
                    {
                        "uuid": "new-group-1",
                        "name": "TestGroup",
                        "description": "Test Group",
                        "federatedAttributeValues": [],
                        "owner": "LOCAL",
                        "createdAt": "2021-05-01T15:11:00Z",
                        "updatedAt": "2021-05-01T15:11:00Z",
                    }
                ],
                201,
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        groups = await dt.account.iam_groups.create(account_uuid, group_config)

    assert len(groups) == 1
    assert isinstance(groups[0], Group)
    assert groups[0].name == "TestGroup"


async def test_groups_get_members(dt: DynatraceAsync):
    account_uuid = "account-123"
    group_uuid = "group-1"

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
        ) == ("GET", f"/iam/v1/accounts/{account_uuid}/groups/{group_uuid}/users"):
            return MockResponse(
                {
                    "count": 1,
                    "items": [
                        {
                            "uid": "user-1",
                            "email": "user@example.com",
                            "name": "John",
                            "surname": "Doe",
                            "userStatus": "ACTIVE",
                            "emergencyContact": False,
                        }
                    ],
                }
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        members = await dt.account.iam_groups.get_members(account_uuid, group_uuid)

    assert isinstance(members, GroupMembers)
    assert members.count == 1
    assert len(members.items) == 1
    assert members.items[0].email == "user@example.com"


async def test_groups_update(dt: DynatraceAsync):
    account_uuid = "account-123"
    group_uuid = "group-1"

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
        ) == ("PUT", f"/iam/v1/accounts/{account_uuid}/groups/{group_uuid}"):
            assert json == {
                "name": "Updated Group",
                "description": "Updated description",
                "federatedAttributeValues": [],
            }
            return MockResponse({}, 200)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        group_config = GroupUpdateRequest(
            name="Updated Group", description="Updated description"
        )
        response = await dt.account.iam_groups.update(
            account_uuid, group_uuid, group_config
        )

    assert response.status_code == 200


async def test_groups_delete(dt: DynatraceAsync):
    account_uuid = "account-123"
    group_uuid = "group-1"

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
        ) == ("DELETE", f"/iam/v1/accounts/{account_uuid}/groups/{group_uuid}"):
            return MockResponse({}, 200)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        response = await dt.account.iam_groups.delete(account_uuid, group_uuid)

    assert response.status_code == 200
