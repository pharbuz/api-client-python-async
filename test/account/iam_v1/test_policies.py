"""Tests for account IAM v1 policies API."""

import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.iam_v1.policies import (
    AccountPoliciesService,
    EffectivePermissions,
    Policy,
    PolicyBindings,
    PolicyCreateRequest,
    PolicyList,
    PolicyOverviewList,
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


async def test_policies_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.iam_policies, AccountPoliciesService)


async def test_policies_list(dt: DynatraceAsync):
    level_type = "account"
    level_id = "account-123"

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
            f"/iam/v1/repo/{level_type}/{level_id}/policies",
        ):
            return MockResponse(
                {
                    "policies": [
                        {
                            "uuid": "policy-1",
                            "name": "TestPolicy",
                            "description": "Test Policy",
                        }
                    ]
                }
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        policies = await dt.account.iam_policies.list(level_type, level_id)

    assert isinstance(policies, PolicyList)
    assert len(policies.policies) == 1


async def test_policies_create(dt: DynatraceAsync):
    level_type = "account"
    level_id = "account-123"

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
            f"/iam/v1/repo/{level_type}/{level_id}/policies",
        ):
            return MockResponse(
                {
                    "uuid": "new-policy-1",
                    "name": "NewPolicy",
                    "description": "New Policy",
                    "tags": [],
                    "statementQuery": "ALLOW action",
                    "statements": [],
                },
                201,
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        policy_config = PolicyCreateRequest(
            name="NewPolicy",
            description="New Policy",
            statement_query="ALLOW action",
        )
        policy = await dt.account.iam_policies.create(
            level_type, level_id, policy_config
        )

    assert isinstance(policy, Policy)
    assert policy.name == "NewPolicy"


async def test_policies_get(dt: DynatraceAsync):
    level_type = "account"
    level_id = "account-123"
    policy_uuid = "policy-1"

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
            f"/iam/v1/repo/{level_type}/{level_id}/policies/{policy_uuid}",
        ):
            return MockResponse(
                {
                    "uuid": policy_uuid,
                    "name": "TestPolicy",
                    "description": "Test Policy",
                    "tags": [],
                    "statementQuery": "ALLOW action",
                    "statements": [],
                }
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        policy = await dt.account.iam_policies.get(level_type, level_id, policy_uuid)

    assert isinstance(policy, Policy)
    assert policy.uuid == policy_uuid


async def test_policies_update(dt: DynatraceAsync):
    level_type = "account"
    level_id = "account-123"
    policy_uuid = "policy-1"

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
            f"/iam/v1/repo/{level_type}/{level_id}/policies/{policy_uuid}",
        ):
            return MockResponse({}, 204)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        policy_config = PolicyCreateRequest(
            name="UpdatedPolicy",
            description="Updated Policy",
            statement_query="ALLOW action",
        )
        response = await dt.account.iam_policies.update(
            level_type, level_id, policy_uuid, policy_config
        )

    assert response.status_code == 204


async def test_policies_delete(dt: DynatraceAsync):
    level_type = "account"
    level_id = "account-123"
    policy_uuid = "policy-1"

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
            f"/iam/v1/repo/{level_type}/{level_id}/policies/{policy_uuid}",
        ):
            return MockResponse({}, 204)
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        response = await dt.account.iam_policies.delete(
            level_type, level_id, policy_uuid
        )

    assert response.status_code == 204


async def test_policies_list_aggregate(dt: DynatraceAsync):
    level_type = "account"
    level_id = "account-123"

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
            f"/iam/v1/repo/{level_type}/{level_id}/policies/aggregate",
        ):
            return MockResponse(
                {
                    "policyOverviewList": [
                        {
                            "uuid": "policy-1",
                            "name": "TestPolicy",
                            "description": "Test Policy",
                            "levelId": level_id,
                            "levelType": level_type,
                        }
                    ]
                }
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        policies = await dt.account.iam_policies.list_aggregate(level_type, level_id)

    assert isinstance(policies, PolicyOverviewList)
    assert len(policies.policy_overview_list) == 1


async def test_policies_list_bindings(dt: DynatraceAsync):
    level_type = "account"
    level_id = "account-123"

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
            f"/iam/v1/repo/{level_type}/{level_id}/bindings",
        ):
            return MockResponse(
                {
                    "levelType": level_type,
                    "levelId": level_id,
                    "policyBindings": [
                        {
                            "policyUuid": "policy-1",
                            "groups": ["group-1"],
                            "parameters": {},
                            "metadata": {},
                            "boundaries": [],
                        }
                    ],
                }
            )
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        bindings = await dt.account.iam_policies.list_bindings(level_type, level_id)

    assert isinstance(bindings, PolicyBindings)
    assert len(bindings.policy_bindings) == 1


async def test_policies_get_effective_permissions(dt: DynatraceAsync):
    level_type = "account"
    level_id = "account-123"
    entity_id = "user-1"
    entity_type = "user"

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
            f"/iam/v1/resolution/{level_type}/{level_id}/effectivepermissions",
        ):
            return MockResponse({"effectivePermissions": []})
        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        permissions = await dt.account.iam_policies.get_effective_permissions(
            level_type, level_id, entity_id, entity_type
        )

    assert isinstance(permissions, EffectivePermissions)
