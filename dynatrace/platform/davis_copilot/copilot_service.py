from __future__ import annotations

from enum import Enum
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class CopilotService:
    """Client wrapper for the Davis CoPilot preview API."""

    BASE_PATH = "/platform/davis/copilot/v1"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list_skills(self) -> AvailableSkillsResponse:
        """Return all skills available to the current token."""
        response = await self.__http_client.make_request(f"{self.BASE_PATH}/skills")
        return AvailableSkillsResponse(
            self.__http_client, response.headers, response.json()
        )

    async def send_conversation_message(
        self,
        payload: dict[str, Any] | DynatraceObject,
        accept: str | None = "application/json",
        raw_response: bool = False,
    ) -> RecommenderResponse | Response:
        """Send a message to the recommender skill.

        When `accept` is set to ``application/x-ndjson`` or `raw_response` is True, the raw HTTP
        response is returned
        to allow the caller to handle streaming tokens manually.
        """
        body = self.__normalize_payload(payload)
        headers = {"Accept": accept} if accept else {}
        response = await self.__http_client.make_request(
            f"{self.BASE_PATH}/skills/conversations:message",
            params=body,
            method="POST",
            headers=headers,
        )

        if raw_response or (accept and accept.lower() == "application/x-ndjson"):
            return response

        return RecommenderResponse(
            self.__http_client, response.headers, response.json()
        )

    async def submit_conversation_feedback(
        self, payload: dict[str, Any] | DynatraceObject
    ) -> Response:
        """Submit feedback for a recommender conversation."""
        body = self.__normalize_payload(payload)
        return await self.__http_client.make_request(
            f"{self.BASE_PATH}/skills/conversations:feedback",
            params=body,
            method="POST",
        )

    async def document_search(
        self, payload: dict[str, Any] | DynatraceObject
    ) -> DocumentSearchResponse:
        """Execute a document search request."""
        body = self.__normalize_payload(payload)
        response = await self.__http_client.make_request(
            f"{self.BASE_PATH}/skills/document-search:execute",
            params=body,
            method="POST",
        )
        return DocumentSearchResponse(
            self.__http_client, response.headers, response.json()
        )

    async def explain_dql_query(
        self, payload: dict[str, Any] | DynatraceObject
    ) -> Dql2NlResponse:
        """Explain a DQL query via the dql2nl skill."""
        body = self.__normalize_payload(payload)
        response = await self.__http_client.make_request(
            f"{self.BASE_PATH}/skills/dql2nl:explain",
            params=body,
            method="POST",
        )
        return Dql2NlResponse(self.__http_client, response.headers, response.json())

    async def submit_dql2nl_feedback(
        self, payload: dict[str, Any] | DynatraceObject
    ) -> Response:
        """Submit feedback for a dql2nl response."""
        body = self.__normalize_payload(payload)
        return await self.__http_client.make_request(
            f"{self.BASE_PATH}/skills/dql2nl:feedback",
            params=body,
            method="POST",
        )

    async def generate_dql_query(
        self, payload: dict[str, Any] | DynatraceObject
    ) -> Nl2DqlResponse:
        """Generate a DQL query from natural language via the nl2dql skill."""
        body = self.__normalize_payload(payload)
        response = await self.__http_client.make_request(
            f"{self.BASE_PATH}/skills/nl2dql:generate",
            params=body,
            method="POST",
        )
        return Nl2DqlResponse(self.__http_client, response.headers, response.json())

    async def submit_nl2dql_feedback(
        self, payload: dict[str, Any] | DynatraceObject
    ) -> Response:
        """Submit feedback for an nl2dql response."""
        body = self.__normalize_payload(payload)
        return await self.__http_client.make_request(
            f"{self.BASE_PATH}/skills/nl2dql:feedback",
            params=body,
            method="POST",
        )

    @staticmethod
    def __normalize_payload(
        payload: dict[str, Any] | DynatraceObject | None,
    ) -> dict[str, Any] | None:
        if payload is None:
            return None
        if isinstance(payload, DynatraceObject):
            return payload.json()
        if hasattr(payload, "to_json") and callable(
            getattr(payload, "to_json")  # noqa: B009
        ):
            return payload.to_json()
        return payload


class SkillType(Enum):
    CONVERSATION = "conversation"
    NL2DQL = "nl2dql"
    DQL2NL = "dql2nl"
    DOCUMENT_SEARCH = "documentSearch"

    def __str__(self) -> str:
        return self.value


