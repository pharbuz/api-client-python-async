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
from datetime import datetime
from enum import Enum
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import int64_to_datetime, timestamp_to_string


class MetricService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def query(
        self,
        metric_selector: str,
        resolution: str = None,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
        entity_selector: str | None = None,
        mz_selector: str | None = None,
    ) -> PaginatedList["MetricSeriesCollection"]:

        params = {
            "metricSelector": metric_selector,
            "resolution": resolution,
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
            "entitySelector": entity_selector,
            "mzSelector": mz_selector,
        }
        return await PaginatedList(
            MetricSeriesCollection,
            self.__http_client,
            "/api/v2/metrics/query",
            params,
            list_item="result",
        ).initialize()

    async def list(
        self,
        metric_selector: str | None = None,
        text: str | None = None,
        fields: str | None = None,
        written_since: str | datetime | None = None,
        metadata_selector: str | None = None,
        page_size=100,
    ) -> PaginatedList["MetricDescriptor"]:
        params = {
            "pageSize": page_size,
            "metricSelector": metric_selector,
            "text": text,
            "fields": fields,
            "writtenSince": timestamp_to_string(written_since),
            "metadataSelector": metadata_selector,
        }
        return await PaginatedList(
            MetricDescriptor,
            self.__http_client,
            "/api/v2/metrics",
            params,
            list_item="metrics",
        ).initialize()

    async def get(self, metric_id: str) -> "MetricDescriptor":
        response = (
            await self.__http_client.make_request(f"/api/v2/metrics/{metric_id}")
        ).json()
        return MetricDescriptor(http_client=self.__http_client, raw_element=response)

    async def delete(self, metric_id) -> Response:
        return await self.__http_client.make_request(
            f"/api/v2/metrics/{metric_id}", method="DELETE"
        )

    async def ingest(self, lines: builtins.list[str]):
        lines = "\n".join(lines).encode("utf-8")
        return (
            await self.__http_client.make_request(
                "/api/v2/metrics/ingest",
                method="POST",
                data=lines,
                headers={"Content-Type": "text/plain; charset=utf-8"},
            )
        ).json()


class MetricSeries(DynatraceObject):
    def _create_from_raw_data(self, raw_element):
        self.timestamps: list[datetime] = [
            int64_to_datetime(timestamp)
            for timestamp in raw_element.get("timestamps", [])
        ]
        self.dimensions: list[str] = raw_element.get("dimensions", [])
        self.values: list[float] = raw_element.get("values", [])
        self.dimension_map: dict[str, Any] | None = raw_element.get("dimensionMap", [])


class MetricSeriesCollection(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict):
        self.metric_id: str = raw_element.get("metricId")
        self.data: list[MetricSeries] = [
            MetricSeries(self._http_client, self._headers, metric_serie)
            for metric_serie in raw_element.get("data", [])
        ]
        self.warnings: list[str] | None = raw_element.get("warnings")


class MetricDefaultAggregation(DynatraceObject):
    def _create_from_raw_data(self, raw_element):
        self.parameter: float = raw_element.get("parameter")
        self.type: str = raw_element.get("type")


class MetricDimensionDefinition(DynatraceObject):
    def _create_from_raw_data(self, raw_element):
        self.index: int = raw_element.get("index")
        self.name: str = raw_element.get("name")
        self.key: str = raw_element.get("key")
        self.type: str = raw_element.get("type")


class AggregationType(Enum):
    AUTO = "auto"
    AVG = "avg"
    COUNT = "count"
    MAX = "max"
    MEDIAN = "median"
    MIN = "min"
    PERCENTILE = "percentile"
    SUM = "sum"
    VALUE = "value"


class Transformation(Enum):
    DEFAULT = "default"
    FILTER = "filter"
    FOLD = "fold"
    LAST = "last"
    LIMIT = "limit"
    MERGE = "merge"
    NAMES = "names"
    PARENTS = "parents"
    RATE = "rate"
    SORT = "sort"
    SPLITBY = "splitBy"
    TIMESHIFT = "timeshift"
    LASTREAL = "lastReal"
    SETUNIT = "setUnit"


class MetricDescriptor(DynatraceObject):
    def _create_from_raw_data(self, raw_element):

        # required
        self.metric_id: str = raw_element.get("metricId")

        # optional
        self.aggregation_types: list[AggregationType] | None = [
            AggregationType(element)
            for element in raw_element.get("aggregationTypes", [])
        ]
        self.created: datetime | None = int64_to_datetime(raw_element.get("created"))
        self.ddu_billable: bool | None = raw_element.get("dduBillable")
        self.default_aggregation: MetricDefaultAggregation | None = (
            MetricDefaultAggregation(raw_element=raw_element.get("defaultAggregation"))
        )
        self.description: str | None = raw_element.get("description")
        self.dimension_definitions: list[MetricDimensionDefinition] | None = [
            MetricDimensionDefinition(raw_element=element)
            for element in raw_element.get("dimensionDefinitions", [])
        ]
        self.display_name: str | None = raw_element.get("displayName")
        self.entity_type: list[str] | None = raw_element.get("entityType", [])
        self.impact_relevant: bool | None = raw_element.get("impactRelevant")
        self.last_written: datetime | None = int64_to_datetime(
            raw_element.get("lastWritten")
        )
        self.maximum_value: float | None = raw_element.get("maximumValue")
        self.metric_value_type: MetricValueType | None = (
            MetricValueType(raw_element=raw_element.get("metricValueType"))
            if raw_element.get("metricValueType")
            else None
        )
        self.minimum_value: float | None = raw_element.get("minimumValue")
        self.root_cause_relevant: bool | None = raw_element.get("rootCauseRelevant")
        self.tags: list[str] | None = raw_element.get("tags")
        self.transformations: list[Transformation] | None = [
            Transformation(element)
            for element in raw_element.get("transformations", [])
        ]
        self.unit: str | None = raw_element.get("unit")
        self.warnings: list[str] | None = raw_element.get("warnings")


class ValueType(Enum):
    ERROR = "error"
    SCORE = "score"
    UNKNOWN = "unknown"


class MetricValueType(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.type = ValueType(raw_element.get("type"))
