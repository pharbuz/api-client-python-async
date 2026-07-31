"""Account policy management API wrappers."""

import builtins
from typing import Any, Union

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class AccountPoliciesService:
    """
    /iam/v1 Policy management API

    - GET /iam/v1/repo/{levelType}/{levelId}/policies
    - POST /iam/v1/repo/{levelType}/{levelId}/policies
    - GET /iam/v1/repo/{levelType}/{levelId}/policies/{policyUuid}
    - PUT /iam/v1/repo/{levelType}/{levelId}/policies/{policyUuid}
    - DELETE /iam/v1/repo/{levelType}/{levelId}/policies/{policyUuid}
    - GET /iam/v1/repo/{levelType}/{levelId}/policies/aggregate
    - GET /iam/v1/repo/{levelType}/{levelId}/bindings
    - GET /iam/v1/repo/{levelType}/{levelId}/bindings/{policyUuid}
    - POST /iam/v1/repo/{levelType}/{levelId}/bindings/{policyUuid}
    - PUT /iam/v1/repo/{levelType}/{levelId}/bindings/groups/{groupUuid}
    - GET /iam/v1/resolution/{levelType}/{levelId}/effectivepermissions
    """

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def list(
        self,
        level_type: str,
        level_id: str,
        categories: list[str] | None = None,
        name: str | None = None,
    ) -> "PolicyList":
        """List all native policies of a level."""
        params: dict[str, Any] = {}
        if categories:
            params["categories"] = categories
        if name:
            params["name"] = name
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/repo/{level_type}/{level_id}/policies",
                params=params,
            )
        ).json()
        return PolicyList(raw_element=resp)

    async def create(
        self,
        level_type: str,
        level_id: str,
        policy_config: Union["PolicyCreateRequest", dict[str, Any]],
    ) -> "Policy":
        """Create a new policy."""
        if isinstance(policy_config, PolicyCreateRequest):
            body = policy_config.to_json()
        else:
            body = policy_config
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/repo/{level_type}/{level_id}/policies",
                method="POST",
                json=body,
            )
        ).json()
        return Policy(raw_element=resp)

    async def get(self, level_type: str, level_id: str, policy_uuid: str) -> "Policy":
        """Get a policy."""
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/repo/{level_type}/{level_id}/policies/{policy_uuid}"
            )
        ).json()
        return Policy(raw_element=resp)

    async def update(
        self,
        level_type: str,
        level_id: str,
        policy_uuid: str,
        policy_config: Union["PolicyCreateRequest", dict[str, Any]],
    ) -> Response:
        """Update a policy."""
        if isinstance(policy_config, PolicyCreateRequest):
            body = policy_config.to_json()
        else:
            body = policy_config
        return await self.__http_client.make_request(
            f"/iam/v1/repo/{level_type}/{level_id}/policies/{policy_uuid}",
            method="PUT",
            json=body,
        )

    async def delete(
        self, level_type: str, level_id: str, policy_uuid: str, force: bool = False
    ) -> Response:
        """Delete a policy."""
        return await self.__http_client.make_request(
            f"/iam/v1/repo/{level_type}/{level_id}/policies/{policy_uuid}",
            method="DELETE",
            params={"force": force},
        )

    async def list_aggregate(self, level_type: str, level_id: str) -> "PolicyOverviewList":
        """List all policies for a level, including inherited from higher levels."""
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/repo/{level_type}/{level_id}/policies/aggregate"
            )
        ).json()
        return PolicyOverviewList(raw_element=resp)

    async def list_bindings(self, level_type: str, level_id: str) -> "PolicyBindings":
        """List all policy bindings of a level."""
        resp = (
            await self.__http_client.make_request(f"/iam/v1/repo/{level_type}/{level_id}/bindings")
        ).json()
        return PolicyBindings(raw_element=resp)

    async def get_policy_bindings(
        self, level_type: str, level_id: str, policy_uuid: str
    ) -> "PolicyBindings":
        """Get policy bindings within a level."""
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/repo/{level_type}/{level_id}/bindings/{policy_uuid}"
            )
        ).json()
        return PolicyBindings(raw_element=resp)

    async def add_policy_bindings(
        self,
        level_type: str,
        level_id: str,
        policy_uuid: str,
        bindings_config: Union["PolicyBindingsCreateRequest", dict[str, Any]],
    ) -> Response:
        """Add policy bindings to a level."""
        if isinstance(bindings_config, PolicyBindingsCreateRequest):
            body = bindings_config.to_json()
        else:
            body = bindings_config
        return await self.__http_client.make_request(
            f"/iam/v1/repo/{level_type}/{level_id}/bindings/{policy_uuid}",
            method="POST",
            json=body,
        )

    async def get_group_policies(
        self, level_type: str, level_id: str, group_uuid: str
    ) -> "PolicyUuids":
        """List all policies for a user group."""
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/repo/{level_type}/{level_id}/bindings/groups/{group_uuid}"
            )
        ).json()
        return PolicyUuids(raw_element=resp)

    async def set_group_policies(
        self,
        level_type: str,
        level_id: str,
        group_uuid: str,
        policy_uuids: builtins.list[str],
    ) -> Response:
        """Update policy bindings for a user group (overwrites existing)."""
        body = {"policyUuids": policy_uuids}
        return await self.__http_client.make_request(
            f"/iam/v1/repo/{level_type}/{level_id}/bindings/groups/{group_uuid}",
            method="PUT",
            json=body,
        )

    async def get_effective_permissions(
        self,
        level_type: str,
        level_id: str,
        entity_id: str,
        entity_type: str,
        services: builtins.list[str] | None = None,
        page: int = 1,
        size: int = 100,
    ) -> "EffectivePermissions":
        """Get effective permissions for a user or group."""
        params = {
            "entityId": entity_id,
            "entityType": entity_type,
            "page": page,
            "size": size,
        }
        if services:
            params["services"] = services
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/resolution/{level_type}/{level_id}/effectivepermissions",
                params=params,
            )
        ).json()
        return EffectivePermissions(raw_element=resp)


