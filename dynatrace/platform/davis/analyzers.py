"""Davis analyzer execution API wrappers."""

from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class AnalyzerService:
    """
    /platform/davis/analyzers/v1 Analyzers API

    - POST /platform/davis/analyzers/v1/analyzers/{analyzer-name}:execute
    """

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    # Analyzer execution endpoints.
    async def execute(
        self,
        analyzer_name: str,
        payload: dict[str, Any],
        timeout_seconds: int | None = None,
        enable_preview: bool | None = None,
    ) -> "AnalyzerExecuteResult":
        query_params: dict[str, Any] = {}
        if timeout_seconds is not None:
            query_params["timeout-seconds"] = timeout_seconds
        if enable_preview is not None:
            query_params["enable-preview"] = str(enable_preview).lower()

        resp = (
            await self.__http_client.make_request(
                f"/platform/davis/analyzers/v1/analyzers/{analyzer_name}:execute",
                # Execution result models.
                method="POST",
                params=payload,
                query_params=query_params,
            )
        ).json()
        return AnalyzerExecuteResult(raw_element=resp)

    async def poll(
        self,
        analyzer_name: str,
        request_token: str,
        timeout_seconds: int | None = None,
    ) -> "AnalyzerPollResult":
        query_params: dict[str, Any] = {"request-token": request_token}
        if timeout_seconds is not None:
            query_params["timeout-seconds"] = timeout_seconds

        resp = (
            await self.__http_client.make_request(
                f"/platform/davis/analyzers/v1/analyzers/{analyzer_name}:poll",
                method="GET",
                params=query_params,
            )
        ).json()
        return AnalyzerPollResult(raw_element=resp)


class AnalyzerExecuteResult(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.request_token: str | None = raw_element.get("requestToken")
        self.ttl_in_seconds: int | None = raw_element.get("ttlInSeconds")
        result_raw = raw_element.get("result")
        self.result: AnalyzerResult | None = (
            AnalyzerResult(raw_element=result_raw)
            if isinstance(result_raw, dict)
            else None
        )


class AnalyzerPollResult(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.request_token: str | None = raw_element.get("requestToken")
        self.ttl_in_seconds: int | None = raw_element.get("ttlInSeconds")
        result_raw = raw_element.get("result")
        self.result: AnalyzerResult | None = (
            AnalyzerResult(raw_element=result_raw)
            if isinstance(result_raw, dict)
            else None
        )


# Nested analyzer payload models.
class AnalyzerResult(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.result_id: str | None = raw_element.get("resultId")
        self.result_status: str | None = raw_element.get("resultStatus")
        self.execution_status: str | None = raw_element.get("executionStatus")
        input_raw = raw_element.get("input")
        self.input: AnalyzerInput | None = (
            AnalyzerInput(raw_element=input_raw)
            if isinstance(input_raw, dict)
            else None
        )
        self.logs: list[AnalyzerExecutionLog] = [
            AnalyzerExecutionLog(raw_element=e)
            for e in (raw_element.get("logs") or [])
            if isinstance(e, dict)
        ]
        self.output: list[AnalyzerOutput] = [
            AnalyzerOutput(raw_element=e)
            for e in (raw_element.get("output") or [])
            if isinstance(e, dict)
        ]
        self.data: list[AnalyzerDimensionalData] = [
            AnalyzerDimensionalData(raw_element=e)
            for e in (raw_element.get("data") or [])
            if isinstance(e, dict)
        ]


class AnalyzerInput(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        general_raw = raw_element.get("generalParameters") or {}
        self.general_parameters: AnalyzerGeneralParameters | None = (
            AnalyzerGeneralParameters(raw_element=general_raw)
            if isinstance(general_raw, dict)
            else None
        )
        self.parameters: dict[str, Any] = {
            k: v for k, v in raw_element.items() if k != "generalParameters"
        }


class AnalyzerGeneralParameters(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        timeframe_raw = raw_element.get("timeframe")
        self.timeframe: Timeframe | None = (
            Timeframe(raw_element=timeframe_raw)
            if isinstance(timeframe_raw, dict)
            else None
        )
        self.resolve_dimensional_query_data: bool | None = raw_element.get(
            "resolveDimensionalQueryData"
        )
        self.log_verbosity: str | None = raw_element.get("logVerbosity")


class Timeframe(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.start_time: str | None = raw_element.get("startTime")
        self.end_time: str | None = raw_element.get("endTime")


class AnalyzerExecutionLog(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.level: str | None = raw_element.get("level")
        self.message: str | None = raw_element.get("message")
        self.path: str | None = raw_element.get("path")


class AnalyzerOutput(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        system_raw = raw_element.get("system")
        self.system: AnalyzerOutputSystemParameters | None = (
            AnalyzerOutputSystemParameters(raw_element=system_raw)
            if isinstance(system_raw, dict)
            else None
        )
        self.value: dict[str, Any] | None = raw_element.get("value")


class AnalyzerOutputSystemParameters(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.logs: list[AnalyzerOutputLog] = [
            AnalyzerOutputLog(raw_element=e)
            for e in (raw_element.get("logs") or [])
            if isinstance(e, dict)
        ]


class AnalyzerOutputLog(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.level: str | None = raw_element.get("level")
        self.message: str | None = raw_element.get("message")


class AnalyzerDimensionalData(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        query_raw = raw_element.get("query")
        self.query: AnalyzerDimensionalQuery | None = (
            AnalyzerDimensionalQuery(raw_element=query_raw)
            if isinstance(query_raw, dict)
            else None
        )
        self.value: dict[str, Any] | None = raw_element.get("value")
        self.type: str | None = raw_element.get("type")


class AnalyzerDimensionalQuery(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.expression: str | None = raw_element.get("expression")
        timeframe_raw = raw_element.get("timeframe")
        self.timeframe: Timeframe | None = (
            Timeframe(raw_element=timeframe_raw)
            if isinstance(timeframe_raw, dict)
            else None
        )
        self.id: str | None = raw_element.get("id")
        self.ref_id: str | None = raw_element.get("refId")
