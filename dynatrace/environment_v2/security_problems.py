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

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.environment_v2.schemas import ManagementZone
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import int64_to_datetime, timestamp_to_string


class SecurityProblemService:
    ENDPOINT = "/api/v2/securityProblems"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self,
        next_page_key: str | None = None,
        page_size: int | None = None,
        security_problem_selector: str | None = None,
        sort: str | None = None,
        fields: str | None = None,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
    ) -> PaginatedList[SecurityProblem]:
        """Gets a list of security problems based on the given criteria.

        :return: a list of security problems along with their details.
        """
        params = {
            "nextPageKey": next_page_key,
            "pageSize": page_size,
            "securityProblemSelector": security_problem_selector,
            "sort": sort,
            "fields": fields,
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
        }
        return await PaginatedList(
            target_class=SecurityProblem,
            http_client=self.__http_client,
            target_url=self.ENDPOINT,
            target_params=params,
            list_item="securityProblems",
        ).initialize()

    async def get(
        self, security_problem_id: str, fields: str | None = None
    ) -> SecurityProblem:
        """Gets a security problem by specifying its id.

        :param security_problem_id: the ID of the security problem
        :return: a security problem along with its details
        """
        params = {"fields": fields}
        response = (
            await self.__http_client.make_request(
                path=f"{self.ENDPOINT}/{security_problem_id}", params=params
            )
        ).json()
        return SecurityProblem(raw_element=response)

    async def list_events(
        self,
        security_problem_id: str,
        next_page_key: str | None = None,
        page_size: int | None = None,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
    ) -> PaginatedList[SecurityProblemEvent]:
        params = {
            "nextPageKey": next_page_key,
            "pageSize": page_size,
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
        }
        return await PaginatedList(
            target_class=SecurityProblemEvent,
            http_client=self.__http_client,
            target_url=f"{self.ENDPOINT}/{security_problem_id}/events",
            target_params=params,
            list_item="events",
        ).initialize()

    async def mute(
        self, security_problem_id: str, reason: str, comment: str | None = None
    ) -> Response:
        params = {"reason": reason, "comment": comment}
        return await self.__http_client.make_request(
            path=f"{self.ENDPOINT}/{security_problem_id}/mute",
            method="POST",
            params=params,
        )

    async def unmute(
        self, security_problem_id: str, reason: str, comment: str | None = None
    ) -> Response:
        params = {"reason": reason, "comment": comment}
        return await self.__http_client.make_request(
            path=f"{self.ENDPOINT}/{security_problem_id}/unmute",
            method="POST",
            params=params,
        )

    async def bulk_mute(
        self,
        reason: str,
        security_problem_ids: list[str],
        comment: str | None = None,
    ) -> BulkMuteResponse:
        params = {
            "reason": reason,
            "comment": comment,
            "securityProblemIds": security_problem_ids,
        }
        response = (
            await self.__http_client.make_request(
                path=f"{self.ENDPOINT}/mute", method="POST", params=params
            )
        ).json()
        return BulkMuteResponse(raw_element=response)

    async def bulk_unmute(
        self,
        reason: str,
        security_problem_ids: list[str],
        comment: str | None = None,
    ) -> BulkMuteResponse:
        params = {
            "reason": reason,
            "comment": comment,
            "securityProblemIds": security_problem_ids,
        }
        response = (
            await self.__http_client.make_request(
                path=f"{self.ENDPOINT}/unmute", method="POST", params=params
            )
        ).json()
        return BulkMuteResponse(raw_element=response)

    async def list_remediation_items(
        self, security_problem_id: str, remediation_item_selector: str | None = None
    ) -> list[RemediationItem]:
        params = {"remediationItemSelector": remediation_item_selector}
        response = (
            await self.__http_client.make_request(
                path=f"{self.ENDPOINT}/{security_problem_id}/remediationItems",
                params=params,
            )
        ).json()
        return [
            RemediationItem(raw_element=item)
            for item in response.get("remediationItems", [])
        ]

    async def get_remediation_item(
        self, security_problem_id: str, remediation_item_id: str
    ) -> RemediationItem:
        response = (
            await self.__http_client.make_request(
                path=f"{self.ENDPOINT}/{security_problem_id}/remediationItems/{remediation_item_id}"
            )
        ).json()
        return RemediationItem(raw_element=response)

    async def set_remediation_item_mute_state(
        self,
        security_problem_id: str,
        remediation_item_id: str,
        muted: bool,
        reason: str,
        comment: str,
    ) -> Response:
        params = {"muted": muted, "reason": reason, "comment": comment}
        return await self.__http_client.make_request(
            path=f"{self.ENDPOINT}/{security_problem_id}/remediationItems/{remediation_item_id}/muteState",
            method="PUT",
            params=params,
        )

    async def list_remediation_progress_entities(
        self,
        security_problem_id: str,
        remediation_item_id: str,
        remediation_progress_entity_selector: str | None = None,
    ) -> list[RemediationProgressEntity]:
        params = {
            "remediationProgressEntitySelector": remediation_progress_entity_selector
        }
        response = (
            await self.__http_client.make_request(
                path=f"{self.ENDPOINT}/{security_problem_id}/remediationItems/{remediation_item_id}/remediationProgressEntities",
                params=params,
            )
        ).json()
        return [
            RemediationProgressEntity(raw_element=item)
            for item in response.get("remediationProgressEntities", [])
        ]

    async def bulk_mute_remediation_items(
        self,
        security_problem_id: str,
        reason: str,
        remediation_item_ids: list[str],
        comment: str | None = None,
    ) -> BulkMuteResponse:
        params = {
            "reason": reason,
            "comment": comment,
            "remediationItemIds": remediation_item_ids,
        }
        response = (
            await self.__http_client.make_request(
                path=f"{self.ENDPOINT}/{security_problem_id}/remediationItems/mute",
                method="POST",
                params=params,
            )
        ).json()
        return BulkMuteResponse(raw_element=response)

    async def bulk_unmute_remediation_items(
        self,
        security_problem_id: str,
        reason: str,
        remediation_item_ids: list[str],
        comment: str | None = None,
    ) -> BulkMuteResponse:
        params = {
            "reason": reason,
            "comment": comment,
            "remediationItemIds": remediation_item_ids,
        }
        response = (
            await self.__http_client.make_request(
                path=f"{self.ENDPOINT}/{security_problem_id}/remediationItems/unmute",
                method="POST",
                params=params,
            )
        ).json()
        return BulkMuteResponse(raw_element=response)

    async def update_remediation_items_tracking_links(
        self,
        security_problem_id: str,
        updates: list[dict[str, Any]] | None = None,
        deletes: list[str] | None = None,
    ) -> Response:
        params = {"updates": updates or [], "deletes": deletes or []}
        return await self.__http_client.make_request(
            path=f"{self.ENDPOINT}/{security_problem_id}/remediationItems/trackingLinks",
            method="POST",
            params=params,
        )

    async def list_vulnerable_functions(
        self,
        security_problem_id: str,
        vulnerable_functions_selector: str | None = None,
        group_by: str | None = None,
    ) -> VulnerableFunctionsContainer:
        params = {
            "vulnerableFunctionsSelector": vulnerable_functions_selector,
            "groupBy": group_by,
        }
        response = (
            await self.__http_client.make_request(
                path=f"{self.ENDPOINT}/{security_problem_id}/vulnerableFunctions",
                params=params,
            )
        ).json()
        return VulnerableFunctionsContainer(raw_element=response)


