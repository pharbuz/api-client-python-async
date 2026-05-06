"""Account notifications API wrappers."""

from __future__ import annotations

import builtins
from datetime import datetime
from enum import Enum
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.utils import timestamp_to_string


class NotificationService:
    """/v1/accounts/{accountUuid}/notifications API."""

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def list(
        self,
        account_uuid: str,
        start_date_time: datetime | str | None = None,
        end_date_time: datetime | str | None = None,
        types: builtins.list[str | NotificationType] | None = None,
        severities: builtins.list[str | NotificationSeverity] | None = None,
        capabilities: builtins.list[str] | None = None,
        environments: builtins.list[str] | None = None,
        page: int | None = None,
        page_size: int | None = None,
        sorts: builtins.list[str | NotificationSortField] | None = None,
    ) -> NotificationList:
        body: dict[str, Any] = {
            "startDateTime": timestamp_to_string(start_date_time),
            "endDateTime": timestamp_to_string(end_date_time),
            "types": [self._enum_value(item) for item in types] if types else None,
            "severities": (
                [self._enum_value(item) for item in severities] if severities else None
            ),
            "capabilities": capabilities,
            "environments": environments,
            "page": page,
            "pageSize": page_size,
            "sorts": [self._enum_value(item) for item in sorts] if sorts else None,
        }

        resp = (
            await self.__http_client.make_request(
                f"/v1/accounts/{account_uuid}/notifications",
                method="POST",
                params=body,
            )
        ).json()
        return NotificationList(raw_element=resp)

    @staticmethod
    def _enum_value(value: str | Enum) -> str:
        return value.value if isinstance(value, Enum) else value


class NotificationType(Enum):
    FORECAST = "FORECAST"
    BUDGET = "BUDGET"
    COST = "COST"
    BYOK_REVOKED = "BYOK_REVOKED"
    BYOK_ACTIVATED = "BYOK_ACTIVATED"


class NotificationSeverity(Enum):
    SEVERE = "SEVERE"
    WARN = "WARN"
    INFO = "INFO"


class NotificationSortField(Enum):
    TYPE = "type"
    TYPE_DESC = "-type"
    DATE = "date"
    DATE_DESC = "-date"


class NotificationDetails(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.environments: builtins.list[str] | None = raw_element.get("environments")
        self.capabilities: builtins.list[str] | None = raw_element.get("capabilities")
        self.all_environments: bool | None = raw_element.get("allEnvironments")
        self.all_capabilities: bool | None = raw_element.get("allCapabilities")
        self.environment_uuid: str | None = raw_element.get("environmentUuid")
        self.key_name: str | None = raw_element.get("keyName")


class Notification(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.key: str | None = raw_element.get("key")
        self.account_uuid: str | None = raw_element.get("accountUuid")
        self.message: str | None = raw_element.get("message")
        self.severity: str | None = raw_element.get("severity")
        self.type: str | None = raw_element.get("type")
        details = raw_element.get("details") or {}
        self.details: NotificationDetails | None = (
            NotificationDetails(raw_element=details) if details else None
        )
        self.date: str | None = raw_element.get("date")


class NotificationList(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.records: builtins.list[Notification] = [
            Notification(raw_element=record)
            for record in raw_element.get("records", [])
        ]
        self.total_record_count: int | None = raw_element.get("totalRecordCount")
        self.has_next_page: bool | None = raw_element.get("hasNextPage")
