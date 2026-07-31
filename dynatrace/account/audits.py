"""Account audits API wrappers."""

import builtins
from datetime import datetime
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.utils import timestamp_to_string


class AccountAuditsService:
    """/audit/v1 Account audits API."""

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def list(
        self,
        account_uuid: str,
        start_time: datetime | str | None = None,
        end_time: datetime | str | None = None,
        add_fields: builtins.list[str] | None = None,
        filter: str | None = None,
        limit: int | None = None,
        scan_limit_gigabyte: int | None = None,
        result_size_limit_megabyte: int | None = None,
    ) -> "AuditsByAccount":
        params: dict[str, Any] = {
            "startTime": timestamp_to_string(start_time),
            "endTime": timestamp_to_string(end_time),
            "filter": filter,
            "limit": limit,
            "scanLimitGigabyte": scan_limit_gigabyte,
            "resultSizeLimitMegabyte": result_size_limit_megabyte,
        }
        if add_fields:
            params["addFields"] = ",".join(add_fields)

        resp = (
            await self.__http_client.make_request(
                f"/audit/v1/accounts/{account_uuid}",
                params=params,
            )
        ).json()
        return AuditsByAccount(raw_element=resp)


class Audit(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.event_id: str | None = raw_element.get("eventId")
        self.timestamp: str | None = raw_element.get("timestamp")
        self.user: str | None = raw_element.get("user")
        self.resource: str | None = raw_element.get("resource")
        self.resource_name: str | None = raw_element.get("resourceName")
        self.event_provider: str | None = raw_element.get("eventProvider")
        self.event_type: str | None = raw_element.get("eventType")
        self.account_uuid: str | None = raw_element.get("accountUuid")
        self.authentication_client_id: str | None = raw_element.get(
            "authenticationClientId"
        )
        self.authentication_grant_type: str | None = raw_element.get(
            "authenticationGrantType"
        )
        self.authentication_token: str | None = raw_element.get("authenticationToken")
        self.authentication_type: str | None = raw_element.get("authenticationType")
        self.details: dict[str, str] | None = raw_element.get("details")
        self.event_outcome: str | None = raw_element.get("eventOutcome")
        self.event_reason: str | None = raw_element.get("eventReason")
        self.event_version: str | None = raw_element.get("eventVersion")
        self.origin_address: str | None = raw_element.get("originAddress")
        self.origin_session: str | None = raw_element.get("originSession")
        self.origin_type: str | None = raw_element.get("originType")
        self.origin_x_forwarded_for: str | None = raw_element.get("originXForwardedFor")
        self.resource_id: str | None = raw_element.get("resourceId")
        self.environment_uuid: str | None = raw_element.get("environmentUuid")
        self.user_organization: str | None = raw_element.get("userOrganization")


class AuditWarning(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.message: str | None = raw_element.get("message")


class AuditsByAccount(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.audits: builtins.list[Audit] = [
            Audit(raw_element=a) for a in raw_element.get("audits", [])
        ]
        self.warnings: builtins.list[AuditWarning] = [
            AuditWarning(raw_element=w) for w in raw_element.get("warnings", [])
        ]