class Status(Enum):
    SUCCESSFUL = "SUCCESSFUL"
    SUCCESSFUL_WITH_WARNINGS = "SUCCESSFUL_WITH_WARNINGS"
    FAILED = "FAILED"

    def __str__(self) -> str:
        return self.value


class AvailableSkillsResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        raw_skills = raw_element.get("skills") or []
        self.skills: list[SkillType] = [SkillType(skill) for skill in raw_skills]


class Notification(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.severity: str | None = raw_element.get("severity")
        self.notification_type: str | None = raw_element.get("notificationType")
        self.message: str | None = raw_element.get("message")


class SourceDocument(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.title: str | None = raw_element.get("title")
        self.url: str | None = raw_element.get("url")
        self.type: str | None = raw_element.get("type")


class Metadata(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        notifications_raw = raw_element.get("notifications") or []
        self.notifications: list[Notification] = [
            Notification(raw_element=notification) for notification in notifications_raw
        ]


class MetadataWithSource(Metadata):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        super()._create_from_raw_data(raw_element or {})
        sources_raw = (raw_element or {}).get("sources") or []
        self.sources: list[SourceDocument] = [
            SourceDocument(raw_element=source) for source in sources_raw
        ]


class ConversationHistoryItem(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.role: str | None = raw_element.get("role")
        self.text: str | None = raw_element.get("text")
        self.supplementary: str | None = raw_element.get("supplementary")


class State(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.version: str | None = raw_element.get("version")
        self.conversation_id: str | None = raw_element.get("conversationId")
        self.skill_name: str | None = raw_element.get("skillName")
        history_raw = raw_element.get("history") or []
        self.history: list[ConversationHistoryItem] = [
            ConversationHistoryItem(raw_element=item) for item in history_raw
        ]


class ConversationResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.text: str | None = raw_element.get("text")
        self.message_token: str | None = raw_element.get("messageToken")
        status = raw_element.get("status")
        self.status: Status | None = Status(status) if status else None
        metadata_raw = raw_element.get("metadata") or {}
        self.metadata: MetadataWithSource = (
            MetadataWithSource(raw_element=metadata_raw)
            if metadata_raw
            else MetadataWithSource(raw_element={})
        )
        state_raw = raw_element.get("state") or {}
        self.state: State = (
            State(raw_element=state_raw) if state_raw else State(raw_element={})
        )


class RecommenderResponse(ConversationResponse):
    """Wrapper for the non-streaming recommender response."""


class DocumentMetadata(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.id: str | None = raw_element.get("id")
        self.external_id: str | None = raw_element.get("externalId")
        self.name: str | None = raw_element.get("name")
        self.type: str | None = raw_element.get("type")
        self.description: str | None = raw_element.get("description")
        self.version: str | None = raw_element.get("version")


class ScoredDocument(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.document_id: str | None = raw_element.get("documentId")
        self.relevance_score: float | None = raw_element.get("relevanceScore")
        metadata_raw = raw_element.get("documentMetadata") or {}
        self.document_metadata: DocumentMetadata | None = (
            DocumentMetadata(raw_element=metadata_raw) if metadata_raw else None
        )


class DocumentSearchResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.message_token: str | None = raw_element.get("messageToken")
        status = raw_element.get("status")
        self.status: Status | None = Status(status) if status else None
        results_raw = raw_element.get("results") or []
        self.results: list[ScoredDocument] = [
            ScoredDocument(raw_element=result) for result in results_raw
        ]


class Nl2DqlResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.dql: str | None = raw_element.get("dql")
        self.message_token: str | None = raw_element.get("messageToken")
        status = raw_element.get("status")
        self.status: Status | None = Status(status) if status else None
        metadata_raw = raw_element.get("metadata") or {}
        self.metadata: Metadata | None = (
            Metadata(raw_element=metadata_raw) if metadata_raw else None
        )


class Dql2NlResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.summary: str | None = raw_element.get("summary")
        self.explanation: str | None = raw_element.get("explanation")
        self.message_token: str | None = raw_element.get("messageToken")
        status = raw_element.get("status")
        self.status: Status | None = Status(status) if status else None
        metadata_raw = raw_element.get("metadata") or {}
        self.metadata: Metadata | None = (
            Metadata(raw_element=metadata_raw) if metadata_raw else None
        )
