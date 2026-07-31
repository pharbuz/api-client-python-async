"""
Copyright 2021 Dynatrace LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import builtins
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import raw_optional_bool, raw_optional_int, raw_optional_str


class NetworkZoneService:
    ENDPOINT = "/api/v2/networkZones"
    ENDPOINT_GLOBALSETTINGS = "/api/v2/networkZoneSettings"
    ENDPOINT_HOST_CONNECTION_STATISTICS = "/api/v2/networkZones"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(self) -> PaginatedList["NetworkZone"]:
        """Lists all network zones. No params

        :return: a list of Network Zones with details
        """
        return await PaginatedList(
            NetworkZone,
            self.__http_client,
            target_url=self.ENDPOINT,
            list_item="networkZones",
        ).initialize()

    async def get(self, networkzone_id: str):
        """Gets parameters of specified network zone

        :param networkzone_id: the ID of the network zone
        :return: a Network Zone + details
        """
        response = (
            await self.__http_client.make_request(f"{self.ENDPOINT}/{networkzone_id}")
        ).json()
        return NetworkZone(raw_element=response)

    async def get_host_statistics(
        self, networkzone_id: str, filter: str | None = None
    ) -> "NetworkZoneConnectionStatistics":
        """Gets the statistics about hosts using the network zone."""
        params = {"filter": filter}
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{networkzone_id}/hostConnectionStatistics",
                params=params,
            )
        ).json()
        return NetworkZoneConnectionStatistics(raw_element=response)

    async def update(
        self,
        networkzone_id: str,
        alternate_zones: builtins.list[str] | None = None,
        description: str | None = None,
    ):
        """Updates an existing network zone or creates a new one

        :param networkzone_id: the ID of the network zone, if none exists, will create
        :param alternate_zones: optional list of text body of alternative network zones
        :param description: optional text body for short description of network zone
        :return: HTTP response
        """
        params = {"alternativeZones": alternate_zones, "description": description}
        return await self.__http_client.make_request(
            path=f"{self.ENDPOINT}/{networkzone_id}", params=params, method="PUT"
        )

    async def delete(self, networkzone_id: str):
        """Deletes the specified network zone

        :param networkzone_id: the ID of the network zone
        :return: HTTP response
        """
        return await self.__http_client.make_request(
            path=f"{self.ENDPOINT}/{networkzone_id}", method="DELETE"
        )

    async def get_global_config(self) -> "NetworkZoneSettings":
        """Gets the global configuration of network zones. No params
        :return: Network Zone Global Settings object
        """
        response = (
            await self.__http_client.make_request(path=self.ENDPOINT_GLOBALSETTINGS)
        ).json()
        return NetworkZoneSettings(raw_element=response)

    async def update_global_config(self, configuration: bool):
        """Updates the global configuration of network zones.

        :param configuration: boolean setting to enable/disable NZs
        :return: HTTP response
        """
        params = {"networkZonesEnabled": configuration}
        return await self.__http_client.make_request(
            path=self.ENDPOINT_GLOBALSETTINGS, method="PUT", params=params
        )

    async def getGlobalConfig(self):
        return await self.get_global_config()

    async def updateGlobalConfig(self, configuration: bool):
        return await self.update_global_config(configuration)


class NetworkZone(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.description: str | None = raw_optional_str(raw_element, "description")
        self.alternative_zones: list[str] = raw_element.get("alternativeZones", [])
        self.num_oneagents_using: int | None = raw_optional_int(
            raw_element, "numOfOneAgentsUsing"
        )
        self.num_oneagents_configured: int | None = raw_optional_int(
            raw_element, "numOfConfiguredOneAgents"
        )
        self.num_oneagents_from_other_zones: int | None = raw_optional_int(
            raw_element, "numOfOneAgentsFromOtherZones"
        )
        self.num_configured_activegates: int | None = raw_optional_int(
            raw_element, "numOfConfiguredActiveGates"
        )


class NetworkZoneSettings(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, bool]):
        self.network_zones_enabled: bool | None = raw_optional_bool(
            raw_element, "networkZonesEnabled"
        )


class NetworkZoneConnectionStatistics(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.hosts_configured_but_not_connected: list[str] = raw_element.get(
            "hostsConfiguredButNotConnected", []
        )
        self.hosts_connected_as_alternative: list[str] = raw_element.get(
            "hostsConnectedAsAlternative", []
        )
        self.hosts_connected_as_failover: list[str] = raw_element.get(
            "hostsConnectedAsFailover", []
        )
        self.hosts_connected_as_failover_without_active_gates: list[str] = (
            raw_element.get("hostsConnectedAsFailoverWithoutActiveGates", [])
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "hostsConfiguredButNotConnected": self.hosts_configured_but_not_connected,
            "hostsConnectedAsAlternative": self.hosts_connected_as_alternative,
            "hostsConnectedAsFailover": self.hosts_connected_as_failover,
            "hostsConnectedAsFailoverWithoutActiveGates": self.hosts_connected_as_failover_without_active_gates,
        }
