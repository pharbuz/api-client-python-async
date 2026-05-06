"""High-level platform API aggregators."""

from dynatrace.http_client import HttpClient
from dynatrace.platform.appengine.registry import AppEngineRegistryService
from dynatrace.platform.davis.analyzers import AnalyzerService
from dynatrace.platform.davis_copilot.copilot_service import CopilotService
from dynatrace.platform.grail_dql_query.query_assistance import (
    QueryAssistanceService,
)
from dynatrace.platform.grail_dql_query.query_execution import QueryExecutionService


class PlatformAPI:
    def __init__(self, http_client: HttpClient) -> None:
        # AppEngine platform APIs.
        self.appengine_registry: AppEngineRegistryService = AppEngineRegistryService(
            http_client
        )

        # Davis platform APIs.
        self.davis_analyzers: AnalyzerService = AnalyzerService(http_client)
        self.davis_copilot: CopilotService = CopilotService(http_client)

        # Grail query APIs.
        self.grail_query_assistance: QueryAssistanceService = QueryAssistanceService(
            http_client
        )
        self.grail_query_execution: QueryExecutionService = QueryExecutionService(
            http_client
        )