class SecurityProblem(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.security_problem_id: str | None = raw_element.get("securityProblemId")
        self.display_id: str | None = raw_element.get("displayId")
        self.title: str | None = raw_element.get("title")
        self.external_vulnerability_id: str | None = raw_element.get(
            "externalVulnerabilityId"
        )
        self.package_name: str | None = raw_element.get("packageName")
        self.url: str | None = raw_element.get("url")
        self.cve_ids: list[str] = raw_element.get("cveIds", [])
        self.muted: bool | None = raw_element.get("muted")

        self.status: SecurityProblemStatus | None = (
            SecurityProblemStatus(raw_element.get("status"))
            if raw_element.get("status")
            else None
        )
        self.technology: SecurityProblemTechnology | None = (
            SecurityProblemTechnology(raw_element.get("technology"))
            if raw_element.get("technology")
            else None
        )
        self.vulnerability_type: VulnerabilityType | None = (
            VulnerabilityType(raw_element.get("vulnerabilityType"))
            if raw_element.get("vulnerabilityType")
            else None
        )

        self.first_seen_timestamp: datetime | None = int64_to_datetime(
            raw_element.get("firstSeenTimestamp")
        )
        self.last_opened_timestamp: datetime | None = int64_to_datetime(
            raw_element.get("lastOpenedTimestamp")
        )
        self.last_updated_timestamp: datetime | None = int64_to_datetime(
            raw_element.get("lastUpdatedTimestamp")
        )
        self.last_resolved_timestamp: datetime | None = int64_to_datetime(
            raw_element.get("lastResolvedTimestamp")
        )

        self.risk_assessment: RiskAssessment | None = (
            RiskAssessment(raw_element=raw_element.get("riskAssessment"))
            if raw_element.get("riskAssessment")
            else None
        )
        self.management_zones: list[ManagementZone] = [
            ManagementZone(raw_element=mz)
            for mz in raw_element.get("managementZones", [])
        ]


class RiskAssessment(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.risk_level: SecurityProblemRiskLevel | None = (
            SecurityProblemRiskLevel(raw_element.get("riskLevel"))
            if raw_element.get("riskLevel")
            else None
        )
        self.risk_score: float | None = raw_element.get("riskScore")
        self.base_risk_level: SecurityProblemRiskLevel | None = (
            SecurityProblemRiskLevel(raw_element.get("baseRiskLevel"))
            if raw_element.get("baseRiskLevel")
            else None
        )
        self.base_risk_score: float | None = raw_element.get("baseRiskScore")
        self.exposure: str | None = raw_element.get("exposure")
        self.data_assets: str | None = raw_element.get("dataAssets")
        self.public_exploit: str | None = raw_element.get("publicExploit")
        self.vulnerable_function_usage: str | None = raw_element.get(
            "vulnerableFunctionUsage"
        )
        self.assessment_accuracy: str | None = raw_element.get("assessmentAccuracy")
        self.risk_vector: str | None = raw_element.get("riskVector")
        self.base_risk_vector: str | None = raw_element.get("baseRiskVector")


class SecurityProblemEvent(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.raw_event: dict[str, Any] = raw_element


class RemediationItem(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.remediation_item_id: str | None = raw_element.get("remediationItemId")
        self.entity_id: str | None = raw_element.get("entityId")
        self.entity_name: str | None = raw_element.get("entityName")
        self.mute_state: dict[str, Any] | None = raw_element.get("muteState")
        self.raw_remediation_item: dict[str, Any] = raw_element


class RemediationProgressEntity(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.entity_id: str | None = raw_element.get("entityId")
        self.entity_name: str | None = raw_element.get("entityName")
        self.raw_remediation_progress_entity: dict[str, Any] = raw_element


class VulnerableFunctionsContainer(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.vulnerable_functions: list[dict[str, Any]] = raw_element.get(
            "vulnerableFunctions", []
        )
        self.vulnerable_functions_by_process_group: list[dict[str, Any]] = (
            raw_element.get("vulnerableFunctionsByProcessGroup", [])
        )


class BulkMuteSummary(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.mute_state_change_triggered: bool | None = raw_element.get(
            "muteStateChangeTriggered"
        )
        self.reason: str | None = raw_element.get("reason")
        self.security_problem_id: str | None = raw_element.get("securityProblemId")
        self.remediation_item_id: str | None = raw_element.get("remediationItemId")


class BulkMuteResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.summary: list[BulkMuteSummary] = [
            BulkMuteSummary(raw_element=item) for item in raw_element.get("summary", [])
        ]


class SecurityProblemStatus(Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class VulnerabilityType(Enum):
    CODE_LEVEL = "CODE_LEVEL"
    RUNTIME = "RUNTIME"
    THIRD_PARTY = "THIRD_PARTY"


class SecurityProblemTechnology(Enum):
    DOTNET = "DOTNET"
    GO = "GO"
    JAVA = "JAVA"
    KUBERNETES = "KUBERNETES"
    NODE_JS = "NODE_JS"
    PHP = "PHP"
    PYTHON = "PYTHON"


class SecurityProblemRiskLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"
