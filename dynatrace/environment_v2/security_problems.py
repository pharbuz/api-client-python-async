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

import builtins
from datetime import datetime
from enum import Enum
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.environment_v2.schemas import ManagementZone
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import (
    int64_to_datetime,
    raw_optional_bool,
    raw_optional_float,
    raw_optional_int,
    raw_optional_object,
    raw_optional_object_list,
    raw_optional_str,
    raw_optional_str_list,
    timestamp_to_string,
)


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
        security_problem_ids: builtins.list[str],
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
        security_problem_ids: builtins.list[str],
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
    ) -> builtins.list[RemediationItem]:
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
    ) -> builtins.list[RemediationProgressEntity]:
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
        remediation_item_ids: builtins.list[str],
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
        remediation_item_ids: builtins.list[str],
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
        updates: builtins.list[dict[str, Any]] | None = None,
        deletes: builtins.list[str] | None = None,
    ) -> Response:
        params: dict[str, builtins.list[dict[str, Any]] | builtins.list[str]] = {
            "updates": updates or [],
            "deletes": deletes or [],
        }
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
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.security_problem_id: str | None = raw_element.get("securityProblemId")
        self.display_id: str | None = raw_element.get("displayId")
        self.title: str | None = raw_element.get("title")
        self.description: str | None = raw_optional_str(raw_element, "description")
        self.external_vulnerability_id: str | None = raw_element.get(
            "externalVulnerabilityId"
        )
        self.package_name: str | None = raw_element.get("packageName")
        self.url: str | None = raw_element.get("url")
        self.cve_ids: list[str] = raw_element.get("cveIds", [])
        self.muted: bool | None = raw_element.get("muted")
        self.mute_state_change_in_progress: bool | None = raw_optional_bool(
            raw_element, "muteStateChangeInProgress"
        )
        self.remediation_description: str | None = raw_optional_str(
            raw_element, "remediationDescription"
        )
        self.affected_entities: list[str] = raw_optional_str_list(
            raw_element, "affectedEntities"
        )
        self.exposed_entities: list[str] = raw_optional_str_list(
            raw_element, "exposedEntities"
        )
        self.reachable_data_assets: list[str] = raw_optional_str_list(
            raw_element, "reachableDataAssets"
        )

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
        self.global_counts: Counts | None = raw_optional_object(
            raw_element, "globalCounts", lambda value: Counts(raw_element=value)
        )
        self.filtered_counts: Counts | None = raw_optional_object(
            raw_element, "filteredCounts", lambda value: Counts(raw_element=value)
        )
        self.code_level_vulnerability_details: CodeLevelVulnerabilityDetails | None = (
            raw_optional_object(
                raw_element,
                "codeLevelVulnerabilityDetails",
                lambda value: CodeLevelVulnerabilityDetails(raw_element=value),
            )
        )
        self.events: list[SecurityProblemEvent] | None = raw_optional_object_list(
            raw_element,
            "events",
            lambda value: SecurityProblemEvent(raw_element=value),
        )
        self.related_attacks: RelatedAttacksList | None = raw_optional_object(
            raw_element,
            "relatedAttacks",
            lambda value: RelatedAttacksList(raw_element=value),
        )
        self.related_container_images: RelatedContainerList | None = (
            raw_optional_object(
                raw_element,
                "relatedContainerImages",
                lambda value: RelatedContainerList(raw_element=value),
            )
        )
        self.related_entities: RelatedEntitiesList | None = raw_optional_object(
            raw_element,
            "relatedEntities",
            lambda value: RelatedEntitiesList(raw_element=value),
        )
        self.vulnerable_components: list[VulnerableComponent] | None = (
            raw_optional_object_list(
                raw_element,
                "vulnerableComponents",
                lambda value: VulnerableComponent(raw_element=value),
            )
        )
        self.entry_points: dict[str, Any] | None = raw_element.get("entryPoints")