# Response models
class PolicyStatement(DynatraceObject):
    """Policy statement."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.effect: str | None = raw_element.get("effect")
        self.permissions: list[str] = raw_element.get("permissions", [])
        self.conditions: list[dict[str, Any]] = raw_element.get("conditions", [])


class Policy(DynatraceObject):
    """Policy object."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.uuid: str | None = raw_element.get("uuid")
        self.name: str | None = raw_element.get("name")
        self.description: str | None = raw_element.get("description")
        self.tags: list[str] = raw_element.get("tags", [])
        self.statement_query: str | None = raw_element.get("statementQuery")
        statements_data = raw_element.get("statements", [])
        self.statements: list[PolicyStatement] = [
            PolicyStatement(raw_element=s) for s in statements_data
        ]


class PolicyList(DynatraceObject):
    """List of policies."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.policies: list[dict[str, Any]] = raw_element.get("policies", [])


class PolicyOverview(DynatraceObject):
    """Policy overview object."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.uuid: str | None = raw_element.get("uuid")
        self.name: str | None = raw_element.get("name")
        self.description: str | None = raw_element.get("description")
        self.level_id: str | None = raw_element.get("levelId")
        self.level_type: str | None = raw_element.get("levelType")


class PolicyOverviewList(DynatraceObject):
    """List of policy overviews."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.policy_overview_list: list[PolicyOverview] = [
            PolicyOverview(raw_element=e) for e in raw_element.get("policyOverviewList", [])
        ]


class PolicyBinding(DynatraceObject):
    """Policy binding object."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.policy_uuid: str | None = raw_element.get("policyUuid")
        self.groups: list[str] = raw_element.get("groups", [])
        self.parameters: dict[str, str] = raw_element.get("parameters", {})
        self.metadata: dict[str, str] = raw_element.get("metadata", {})
        self.boundaries: list[str] = raw_element.get("boundaries", [])


class PolicyBindings(DynatraceObject):
    """Policy bindings for a level."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.level_type: str | None = raw_element.get("levelType")
        self.level_id: str | None = raw_element.get("levelId")
        self.policy_bindings: list[PolicyBinding] = [
            PolicyBinding(raw_element=e) for e in raw_element.get("policyBindings", [])
        ]


class PolicyUuids(DynatraceObject):
    """List of policy UUIDs."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.policy_uuids: list[str] = raw_element.get("policyUuids", [])


class EffectivePermission(DynatraceObject):
    """Effective permission."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.permission: str | None = raw_element.get("permission")
        self.effects: list[dict[str, Any]] = raw_element.get("effects", [])


class EffectivePermissions(DynatraceObject):
    """Effective permissions for a user or group."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.effective_permissions: list[EffectivePermission] = [
            EffectivePermission(raw_element=e) for e in raw_element.get("effectivePermissions", [])
        ]


# Request models
class PolicyCreateRequest(DynatraceObject):
    """Request for creating a policy."""

    def __init__(
        self,
        name: str,
        description: str,
        statement_query: str,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.name: str | None = name
        self.description: str | None = description
        self.statement_query: str | None = statement_query
        self.tags: list[str] = tags or []

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.name = raw_element.get("name")
        self.description = raw_element.get("description")
        self.statement_query = raw_element.get("statementQuery")
        self.tags = raw_element.get("tags", [])

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "statementQuery": self.statement_query,
            "tags": self.tags,
        }


class PolicyBindingsCreateRequest(DynatraceObject):
    """Request for creating policy bindings."""

    def __init__(
        self,
        groups: list[str],
        boundaries: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.groups = groups
        self.boundaries = boundaries or []

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.groups = raw_element.get("groups", [])
        self.boundaries = raw_element.get("boundaries", [])

    def to_json(self) -> dict[str, Any]:
        return {
            "groups": self.groups,
            "boundaries": self.boundaries,
        }
