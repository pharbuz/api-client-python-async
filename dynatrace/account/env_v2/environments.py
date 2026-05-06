"""Account environment management API v2 wrappers."""

from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class AccountEnvironmentsV2Service:
    """
    /env/v2 Environment management API

    - GET /env/v2/accounts/{accountUuid}/environments
    - GET /env/v2/accounts/{accountUuid}/clusters
    """

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    # Environment and cluster listing endpoints.
    async def list_environments(
        self, account_uuid: str
    ) -> "AccountEnvironmentsV2Response":
        resp = (
            await self.__http_client.make_request(
                f"/env/v2/accounts/{account_uuid}/environments"
            )
        ).json()
        return AccountEnvironmentsV2Response(raw_element=resp)

    async def list_clusters(self, account_uuid: str) -> "AccountClustersResponse":
        resp = (
            await self.__http_client.make_request(
                # Response models.
                f"/env/v2/accounts/{account_uuid}/clusters"
            )
        ).json()
        return AccountClustersResponse(raw_element=resp)


class AccountEnvironmentItem(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.id: str | None = raw_element.get("id")
        self.name: str | None = raw_element.get("name")
        self.active: bool | None = raw_element.get("active")
        self.url: str | None = raw_element.get("url")


class AccountEnvironmentsV2Response(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.data: list[AccountEnvironmentItem] = [
            AccountEnvironmentItem(raw_element=e) for e in raw_element.get("data", [])
        ]


class AccountClusterItem(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.cluster_id: str | None = raw_element.get("clusterId")


class AccountClustersResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.data: list[AccountClusterItem] = [
            AccountClusterItem(raw_element=e) for e in raw_element.get("data", [])
        ]
