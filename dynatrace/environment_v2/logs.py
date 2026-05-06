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

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import timestamp_to_string


class LogService:
    # TODO - Add search and aggregate
    ENDPOINT = "/api/v2/logs"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def export(
        self,
        query: str | None = None,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
        sort: str | None = None,
        page_size: int | None = None,
    ) -> PaginatedList["LogRecord"]:
        """
        Gets the log records matching the provided criteria. Retrieves all records using pagination.
        :param query: The log search query
        :param page_size: Number of results per page
        :param time_from: Start of the requested timeframe
        :param time_to: End of the requested timefram
        :param sort: Defines the ordering of log records
        :return A list of log records
        """
        params = {
            "query": query,
            "pageSize": page_size,
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
            "sort": sort,
        }
        return await PaginatedList(
            LogRecord,
            self.__http_client,
            "/api/v2/logs/export",
            params,
            list_item="results",
        ).initialize()

    async def ingest(self, payload: dict[str, Any] | list[dict[str, Any]]) -> Response:
        """
        Ingests logs into the Dynatrace log store.
        :param payload: A list of log entries or a single log entry, which are JSON objects (dictionaries)
        :return: The HTTP Response
        """
        headers = {"Content-Type": "application/json; charset=utf-8"}
        return await self.__http_client.make_request(
            f"{self.ENDPOINT}/ingest", params=payload, method="POST", headers=headers
        )


class LogRecord(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.additional_columns: dict = raw_element.get("additionalColumns")
        self.event_type: EventType = EventType(raw_element.get("eventType"))
        self.timestamp: datetime = datetime.fromtimestamp(
            raw_element.get("timestamp") / 1000,
            UTC,
        )
        self.content: str = raw_element.get("content")
        self.status: LogRecordStatus = LogRecordStatus(raw_element.get("status"))


class EventType(Enum):
    K8S = "K8S"
    LOG = "LOG"
    SFM = "SFM"


class LogRecordStatus(Enum):
    ERROR = "ERROR"
    INFO = "INFO"
    NONE = "NONE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    WARN = "WARN"
