from datetime import datetime

import dynatrace.environment_v2.security_problems as sp
from dynatrace import DynatraceAsync
from dynatrace.environment_v2.schemas import ManagementZone
from dynatrace.pagination import PaginatedList
from dynatrace.utils import int64_to_datetime
from test.async_utils import collect

SECURITY_PROBLEM_ID = "12544152654387159360"
REMEDIATION_ITEM_ID = "ri-1"


async def test_list(dt: DynatraceAsync) -> None:
    security_problems = await dt.security_problems.list(time_from="now-30d")

    assert isinstance(security_problems, PaginatedList)
    security_problem_list = await collect(security_problems)
    assert len(security_problem_list) == 2
    assert all(isinstance(p, sp.SecurityProblem) for p in security_problem_list)


async def test_get(dt: DynatraceAsync) -> None:
    security_problem = await dt.security_problems.get(
        security_problem_id=SECURITY_PROBLEM_ID
    )

    assert isinstance(security_problem, sp.SecurityProblem)
    assert isinstance(security_problem.first_seen_timestamp, datetime)
    assert isinstance(security_problem.last_opened_timestamp, datetime)
    assert isinstance(security_problem.last_updated_timestamp, datetime)
    assert isinstance(security_problem.last_resolved_timestamp, datetime)
    assert isinstance(security_problem.risk_assessment, sp.RiskAssessment)
    assert isinstance(security_problem.management_zones, list)
    assert all(
        isinstance(management_zone, ManagementZone)
        for management_zone in security_problem.management_zones
    )

    assert security_problem.security_problem_id == SECURITY_PROBLEM_ID
    assert security_problem.display_id == "S-1234"
    assert security_problem.status == sp.SecurityProblemStatus.OPEN
    assert security_problem.technology == sp.SecurityProblemTechnology.PYTHON
    assert security_problem.vulnerability_type == sp.VulnerabilityType.CODE_LEVEL
    assert (
        security_problem.risk_assessment.risk_level == sp.SecurityProblemRiskLevel.HIGH
    )
    assert security_problem.risk_assessment.base_risk_level == (
        sp.SecurityProblemRiskLevel.MEDIUM
    )


async def test_all_required_endpoints(dt: DynatraceAsync) -> None:
    events = await dt.security_problems.list_events(SECURITY_PROBLEM_ID)
    events_list = await collect(events)
    assert len(events_list) == 1
    assert isinstance(events_list[0], sp.SecurityProblemEvent)

    mute_response = await dt.security_problems.mute(
        SECURITY_PROBLEM_ID, reason="OTHER", comment="mute"
    )
    assert mute_response.status_code == 200

    unmute_response = await dt.security_problems.unmute(
        SECURITY_PROBLEM_ID, reason="AFFECTED", comment="unmute"
    )
    assert unmute_response.status_code == 200

    remediation_items = await dt.security_problems.list_remediation_items(
        SECURITY_PROBLEM_ID
    )
    assert len(remediation_items) == 1
    assert isinstance(remediation_items[0], sp.RemediationItem)

    remediation_item = await dt.security_problems.get_remediation_item(
        SECURITY_PROBLEM_ID, REMEDIATION_ITEM_ID
    )
    assert isinstance(remediation_item, sp.RemediationItem)

    remediation_mute_state_response = (
        await dt.security_problems.set_remediation_item_mute_state(
            SECURITY_PROBLEM_ID,
            REMEDIATION_ITEM_ID,
            muted=True,
            reason="IGNORE",
            comment="test",
        )
    )
    assert remediation_mute_state_response.status_code == 200

    progress_entities = await dt.security_problems.list_remediation_progress_entities(
        SECURITY_PROBLEM_ID, REMEDIATION_ITEM_ID
    )
    assert len(progress_entities) == 1
    assert isinstance(progress_entities[0], sp.RemediationProgressEntity)

    remediation_bulk_mute = await dt.security_problems.bulk_mute_remediation_items(
        SECURITY_PROBLEM_ID, reason="OTHER", remediation_item_ids=[REMEDIATION_ITEM_ID]
    )
    assert isinstance(remediation_bulk_mute, sp.BulkMuteResponse)
    assert len(remediation_bulk_mute.summary) == 1

    remediation_bulk_unmute = await dt.security_problems.bulk_unmute_remediation_items(
        SECURITY_PROBLEM_ID,
        reason="AFFECTED",
        remediation_item_ids=[REMEDIATION_ITEM_ID],
    )
    assert isinstance(remediation_bulk_unmute, sp.BulkMuteResponse)
    assert len(remediation_bulk_unmute.summary) == 1

    tracking_links_response = (
        await dt.security_problems.update_remediation_items_tracking_links(
            SECURITY_PROBLEM_ID,
            updates=[{"remediationItemId": REMEDIATION_ITEM_ID, "trackingLink": {}}],
            deletes=[],
        )
    )
    assert tracking_links_response.status_code == 200

    vulnerable_functions = await dt.security_problems.list_vulnerable_functions(
        SECURITY_PROBLEM_ID
    )
    assert isinstance(vulnerable_functions, sp.VulnerableFunctionsContainer)
    assert vulnerable_functions.vulnerable_functions is not None
    assert len(vulnerable_functions.vulnerable_functions) == 1

    bulk_mute = await dt.security_problems.bulk_mute(
        reason="OTHER", security_problem_ids=[SECURITY_PROBLEM_ID]
    )
    assert isinstance(bulk_mute, sp.BulkMuteResponse)
    assert len(bulk_mute.summary) == 1

    bulk_unmute = await dt.security_problems.bulk_unmute(
        reason="AFFECTED", security_problem_ids=[SECURITY_PROBLEM_ID]
    )
    assert isinstance(bulk_unmute, sp.BulkMuteResponse)
    assert len(bulk_unmute.summary) == 1


