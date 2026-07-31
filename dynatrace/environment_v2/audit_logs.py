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

from datetime import datetime
from enum import Enum
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import (
    raw_required_bool,
    raw_required_datetime,
    raw_required_str,
    timestamp_to_string,
)


class AuditLogsService:

    # TODO - Early adopter as of May 14th 2021, check back later for changes
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self,
        log_filter: str | None = None,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
        sort: str | None = None,
    ) -> PaginatedList["AuditLogEntry"]:
        params = {
            "filter": log_filter,
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
            "sort": sort,
        }
        return await PaginatedList(
            target_class=AuditLogEntry,
            http_client=self.__http_client,
            target_url="/api/v2/auditlogs",
            target_params=params,
            list_item="auditLogs",
        ).initialize()

    async def get(self, log_id: str) -> "AuditLogEntry":
        response = (
            await self.__http_client.make_request(f"/api/v2/auditlogs/{log_id}")
        ).json()
        return AuditLogEntry(raw_element=response)


class EventType(Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"
    GENERAL = "GENERAL"
    GET = "GET"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    READ = "READ"
    REMOTE_CONFIGURATION_MANAGEMENT = "REMOTE_CONFIGURATION_MANAGEMENT"
    REVOKE = "REVOKE"
    TAG_ADD = "TAG_ADD"
    TAG_REMOVE = "TAG_REMOVE"
    TAG_UPDATE = "TAG_UPDATE"
    UPDATE = "UPDATE"


class UserType(Enum):
    PUBLIC_TOKEN_IDENTIFIER = "PUBLIC_TOKEN_IDENTIFIER"
    REQUEST_ID = "REQUEST_ID"
    SERVICE_NAME = "SERVICE_NAME"
    TOKEN_HASH = "TOKEN_HASH"
    USER_NAME = "USER_NAME"


class AuditLogEntry(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.category: str = raw_required_str(raw_element, "category")
        self.environment_id: str = raw_required_str(raw_element, "environmentId")
        self.event_type: EventType = EventType(raw_element["eventType"])
        self.log_id: str = raw_required_str(raw_element, "logId")
        self.success: bool = raw_required_bool(raw_element, "success")
        self.timestamp: datetime = raw_required_datetime(raw_element, "timestamp")
        self.user: str = raw_required_str(raw_element, "user")
        self.user_type: UserType = UserType(raw_element["userType"])

        self.entity_id: str | None = raw_element.get("entityId")
        self.user_origin: str | None = raw_element.get("userOrigin")
        self.message: str | None = raw_element.get("message")
        self.patch: list[dict[str, Any]] | None = raw_element.get("patch")
