"""Grail DQL query execution API wrappers."""

from typing import Any, Union

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.utils import build_headers

BASE_PATH = "/platform/storage/query/v1"


class QueryExecutionService:
    ENDPOINT_EXECUTE = f"{BASE_PATH}/query:execute"
    ENDPOINT_POLL = f"{BASE_PATH}/query:poll"
    ENDPOINT_CANCEL = f"{BASE_PATH}/query:cancel"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    # Query execution endpoints.
    async def execute(
        self,
        query: str,
        default_sampling_ratio: float | None = None,
        default_scan_limit_gbytes: int | None = None,
        default_timeframe_start: str | None = None,
        default_timeframe_end: str | None = None,
        enable_preview: bool | None = None,
        enforce_query_consumption_limit: bool | None = None,
        fetch_timeout_seconds: int | None = None,
        filter_segments: list[dict[str, Any]] | None = None,
        include_types: bool | None = None,
        locale: str | None = None,
        max_result_bytes: int | None = None,
        max_result_records: int | None = None,
        query_options: dict[str, str] | None = None,
        request_timeout_milliseconds: int | None = None,
        timezone: str | None = None,
        enrich: str | None = None,
        dt_client_context: str | None = None,
        enforce_query_consumption_limit_header: bool | None = None,
    ) -> "QueryStartResponse":
        """Execute a DQL query and return result or request token."""
        headers = build_headers(
            dt_client_context, enforce_query_consumption_limit_header
        )
        body = {
            "query": query,
            "defaultSamplingRatio": default_sampling_ratio,
            "defaultScanLimitGbytes": default_scan_limit_gbytes,
            "defaultTimeframeStart": default_timeframe_start,
            "defaultTimeframeEnd": default_timeframe_end,
            "enablePreview": enable_preview,
            "enforceQueryConsumptionLimit": enforce_query_consumption_limit,
            "fetchTimeoutSeconds": fetch_timeout_seconds,
            "filterSegments": filter_segments,
            "includeTypes": include_types,
            "locale": locale,
            "maxResultBytes": max_result_bytes,
            "maxResultRecords": max_result_records,
            "queryOptions": query_options,
            "requestTimeoutMilliseconds": request_timeout_milliseconds,
            "timezone": timezone,
        }
        query_params = {"enrich": enrich}
        response = await self.__http_client.make_request(
            self.ENDPOINT_EXECUTE,
            params=body,
            headers=headers,
            method="POST",
            query_params=query_params,
        )
        return QueryStartResponse(self.__http_client, response.headers, response.json())

    async def poll(
        self,
        request_token: str,
        request_timeout_milliseconds: int | None = None,
        enrich: str | None = None,
        dt_client_context: str | None = None,
    ) -> "QueryPollResponse":
        """Poll query status and results."""
        headers = build_headers(dt_client_context, None)
        params = {
            "request-token": request_token,
            "request-timeout-milliseconds": request_timeout_milliseconds,
            "enrich": enrich,
        }
        response = await self.__http_client.make_request(
            self.ENDPOINT_POLL, params=params, headers=headers
        )
        return QueryPollResponse(self.__http_client, response.headers, response.json())

    async def cancel(
        self,
        request_token: str,
        enrich: str | None = None,
        dt_client_context: str | None = None,
    ) -> Union["QueryPollResponse", Response]:
        """Cancel query execution. Returns result if already finished."""
        headers = build_headers(dt_client_context, None)
        query_params = {
            "request-token": request_token,
            "enrich": enrich,
        }
        response = await self.__http_client.make_request(
            self.ENDPOINT_CANCEL,
            headers=headers,
            method="POST",
            query_params=query_params,
        )
        try:
            payload = response.json()
        except ValueError:
            return response
        return QueryPollResponse(self.__http_client, response.headers, payload)


# Shared DQL response primitives.
class PositionInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.column: int | None = raw_element.get("column")
        self.index: int | None = raw_element.get("index")
        self.line: int | None = raw_element.get("line")