def test_security_problem_parses_openapi_model_fields() -> None:
    security_problem = sp.SecurityProblem(
        raw_element={
            "affectedEntities": ["PROCESS_GROUP-1"],
            "codeLevelVulnerabilityDetails": {
                "processGroupIds": ["PROCESS_GROUP-1"],
                "processGroups": ["checkout-service"],
                "shortVulnerabilityLocation": "Repository.find",
                "type": "SQL_INJECTION",
                "vulnerabilityLocation": "com.example.Repository.find",
                "vulnerableFunction": "find",
                "vulnerableFunctionInput": {
                    "inputSegments": [
                        {"type": "TAINTED_INPUT", "value": "request.query"}
                    ],
                    "type": "SQL_STATEMENT",
                },
            },
            "cveIds": ["CVE-2024-9999"],
            "description": "Code-level vulnerability",
            "displayId": "S-1234",
            "events": [
                {
                    "muteState": {
                        "comment": "accepted",
                        "reason": "AFFECTED",
                        "user": "user@example.com",
                    },
                    "reason": "SECURITY_PROBLEM_MUTED",
                    "riskAssessmentSnapshot": {
                        "baseRiskScore": 5.9,
                        "changes": {"deltaRiskScore": 1.1},
                        "exposure": "PUBLIC_NETWORK",
                        "numberOfAffectedEntities": 3,
                        "numberOfAffectedNodes": 2,
                        "numberOfAffectedProcessGroups": 1,
                        "numberOfReachableDataAssets": 1,
                        "numberOfRelatedAttacks": 0,
                        "publicExploit": "AVAILABLE",
                        "riskLevel": "HIGH",
                        "riskScore": 7.8,
                        "vulnerableFunctionUsage": "IN_USE",
                    },
                    "timestamp": 1717250400000,
                }
            ],
            "exposedEntities": ["PROCESS_GROUP-1"],
            "filteredCounts": {
                "affectedNodes": 2,
                "affectedProcessGroups": 1,
                "relatedDatabases": 1,
            },
            "firstSeenTimestamp": 1717243200000,
            "globalCounts": {
                "affectedNodes": 2,
                "affectedProcessGroups": 1,
                "vulnerableComponents": 1,
            },
            "lastOpenedTimestamp": 1717246800000,
            "lastResolvedTimestamp": 1717254000000,
            "lastUpdatedTimestamp": 1717250400000,
            "managementZones": [{"id": "1", "name": "Operations"}],
            "muteStateChangeInProgress": False,
            "muted": True,
            "packageName": "vulnerable-lib",
            "reachableDataAssets": ["SERVICE-DB"],
            "relatedAttacks": {"attacks": ["attack-id"]},
            "relatedContainerImages": {
                "containerImages": [
                    {
                        "affectedEntities": ["PROCESS_GROUP-1"],
                        "imageId": "sha256:123",
                        "imageName": "checkout:latest",
                        "numberOfAffectedEntities": 1,
                    }
                ]
            },
            "relatedEntities": {
                "databases": ["SERVICE-DB"],
                "services": [
                    {
                        "affectedEntities": ["PROCESS_GROUP-1"],
                        "exposure": "PUBLIC_NETWORK",
                        "id": "SERVICE-1",
                        "numberOfAffectedEntities": 1,
                    }
                ],
            },
            "remediationDescription": "Upgrade the package",
            "riskAssessment": {
                "assessmentAccuracy": "REDUCED",
                "assessmentAccuracyDetails": {
                    "reducedReasons": ["LIMITED_AGENT_SUPPORT"]
                },
                "baseRiskLevel": "MEDIUM",
                "baseRiskScore": 5.9,
                "baseRiskVector": "CVSS:3.1/AV:N/AC:L",
                "dataAssets": "REACHABLE",
                "exposure": "PUBLIC_NETWORK",
                "publicExploit": "AVAILABLE",
                "riskLevel": "HIGH",
                "riskScore": 7.8,
                "riskVector": "AV:N/AC:L",
                "vulnerableFunctionRestartRequired": True,
                "vulnerableFunctionUsage": "IN_USE",
            },
            "securityProblemId": SECURITY_PROBLEM_ID,
            "status": "OPEN",
            "technology": "PYTHON",
            "title": "Vulnerable package in production",
            "url": "https://tenant.example/ui/security/problems/S-1234",
            "vulnerabilityType": "CODE_LEVEL",
            "vulnerableComponents": [
                {
                    "affectedEntities": ["PROCESS_GROUP-1"],
                    "displayName": "vulnerable-lib",
                    "fileName": "vulnerable-lib.jar",
                    "id": "VULNERABLE_COMPONENT-1",
                    "numberOfAffectedEntities": 1,
                    "shortName": "vulnerable-lib",
                }
            ],
        }
    )

    assert security_problem.description == "Code-level vulnerability"
    assert security_problem.mute_state_change_in_progress is False
    assert security_problem.affected_entities == ["PROCESS_GROUP-1"]
    assert security_problem.exposed_entities == ["PROCESS_GROUP-1"]
    assert security_problem.reachable_data_assets == ["SERVICE-DB"]
    assert security_problem.global_counts is not None
    assert security_problem.global_counts.vulnerable_components == 1
    assert security_problem.filtered_counts is not None
    assert security_problem.filtered_counts.related_databases == 1
    assert security_problem.code_level_vulnerability_details is not None
    assert security_problem.code_level_vulnerability_details.type == (
        sp.CodeLevelVulnerabilityType.SQL_INJECTION
    )
    vulnerable_input = (
        security_problem.code_level_vulnerability_details.vulnerable_function_input
    )
    assert vulnerable_input is not None
    assert vulnerable_input.type == sp.VulnerableFunctionInputType.SQL_STATEMENT
    assert vulnerable_input.input_segments is not None
    assert vulnerable_input.input_segments[0].type == (
        sp.VulnerableFunctionInputSegmentType.TAINTED_INPUT
    )
    assert security_problem.events is not None
    assert security_problem.events[0].reason == (
        sp.SecurityProblemEventReason.SECURITY_PROBLEM_MUTED
    )
    assert security_problem.events[0].timestamp == int64_to_datetime(1717250400000)
    assert security_problem.events[0].mute_state is not None
    assert security_problem.events[0].mute_state.reason == sp.MuteReason.AFFECTED
    assert security_problem.risk_assessment is not None
    assert security_problem.risk_assessment.vulnerable_function_restart_required
    assert security_problem.risk_assessment.assessment_accuracy_details is not None
    assert security_problem.related_attacks is not None
    assert security_problem.related_attacks.attacks == ["attack-id"]
    assert security_problem.related_container_images is not None
    assert security_problem.related_container_images.container_images is not None
    assert security_problem.related_container_images.container_images[0].image_id == (
        "sha256:123"
    )
    assert security_problem.related_entities is not None
    assert security_problem.related_entities.services is not None
    assert security_problem.related_entities.services[0].exposure == "PUBLIC_NETWORK"
    assert security_problem.vulnerable_components is not None
    assert security_problem.vulnerable_components[0].short_name == "vulnerable-lib"


