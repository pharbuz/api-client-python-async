from datetime import datetime

import dynatrace.environment_v2.security_problems as sp
from dynatrace import DynatraceAsync
from dynatrace.environment_v2.schemas import ManagementZone
from dynatrace.pagination import PaginatedList
from test.async_utils import collect

SECURITY_PROBLEM_ID = "12544152654387159360"
REMEDIATION_ITEM_ID = "ri-1"


async def test_list(dt: DynatraceAsync):
    security_problems = await dt.security_problems.list(time_from="now-30d")

    assert isinstance(security_problems, PaginatedList)
    security_problem_list = await collect(security_problems)
    assert len(security_problem_list) == 2
    assert all(isinstance(p, sp.SecurityProblem) for p in security_problem_list)


async def test_get(dt: DynatraceAsync):
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


async def test_all_required_endpoints(dt: DynatraceAsync):
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
    assert remediation_item.remediation_item_id == REMEDIATION_ITEM_ID

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