class RiskAssessment(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
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
        self.vulnerable_function_restart_required: bool | None = raw_optional_bool(
            raw_element, "vulnerableFunctionRestartRequired"
        )
        self.assessment_accuracy: str | None = raw_element.get("assessmentAccuracy")
        self.assessment_accuracy_details: AssessmentAccuracyDetails | None = (
            raw_optional_object(
                raw_element,
                "assessmentAccuracyDetails",
                lambda value: AssessmentAccuracyDetails(raw_element=value),
            )
        )
        self.risk_vector: str | None = raw_element.get("riskVector")
        self.base_risk_vector: str | None = raw_element.get("baseRiskVector")


class AssessmentAccuracyDetails(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.reduced_reasons: list[str] = raw_optional_str_list(
            raw_element, "reducedReasons"
        )


class Counts(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.affected_nodes: int | None = raw_optional_int(raw_element, "affectedNodes")
        self.affected_process_group_instances: int | None = raw_optional_int(
            raw_element, "affectedProcessGroupInstances"
        )
        self.affected_process_groups: int | None = raw_optional_int(
            raw_element, "affectedProcessGroups"
        )
        self.exposed_process_groups: int | None = raw_optional_int(
            raw_element, "exposedProcessGroups"
        )
        self.reachable_data_assets: int | None = raw_optional_int(
            raw_element, "reachableDataAssets"
        )
        self.related_applications: int | None = raw_optional_int(
            raw_element, "relatedApplications"
        )
        self.related_attacks: int | None = raw_optional_int(
            raw_element, "relatedAttacks"
        )
        self.related_databases: int | None = raw_optional_int(
            raw_element, "relatedDatabases"
        )
        self.related_hosts: int | None = raw_optional_int(raw_element, "relatedHosts")
        self.related_kubernetes_clusters: int | None = raw_optional_int(
            raw_element, "relatedKubernetesClusters"
        )
        self.related_kubernetes_workloads: int | None = raw_optional_int(
            raw_element, "relatedKubernetesWorkloads"
        )
        self.related_services: int | None = raw_optional_int(
            raw_element, "relatedServices"
        )
        self.vulnerable_components: int | None = raw_optional_int(
            raw_element, "vulnerableComponents"
        )


class CodeLevelVulnerabilityDetails(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.process_group_ids: list[str] = raw_optional_str_list(
            raw_element, "processGroupIds"
        )
        self.process_groups: list[str] = raw_optional_str_list(
            raw_element, "processGroups"
        )
        self.short_vulnerability_location: str | None = raw_optional_str(
            raw_element, "shortVulnerabilityLocation"
        )
        self.type: CodeLevelVulnerabilityType | None = (
            CodeLevelVulnerabilityType(raw_element.get("type"))
            if raw_element.get("type")
            else None
        )
        self.vulnerability_location: str | None = raw_optional_str(
            raw_element, "vulnerabilityLocation"
        )
        self.vulnerable_function: str | None = raw_optional_str(
            raw_element, "vulnerableFunction"
        )
        self.vulnerable_function_input: VulnerableFunctionInput | None = (
            raw_optional_object(
                raw_element,
                "vulnerableFunctionInput",
                lambda value: VulnerableFunctionInput(raw_element=value),
            )
        )


class SecurityProblemEvent(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.timestamp: datetime | None = int64_to_datetime(
            raw_element.get("timestamp")
        )
        self.reason: SecurityProblemEventReason | None = (
            SecurityProblemEventReason(raw_element.get("reason"))
            if raw_element.get("reason")
            else None
        )
        self.mute_state: MuteState | None = raw_optional_object(
            raw_element, "muteState", lambda value: MuteState(raw_element=value)
        )
        self.risk_assessment_snapshot: RiskAssessmentSnapshot | None = (
            raw_optional_object(
                raw_element,
                "riskAssessmentSnapshot",
                lambda value: RiskAssessmentSnapshot(raw_element=value),
            )
        )


class MuteState(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.comment: str | None = raw_optional_str(raw_element, "comment")
        self.reason: MuteReason | None = (
            MuteReason(raw_element.get("reason")) if raw_element.get("reason") else None
        )
        self.user: str | None = raw_optional_str(raw_element, "user")


class RiskAssessmentChanges(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.delta_base_risk_score: float | None = raw_optional_float(
            raw_element, "deltaBaseRiskScore"
        )
        self.delta_number_of_affected_nodes: int | None = raw_optional_int(
            raw_element, "deltaNumberOfAffectedNodes"
        )
        self.delta_number_of_affected_process_groups: int | None = raw_optional_int(
            raw_element, "deltaNumberOfAffectedProcessGroups"
        )
        self.delta_number_of_reachable_data_assets: int | None = raw_optional_int(
            raw_element, "deltaNumberOfReachableDataAssets"
        )
        self.delta_number_of_related_attacks: int | None = raw_optional_int(
            raw_element, "deltaNumberOfRelatedAttacks"
        )
        self.delta_risk_score: float | None = raw_optional_float(
            raw_element, "deltaRiskScore"
        )
        self.previous_exposure: str | None = raw_optional_str(
            raw_element, "previousExposure"
        )
        self.previous_public_exploit: str | None = raw_optional_str(
            raw_element, "previousPublicExploit"
        )
        self.previous_vulnerable_function_usage: str | None = raw_optional_str(
            raw_element, "previousVulnerableFunctionUsage"
        )


class RiskAssessmentSnapshot(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.base_risk_score: float | None = raw_optional_float(
            raw_element, "baseRiskScore"
        )
        self.exposure: str | None = raw_optional_str(raw_element, "exposure")
        self.number_of_affected_entities: int | None = raw_optional_int(
            raw_element, "numberOfAffectedEntities"
        )
        self.number_of_affected_nodes: int | None = raw_optional_int(
            raw_element, "numberOfAffectedNodes"
        )
        self.number_of_affected_process_groups: int | None = raw_optional_int(
            raw_element, "numberOfAffectedProcessGroups"
        )
        self.number_of_reachable_data_assets: int | None = raw_optional_int(
            raw_element, "numberOfReachableDataAssets"
        )
        self.number_of_related_attacks: int | None = raw_optional_int(
            raw_element, "numberOfRelatedAttacks"
        )
        self.public_exploit: str | None = raw_optional_str(raw_element, "publicExploit")
        self.risk_level: SecurityProblemRiskLevel | None = (
            SecurityProblemRiskLevel(raw_element.get("riskLevel"))
            if raw_element.get("riskLevel")
            else None
        )
        self.risk_score: float | None = raw_optional_float(raw_element, "riskScore")
        self.vulnerable_function_usage: str | None = raw_optional_str(
            raw_element, "vulnerableFunctionUsage"
        )
        self.changes: RiskAssessmentChanges | None = raw_optional_object(
            raw_element,
            "changes",
            lambda value: RiskAssessmentChanges(raw_element=value),
        )


class RemediationItem(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.name: str | None = raw_optional_str(raw_element, "name")
        self.entity_ids: list[str] = raw_optional_str_list(raw_element, "entityIds")
        self.first_affected_timestamp: datetime | None = int64_to_datetime(
            raw_element.get("firstAffectedTimestamp")
        )
        self.resolved_timestamp: datetime | None = int64_to_datetime(
            raw_element.get("resolvedTimestamp")
        )
        self.vulnerability_state: VulnerabilityState | None = (
            VulnerabilityState(raw_element.get("vulnerabilityState"))
            if raw_element.get("vulnerabilityState")
            else None
        )
        self.assessment: RemediationAssessment | None = raw_optional_object(
            raw_element,
            "assessment",
            lambda value: RemediationAssessment(raw_element=value),
        )
        self.mute_state: RemediationItemMuteState | None = raw_optional_object(
            raw_element,
            "muteState",
            lambda value: RemediationItemMuteState(raw_element=value),
        )
        self.remediation_progress: RemediationProgress | None = raw_optional_object(
            raw_element,
            "remediationProgress",
            lambda value: RemediationProgress(raw_element=value),
        )
        self.tracking_link: TrackingLink | None = raw_optional_object(
            raw_element, "trackingLink", lambda value: TrackingLink(raw_element=value)
        )
        self.vulnerable_components: list[VulnerableComponent] | None = (
            raw_optional_object_list(
                raw_element,
                "vulnerableComponents",
                lambda value: VulnerableComponent(raw_element=value),
            )
        )


class RemediationAssessment(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.assessment_accuracy: str | None = raw_optional_str(
            raw_element, "assessmentAccuracy"
        )
        self.assessment_accuracy_details: AssessmentAccuracyDetails | None = (
            raw_optional_object(
                raw_element,
                "assessmentAccuracyDetails",
                lambda value: AssessmentAccuracyDetails(raw_element=value),
            )
        )
        self.data_assets: str | None = raw_optional_str(raw_element, "dataAssets")
        self.exposure: str | None = raw_optional_str(raw_element, "exposure")
        self.number_of_data_assets: int | None = raw_optional_int(
            raw_element, "numberOfDataAssets"
        )
        self.vulnerable_function_restart_required: bool | None = raw_optional_bool(
            raw_element, "vulnerableFunctionRestartRequired"
        )
        self.vulnerable_function_usage: str | None = raw_optional_str(
            raw_element, "vulnerableFunctionUsage"
        )
        self.vulnerable_functions_in_use: list[VulnerableFunction] | None = (
            raw_optional_object_list(
                raw_element,
                "vulnerableFunctionsInUse",
                lambda value: VulnerableFunction(raw_element=value),
            )
        )
        self.vulnerable_functions_not_available: list[VulnerableFunction] | None = (
            raw_optional_object_list(
                raw_element,
                "vulnerableFunctionsNotAvailable",
                lambda value: VulnerableFunction(raw_element=value),
            )
        )
        self.vulnerable_functions_not_in_use: list[VulnerableFunction] | None = (
            raw_optional_object_list(
                raw_element,
                "vulnerableFunctionsNotInUse",
                lambda value: VulnerableFunction(raw_element=value),
            )
        )


class RemediationItemMuteState(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.comment: str | None = raw_optional_str(raw_element, "comment")
        self.last_updated_timestamp: datetime | None = int64_to_datetime(
            raw_element.get("lastUpdatedTimestamp")
        )
        self.muted: bool | None = raw_optional_bool(raw_element, "muted")
        self.reason: MuteReason | None = (
            MuteReason(raw_element.get("reason")) if raw_element.get("reason") else None
        )
        self.user: str | None = raw_optional_str(raw_element, "user")


class RemediationProgress(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.affected_entities: list[str] = raw_optional_str_list(
            raw_element, "affectedEntities"
        )
        self.unaffected_entities: list[str] = raw_optional_str_list(
            raw_element, "unaffectedEntities"
        )


class TrackingLink(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.display_name: str | None = raw_optional_str(raw_element, "displayName")
        self.last_updated_timestamp: datetime | None = int64_to_datetime(
            raw_element.get("lastUpdatedTimestamp")
        )
        self.url: str | None = raw_optional_str(raw_element, "url")
        self.user: str | None = raw_optional_str(raw_element, "user")


class RemediationProgressEntity(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.name: str | None = raw_optional_str(raw_element, "name")
        self.first_affected_timestamp: datetime | None = int64_to_datetime(
            raw_element.get("firstAffectedTimestamp")
        )
        self.state: RemediationProgressEntityState | None = (
            RemediationProgressEntityState(raw_element.get("state"))
            if raw_element.get("state")
            else None
        )
        self.assessment: RemediationProgressEntityAssessment | None = (
            raw_optional_object(
                raw_element,
                "assessment",
                lambda value: RemediationProgressEntityAssessment(raw_element=value),
            )
        )
        self.vulnerable_components: (
            list[RemediationProgressVulnerableComponent] | None
        ) = raw_optional_object_list(
            raw_element,
            "vulnerableComponents",
            lambda value: RemediationProgressVulnerableComponent(raw_element=value),
        )


class RemediationProgressEntityAssessment(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.vulnerable_function_restart_required: bool | None = raw_optional_bool(
            raw_element, "vulnerableFunctionRestartRequired"
        )
        self.vulnerable_function_usage: str | None = raw_optional_str(
            raw_element, "vulnerableFunctionUsage"
        )
        self.vulnerable_functions_in_use: list[VulnerableFunction] | None = (
            raw_optional_object_list(
                raw_element,
                "vulnerableFunctionsInUse",
                lambda value: VulnerableFunction(raw_element=value),
            )
        )
        self.vulnerable_functions_not_available: list[VulnerableFunction] | None = (
            raw_optional_object_list(
                raw_element,
                "vulnerableFunctionsNotAvailable",
                lambda value: VulnerableFunction(raw_element=value),
            )
        )
        self.vulnerable_functions_not_in_use: list[VulnerableFunction] | None = (
            raw_optional_object_list(
                raw_element,
                "vulnerableFunctionsNotInUse",
                lambda value: VulnerableFunction(raw_element=value),
            )
        )


class VulnerableFunctionsContainer(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.vulnerable_functions: list[VulnerableFunctionProcessGroups] | None = (
            raw_optional_object_list(
                raw_element,
                "vulnerableFunctions",
                lambda value: VulnerableFunctionProcessGroups(raw_element=value),
            )
        )
        self.vulnerable_functions_by_process_group: (
            list[ProcessGroupVulnerableFunctions] | None
        ) = raw_optional_object_list(
            raw_element,
            "vulnerableFunctionsByProcessGroup",
            lambda value: ProcessGroupVulnerableFunctions(raw_element=value),
        )


class VulnerableFunction(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.class_name: str | None = raw_optional_str(raw_element, "className")
        self.file_path: str | None = raw_optional_str(raw_element, "filePath")
        self.function_name: str | None = raw_optional_str(raw_element, "functionName")


class VulnerableFunctionProcessGroups(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.function: VulnerableFunction | None = raw_optional_object(
            raw_element, "function", lambda value: VulnerableFunction(raw_element=value)
        )
        self.process_groups_in_use: list[str] = raw_optional_str_list(
            raw_element, "processGroupsInUse"
        )
        self.process_groups_not_available: list[str] = raw_optional_str_list(
            raw_element, "processGroupsNotAvailable"
        )
        self.process_groups_not_in_use: list[str] = raw_optional_str_list(
            raw_element, "processGroupsNotInUse"
        )
        self.usage: str | None = raw_optional_str(raw_element, "usage")


class ProcessGroupVulnerableFunctions(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.process_group: str | None = raw_optional_str(raw_element, "processGroup")
        self.functions_in_use: list[VulnerableFunction] | None = (
            raw_optional_object_list(
                raw_element,
                "functionsInUse",
                lambda value: VulnerableFunction(raw_element=value),
            )
        )
        self.functions_not_available: list[VulnerableFunction] | None = (
            raw_optional_object_list(
                raw_element,
                "functionsNotAvailable",
                lambda value: VulnerableFunction(raw_element=value),
            )
        )
        self.functions_not_in_use: list[VulnerableFunction] | None = (
            raw_optional_object_list(
                raw_element,
                "functionsNotInUse",
                lambda value: VulnerableFunction(raw_element=value),
            )
        )


class VulnerableFunctionInput(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.type: VulnerableFunctionInputType | None = (
            VulnerableFunctionInputType(raw_element.get("type"))
            if raw_element.get("type")
            else None
        )
        self.input_segments: list[VulnerableFunctionInputSegment] | None = (
            raw_optional_object_list(
                raw_element,
                "inputSegments",
                lambda value: VulnerableFunctionInputSegment(raw_element=value),
            )
        )


class VulnerableFunctionInputSegment(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.type: VulnerableFunctionInputSegmentType | None = (
            VulnerableFunctionInputSegmentType(raw_element.get("type"))
            if raw_element.get("type")
            else None
        )
        self.value: str | None = raw_optional_str(raw_element, "value")


class VulnerableComponent(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.affected_entities: list[str] = raw_optional_str_list(
            raw_element, "affectedEntities"
        )
        self.display_name: str | None = raw_optional_str(raw_element, "displayName")
        self.file_name: str | None = raw_optional_str(raw_element, "fileName")
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.load_origins: list[str] = raw_optional_str_list(raw_element, "loadOrigins")
        self.number_of_affected_entities: int | None = raw_optional_int(
            raw_element, "numberOfAffectedEntities"
        )
        self.short_name: str | None = raw_optional_str(raw_element, "shortName")


class RemediationProgressVulnerableComponent(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.display_name: str | None = raw_optional_str(raw_element, "displayName")
        self.file_name: str | None = raw_optional_str(raw_element, "fileName")
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.load_origins: list[str] = raw_optional_str_list(raw_element, "loadOrigins")
        self.short_name: str | None = raw_optional_str(raw_element, "shortName")


class RelatedAttacksList(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.attacks: list[str] = raw_optional_str_list(raw_element, "attacks")


class RelatedContainerList(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.container_images: list[RelatedContainerImage] | None = (
            raw_optional_object_list(
                raw_element,
                "containerImages",
                lambda value: RelatedContainerImage(raw_element=value),
            )
        )


class RelatedContainerImage(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.affected_entities: list[str] = raw_optional_str_list(
            raw_element, "affectedEntities"
        )
        self.image_id: str | None = raw_optional_str(raw_element, "imageId")
        self.image_name: str | None = raw_optional_str(raw_element, "imageName")
        self.number_of_affected_entities: int | None = raw_optional_int(
            raw_element, "numberOfAffectedEntities"
        )


class RelatedEntitiesList(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.applications: list[RelatedEntity] | None = raw_optional_object_list(
            raw_element, "applications", lambda value: RelatedEntity(raw_element=value)
        )
        self.databases: list[str] = raw_optional_str_list(raw_element, "databases")
        self.hosts: list[RelatedEntity] | None = raw_optional_object_list(
            raw_element, "hosts", lambda value: RelatedEntity(raw_element=value)
        )
        self.kubernetes_clusters: list[RelatedEntity] | None = raw_optional_object_list(
            raw_element,
            "kubernetesClusters",
            lambda value: RelatedEntity(raw_element=value),
        )
        self.kubernetes_workloads: list[RelatedEntity] | None = (
            raw_optional_object_list(
                raw_element,
                "kubernetesWorkloads",
                lambda value: RelatedEntity(raw_element=value),
            )
        )
        self.services: list[RelatedService] | None = raw_optional_object_list(
            raw_element, "services", lambda value: RelatedService(raw_element=value)
        )


class RelatedEntity(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.affected_entities: list[str] = raw_optional_str_list(
            raw_element, "affectedEntities"
        )
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.number_of_affected_entities: int | None = raw_optional_int(
            raw_element, "numberOfAffectedEntities"
        )


class RelatedService(RelatedEntity):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.exposure: str | None = raw_optional_str(raw_element, "exposure")


class BulkMuteSummary(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.mute_state_change_triggered: bool | None = raw_element.get(
            "muteStateChangeTriggered"
        )
        self.reason: str | None = raw_element.get("reason")
        self.security_problem_id: str | None = raw_element.get("securityProblemId")
        self.remediation_item_id: str | None = raw_element.get("remediationItemId")


class BulkMuteResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
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


class CodeLevelVulnerabilityType(Enum):
    CMD_INJECTION = "CMD_INJECTION"
    IMPROPER_INPUT_VALIDATION = "IMPROPER_INPUT_VALIDATION"
    SQL_INJECTION = "SQL_INJECTION"
    SSRF = "SSRF"


class SecurityProblemEventReason(Enum):
    ASSESSMENT_CHANGED = "ASSESSMENT_CHANGED"
    SECURITY_PROBLEM_CREATED = "SECURITY_PROBLEM_CREATED"
    SECURITY_PROBLEM_MUTED = "SECURITY_PROBLEM_MUTED"
    SECURITY_PROBLEM_REOPENED = "SECURITY_PROBLEM_REOPENED"
    SECURITY_PROBLEM_RESOLVED = "SECURITY_PROBLEM_RESOLVED"
    SECURITY_PROBLEM_UNMUTED = "SECURITY_PROBLEM_UNMUTED"
    VULNERABILITY_DEPRECATED = "VULNERABILITY_DEPRECATED"
    VULNERABILITY_ID_CHANGED = "VULNERABILITY_ID_CHANGED"


class MuteReason(Enum):
    AFFECTED = "AFFECTED"
    CONFIGURATION_NOT_AFFECTED = "CONFIGURATION_NOT_AFFECTED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    IGNORE = "IGNORE"
    INITIAL_STATE = "INITIAL_STATE"
    OTHER = "OTHER"
    VULNERABLE_CODE_NOT_IN_USE = "VULNERABLE_CODE_NOT_IN_USE"


class VulnerabilityState(Enum):
    RESOLVED = "RESOLVED"
    VULNERABLE = "VULNERABLE"


class RemediationProgressEntityState(Enum):
    AFFECTED = "AFFECTED"
    UNAFFECTED = "UNAFFECTED"


class VulnerableFunctionInputType(Enum):
    COMMAND = "COMMAND"
    HTTP_CLIENT = "HTTP_CLIENT"
    JNDI = "JNDI"
    SQL_STATEMENT = "SQL_STATEMENT"


class VulnerableFunctionInputSegmentType(Enum):
    MALICIOUS_INPUT = "MALICIOUS_INPUT"
    REGULAR_INPUT = "REGULAR_INPUT"
    TAINTED_INPUT = "TAINTED_INPUT"
