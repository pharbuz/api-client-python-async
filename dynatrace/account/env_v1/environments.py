"""Account environment management API v1 wrappers."""

from typing import Any, Union

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class AccountEnvironmentsV1Service:
    """
    /env/v1 Environment management API

    - GET /env/v1/accounts/{accountUuid}/environments
    - GET /env/v1/accounts/{accountUuid}/environments/{environmentUuid}/ip-allowlist
    - PUT /env/v1/accounts/{accountUuid}/environments/{environmentUuid}/ip-allowlist
    """

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    # Environment list and IP allowlist endpoints.
    async def list(self, account_uuid: str) -> "AccountEnvironmentsWithZones":
        resp = (
            await self.__http_client.make_request(
                f"/env/v1/accounts/{account_uuid}/environments"
            )
        ).json()
        return AccountEnvironmentsWithZones(raw_element=resp)

    async def get_ip_allowlist(
        self, account_uuid: str, environment_uuid: str
    ) -> "IpAllowlistConfig":
        resp = (
            await self.__http_client.make_request(
                f"/env/v1/accounts/{account_uuid}/environments/{environment_uuid}/ip-allowlist"
            )
        ).json()
        # Include http_client for enabling .put()
        return IpAllowlistConfig(raw_element=resp, http_client=self.__http_client)

    async def set_ip_allowlist(
        self,
        account_uuid: str,
        environment_uuid: str,
        config: Union["IpAllowlistConfig", dict[str, Any]],
    ) -> Response:
        if isinstance(config, IpAllowlistConfig):
            body = config.to_json()
        else:
            body = config
        return await self.__http_client.make_request(
            f"/env/v1/accounts/{account_uuid}/environments/{environment_uuid}/ip-allowlist",
            method="PUT",
            params=body,
        )


# Response models.
class TenantResource(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.name: str | None = raw_element.get("name")
        self.id: str | None = raw_element.get("id")


class ManagementZoneResource(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.parent: str | None = raw_element.get("parent")
        self.name: str | None = raw_element.get("name")
        self.id: str | None = raw_element.get("id")


class AccountEnvironmentsWithZones(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.tenant_resources: list[TenantResource] = [
            TenantResource(raw_element=e)
            for e in raw_element.get("tenantResources", [])
        ]
        self.management_zone_resources: list[ManagementZoneResource] = [
            ManagementZoneResource(raw_element=e)
            for e in raw_element.get("managementZoneResources", [])
        ]


# Request/response payload models.
class IpAllowlistEntry(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.name: str | None = raw_element.get("name")
        self.ip_range: str | None = raw_element.get("ipRange")

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ipRange": self.ip_range,
        }


class IpAllowlistConfig(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.enabled: bool | None = raw_element.get("enabled")
        self.allow_webhook_override: bool | None = raw_element.get(
            "allowWebhookOverride"
        )
        self.allowlist: list[IpAllowlistEntry] = [
            IpAllowlistEntry(raw_element=e) for e in raw_element.get("allowlist", [])
        ]

    def to_json(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "allowWebhookOverride": self.allow_webhook_override,
            "allowlist": [e.to_json() for e in self.allowlist],
        }

    async def put(self, account_uuid: str, environment_uuid: str) -> Response:
        return await self._http_client.make_request(
            f"/env/v1/accounts/{account_uuid}/environments/{environment_uuid}/ip-allowlist",
            method="PUT",
            params=self.to_json(),
        )