def test_security_problem_endpoint_models_parse_openapi_payloads() -> None:
    remediation_item = sp.RemediationItem(
        raw_element={
            "assessment": {
                "assessmentAccuracy": "FULL",
                "dataAssets": "REACHABLE",
                "exposure": "PUBLIC_NETWORK",
                "numberOfDataAssets": 1,
                "vulnerableFunctionRestartRequired": False,
                "vulnerableFunctionUsage": "IN_USE",
                "vulnerableFunctionsInUse": [
                    {
                        "className": "Parser",
                        "filePath": "parser.py",
                        "functionName": "parse",
                    }
                ],
            },
            "entityIds": ["PROCESS_GROUP-1"],
            "firstAffectedTimestamp": 1717243200000,
            "id": REMEDIATION_ITEM_ID,
            "muteState": {
                "comment": "accepted",
                "lastUpdatedTimestamp": 1717250400000,
                "muted": True,
                "reason": "OTHER",
                "user": "user@example.com",
            },
            "name": "checkout-service",
            "remediationProgress": {
                "affectedEntities": ["PROCESS_GROUP_INSTANCE-1"],
                "unaffectedEntities": ["PROCESS_GROUP_INSTANCE-2"],
            },
            "resolvedTimestamp": 1717254000000,
            "trackingLink": {
                "displayName": "SEC-1",
                "lastUpdatedTimestamp": 1717250400000,
                "url": "https://tracker.example/SEC-1",
                "user": "user@example.com",
            },
            "vulnerabilityState": "VULNERABLE",
            "vulnerableComponents": [
                {
                    "affectedEntities": ["PROCESS_GROUP-1"],
                    "displayName": "vulnerable-lib",
                    "fileName": "vulnerable-lib.jar",
                    "id": "VULNERABLE_COMPONENT-1",
                    "loadOrigins": ["RUNTIME"],
                    "numberOfAffectedEntities": 1,
                    "shortName": "vulnerable-lib",
                }
            ],
        }
    )
    assert remediation_item.id == REMEDIATION_ITEM_ID
    assert remediation_item.entity_ids == ["PROCESS_GROUP-1"]
    assert remediation_item.first_affected_timestamp == int64_to_datetime(1717243200000)
    assert remediation_item.vulnerability_state == sp.VulnerabilityState.VULNERABLE
    assert remediation_item.assessment is not None
    assert remediation_item.assessment.vulnerable_functions_in_use is not None
    assert remediation_item.assessment.vulnerable_functions_in_use[0].class_name == (
        "Parser"
    )
    assert remediation_item.mute_state is not None
    assert remediation_item.mute_state.reason == sp.MuteReason.OTHER
    assert remediation_item.remediation_progress is not None
    assert remediation_item.remediation_progress.affected_entities == [
        "PROCESS_GROUP_INSTANCE-1"
    ]
    assert remediation_item.tracking_link is not None
    assert remediation_item.tracking_link.display_name == "SEC-1"
    assert remediation_item.vulnerable_components is not None
    assert remediation_item.vulnerable_components[0].load_origins == ["RUNTIME"]

    progress_entity = sp.RemediationProgressEntity(
        raw_element={
            "assessment": {
                "vulnerableFunctionRestartRequired": True,
                "vulnerableFunctionUsage": "IN_USE",
                "vulnerableFunctionsInUse": [
                    {
                        "className": "Parser",
                        "filePath": "parser.py",
                        "functionName": "parse",
                    }
                ],
            },
            "firstAffectedTimestamp": 1717243200000,
            "id": "PROCESS_GROUP_INSTANCE-1",
            "name": "checkout-service-1",
            "state": "AFFECTED",
            "vulnerableComponents": [
                {
                    "displayName": "vulnerable-lib",
                    "fileName": "vulnerable-lib.jar",
                    "id": "VULNERABLE_COMPONENT-1",
                    "loadOrigins": ["RUNTIME"],
                    "shortName": "vulnerable-lib",
                }
            ],
        }
    )
    assert progress_entity.id == "PROCESS_GROUP_INSTANCE-1"
    assert progress_entity.state == sp.RemediationProgressEntityState.AFFECTED
    assert progress_entity.assessment is not None
    assert progress_entity.assessment.vulnerable_functions_in_use is not None
    assert progress_entity.vulnerable_components is not None
    assert progress_entity.vulnerable_components[0].load_origins == ["RUNTIME"]

    vulnerable_functions = sp.VulnerableFunctionsContainer(
        raw_element={
            "vulnerableFunctions": [
                {
                    "function": {
                        "className": "Parser",
                        "filePath": "parser.py",
                        "functionName": "parse",
                    },
                    "processGroupsInUse": ["PROCESS_GROUP-1"],
                    "processGroupsNotAvailable": [],
                    "processGroupsNotInUse": ["PROCESS_GROUP-2"],
                    "usage": "IN_USE",
                }
            ],
            "vulnerableFunctionsByProcessGroup": [
                {
                    "functionsInUse": [
                        {
                            "className": "Parser",
                            "filePath": "parser.py",
                            "functionName": "parse",
                        }
                    ],
                    "functionsNotAvailable": [],
                    "functionsNotInUse": [],
                    "processGroup": "PROCESS_GROUP-1",
                }
            ],
        }
    )
    assert vulnerable_functions.vulnerable_functions is not None
    assert vulnerable_functions.vulnerable_functions[0].function is not None
    assert vulnerable_functions.vulnerable_functions[0].process_groups_in_use == [
        "PROCESS_GROUP-1"
    ]
    assert vulnerable_functions.vulnerable_functions_by_process_group is not None
    assert (
        vulnerable_functions.vulnerable_functions_by_process_group[0].functions_in_use
        is not None
    )
    assert (
        vulnerable_functions.vulnerable_functions_by_process_group[0]
        .functions_in_use[0]
        .function_name
        == "parse"
    )
