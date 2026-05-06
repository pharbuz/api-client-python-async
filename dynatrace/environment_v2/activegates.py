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

from enum import Enum

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.environment_v2.schemas import VersionCompareType
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList


class OsType(Enum):
    LINUX = "LINUX"
    WINDOWS = "WINDOWS"


class ActivegateType(Enum):
    ENVIRONMENT = "ENVIRONMENT"
    ENVIRONMENT_MULTI = "ENVIRONMENT_MULTI"


class UpdateStatus(Enum):
    INCOMPATIBLE = "INCOMPATIBLE"
    OUTDATED = "OUTDATED"
    SUPPRESSED = "SUPPRESSED"
    UNKNOWN = "UNKNOWN"
    UP2DATE = "UP2DATE"
    UPDATE_IN_PROGRESS = "UPDATE_IN_PROGRESS"
    UPDATE_PENDING = "UPDATE_PENDING"
    UPDATE_PROBLEM = "UPDATE_PROBLEM"


class AutoUpdate(Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class Module(Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    BEACON_FORWARDER = "BEACON_FORWARDER"
    CLOUD_FOUNDRY = "CLOUD_FOUNDRY"
    DB_INSIGHT = "DB_INSIGHT"
    EXTENSIONS_V1 = "EXTENSIONS_V1"
    EXTENSIONS_V2 = "EXTENSIONS_V2"
    KUBERNETES = "KUBERNETES"
    LOGS = "LOGS"
    MEMORY_DUMPS = "MEMORY_DUMPS"
    METRIC_API = "METRIC_API"
    ONE_AGENT_ROUTING = "ONE_AGENT_ROUTING"
    OTLP_INGEST = "OTLP_INGEST"
    REST_API = "REST_API"
    SYNTHETIC = "SYNTHETIC"


class ActiveGateService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self,
        hostname: str | None = None,
        os_type: OsType | str | None = None,
        network_address: str | None = None,
        activegate_type: ActivegateType | str | None = None,
        network_zone: str | None = None,
        update_status: UpdateStatus | str | None = None,
        version_compare_type: VersionCompareType | str | None = None,
        version: str | None = None,
        auto_update: AutoUpdate | str | None = None,
        group: str | None = None,
        online: bool | None = None,
        enabled_modules: list[Module | str] | None = None,
        disabled_modules: list[Module | str] | None = None,
    ) -> PaginatedList["ActiveGate"]:
        """
        Lists all available ActiveGates
        :return: A list of ActiveGates.
        """
        params = {
            "hostname": hostname,
            "osType": os_type,
            "networkAddress": network_address,
            "ActivegateType": activegate_type,
            "networkZone": network_zone,
            "updateStatus": update_status,
            "versionCompareType": version_compare_type,
            "version": version,
            "autoUpdate": auto_update,
            "group": group,
            "online": online,
            "enabledModule": enabled_modules,
            "disabledModule": disabled_modules,
        }
        return await PaginatedList(
            ActiveGate,
            self.__http_client,
            "/api/v2/activeGates",
            params,
            list_item="activeGates",
        ).initialize()

    async def get(self, activegate_id: str) -> "ActiveGate":
        return ActiveGate(
            raw_element=(
                await self.__http_client.make_request(
                    f"/api/v2/activeGates/{activegate_id}"
                )
            ).json()
        )


class ActiveGate(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict):
        self.id: str = raw_element.get("id")
        self.network_addresses = raw_element.get("networkAddresses", [])
        self.os_type: str = raw_element.get("osType")
        self.auto_update_status: str = raw_element.get("autoUpdateStatus")
        self.offline_since: int = raw_element.get("offlineSince")
        self.version: str = raw_element.get("version")
        self.type: str = raw_element.get("type")
        self.hostname: str = raw_element.get("hostname")
        self.main_environment: str = raw_element.get("mainEnvironment")
        self.environments: str = raw_element.get("environments", [])
        self.network_zone: str = raw_element.get("networkZone")
        self.group: str = raw_element.get("group")
        self.modules: list[ActiveGateModule] = [
            ActiveGateModule(raw_element=module)
            for module in raw_element.get("modules")
        ]


class ActiveGateModule(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict):
        self.misconfigured: bool = raw_element.get("misconfigured")
        self.type: str = raw_element.get("type")
        self.attributes: bool = raw_element.get("attributes")
        self.enabled: bool = raw_element.get("enabled")
        self.version: str = raw_element.get("version")