class TokenPosition(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.start: PositionInfo | None = (
            PositionInfo(raw_element=raw_element.get("start"))
            if raw_element.get("start")
            else None
        )
        self.end: PositionInfo | None = (
            PositionInfo(raw_element=raw_element.get("end"))
            if raw_element.get("end")
            else None
        )


class MetadataNotification(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.arguments: list[str] | None = raw_element.get("arguments")
        self.message: str | None = raw_element.get("message")
        self.message_format: str | None = raw_element.get("messageFormat")
        self.message_format_specifier_types: list[str] | None = raw_element.get(
            "messageFormatSpecifierTypes"
        )
        self.notification_type: str | None = raw_element.get("notificationType")
        self.severity: str | None = raw_element.get("severity")
        self.syntax_position: TokenPosition | None = (
            TokenPosition(raw_element=raw_element.get("syntaxPosition"))
            if raw_element.get("syntaxPosition")
            else None
        )


class Timeframe(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.start: str | None = raw_element.get("start")
        self.end: str | None = raw_element.get("end")


class GeoPoint(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.latitude: float | None = raw_element.get("latitude")
        self.longitude: float | None = raw_element.get("longitude")


class FieldType(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.type: str | None = raw_element.get("type")
        self.types: list[RangedFieldTypes] = [
            RangedFieldTypes(raw_element=element)
            for element in raw_element.get("types", [])
        ]


class RangedFieldTypes(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.index_range: list[int] | None = raw_element.get("indexRange")
        mappings_raw = raw_element.get("mappings") or {}
        self.mappings: dict[str, FieldType] = {
            key: FieldType(raw_element=value) for key, value in mappings_raw.items()
        }


class MetricMetadata(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.description: str | None = raw_element.get("description")
        self.display_name: str | None = raw_element.get("displayName")
        self.field_name: str | None = raw_element.get("fieldName")
        self.metric_key: str | None = raw_element.get("metric.key")
        self.rate: str | None = raw_element.get("rate")
        self.rollup: str | None = raw_element.get("rollup")
        self.scalar: bool | None = raw_element.get("scalar")
        self.shifted: bool | None = raw_element.get("shifted")
        self.unit: str | None = raw_element.get("unit")


class GrailMetadata(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.analysis_timeframe: Timeframe | None = (
            Timeframe(raw_element=raw_element.get("analysisTimeframe"))
            if raw_element.get("analysisTimeframe")
            else None
        )
        self.canonical_query: str | None = raw_element.get("canonicalQuery")
        self.dql_version: str | None = raw_element.get("dqlVersion")
        self.execution_time_milliseconds: int | None = raw_element.get(
            "executionTimeMilliseconds"
        )
        self.locale: str | None = raw_element.get("locale")
        self.notifications: list[MetadataNotification] = [
            MetadataNotification(raw_element=element)
            for element in raw_element.get("notifications", [])
        ]
        self.query: str | None = raw_element.get("query")
        self.query_id: str | None = raw_element.get("queryId")
        self.sampled: bool | None = raw_element.get("sampled")
        self.scanned_bytes: int | None = raw_element.get("scannedBytes")
        self.scanned_data_points: int | None = raw_element.get("scannedDataPoints")
        self.scanned_records: int | None = raw_element.get("scannedRecords")
        self.timezone: str | None = raw_element.get("timezone")


class Metadata(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.grail: GrailMetadata | None = (
            GrailMetadata(raw_element=raw_element.get("grail"))
            if raw_element.get("grail")
            else None
        )
        self.metrics: list[MetricMetadata] = [
            MetricMetadata(raw_element=element)
            for element in raw_element.get("metrics", [])
        ]


class QueryResult(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.metadata: Metadata | None = (
            Metadata(raw_element=raw_element.get("metadata"))
            if raw_element.get("metadata")
            else None
        )
        self.records: list[dict[str, Any]] = raw_element.get("records", [])
        self.types: list[RangedFieldTypes] = [
            RangedFieldTypes(raw_element=element)
            for element in raw_element.get("types", [])
        ]


class QueryStartResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.progress: int | None = raw_element.get("progress")
        self.request_token: str | None = raw_element.get("requestToken")
        self.result: QueryResult | None = (
            QueryResult(raw_element=raw_element.get("result"))
            if raw_element.get("result")
            else None
        )
        self.state: str | None = raw_element.get("state")
        self.ttl_seconds: int | None = raw_element.get("ttlSeconds")


class QueryPollResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.progress: int | None = raw_element.get("progress")
        self.result: QueryResult | None = (
            QueryResult(raw_element=raw_element.get("result"))
            if raw_element.get("result")
            else None
        )
        self.state: str | None = raw_element.get("state")
        self.ttl_seconds: int | None = raw_element.get("ttlSeconds")
