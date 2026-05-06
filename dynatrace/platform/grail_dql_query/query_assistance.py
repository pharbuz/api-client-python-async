"""Grail DQL query assistance API wrappers."""

from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.utils import build_headers

BASE_PATH = "/platform/storage/query/v1"


class QueryAssistanceService:
    ENDPOINT_AUTOCOMPLETE = f"{BASE_PATH}/query:autocomplete"
    ENDPOINT_PARSE = f"{BASE_PATH}/query:parse"
    ENDPOINT_VERIFY = f"{BASE_PATH}/query:verify"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    # Query assistance endpoints.
    async def autocomplete(
        self,
        query: str,
        cursor_position: int | None = None,
        enforce_query_consumption_limit: bool | None = None,
        locale: str | None = None,
        max_data_suggestions: int | None = None,
        query_options: dict[str, str] | None = None,
        timezone: str | None = None,
        dt_client_context: str | None = None,
        enforce_query_consumption_limit_header: bool | None = None,
    ) -> "AutocompleteResponse":
        """Get autocomplete suggestions for a DQL query."""
        headers = build_headers(
            dt_client_context, enforce_query_consumption_limit_header
        )
        body = {
            "query": query,
            "cursorPosition": cursor_position,
            "enforceQueryConsumptionLimit": enforce_query_consumption_limit,
            "locale": locale,
            "maxDataSuggestions": max_data_suggestions,
            "queryOptions": query_options,
            "timezone": timezone,
        }
        response = await self.__http_client.make_request(
            self.ENDPOINT_AUTOCOMPLETE, params=body, headers=headers, method="POST"
        )
        return AutocompleteResponse(
            self.__http_client, response.headers, response.json()
        )

    async def parse(
        self,
        query: str,
        locale: str | None = None,
        query_options: dict[str, str] | None = None,
        timezone: str | None = None,
        dt_client_context: str | None = None,
    ) -> "DQLNode":
        """Parse a DQL query into a canonical query tree."""
        headers = build_headers(dt_client_context, None)
        body = {
            "query": query,
            "locale": locale,
            "queryOptions": query_options,
            "timezone": timezone,
        }
        response = await self.__http_client.make_request(
            self.ENDPOINT_PARSE, params=body, headers=headers, method="POST"
        )
        return DQLNode.from_dict(response.json(), self.__http_client, response.headers)

    async def verify(
        self,
        query: str,
        generate_canonical_query: bool | None = None,
        locale: str | None = None,
        query_options: dict[str, str] | None = None,
        timezone: str | None = None,
        dt_client_context: str | None = None,
    ) -> "VerifyResponse":
        """Verify a DQL query without executing it."""
        headers = build_headers(dt_client_context, None)
        body = {
            "query": query,
            "generateCanonicalQuery": generate_canonical_query,
            "locale": locale,
            "queryOptions": query_options,
            "timezone": timezone,
        }
        response = await self.__http_client.make_request(
            self.ENDPOINT_VERIFY, params=body, headers=headers, method="POST"
        )
        return VerifyResponse(self.__http_client, response.headers, response.json())

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


class VerifyResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.valid: bool | None = raw_element.get("valid")
        self.canonical_query: str | None = raw_element.get("canonicalQuery")
        self.notifications: list[MetadataNotification] = [
            MetadataNotification(raw_element=element)
            for element in raw_element.get("notifications", [])
        ]


class AutocompleteSuggestionPart(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.info: str | None = raw_element.get("info")
        self.suggestion: str | None = raw_element.get("suggestion")
        self.synopsis: str | None = raw_element.get("synopsis")
        self.type: str | None = raw_element.get("type")


class AutocompleteSuggestion(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.already_typed_characters: int | None = raw_element.get(
            "alreadyTypedCharacters"
        )
        self.parts: list[AutocompleteSuggestionPart] = [
            AutocompleteSuggestionPart(raw_element=element)
            for element in raw_element.get("parts", [])
        ]
        self.suggestion: str | None = raw_element.get("suggestion")


class AutocompleteResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.optional: bool | None = raw_element.get("optional")
        self.suggested_ttl_seconds: int | None = raw_element.get("suggestedTtlSeconds")
        self.suggestions: list[AutocompleteSuggestion] = [
            AutocompleteSuggestion(raw_element=element)
            for element in raw_element.get("suggestions", [])
        ]


class DQLNode(DynatraceObject):
    @staticmethod
    def from_dict(
        raw_element: dict[str, Any],
        http_client: HttpClient | None = None,
        headers: dict[str, Any] | None = None,
    ) -> "DQLNode":
        node_type = raw_element.get("nodeType")
        if node_type == "TERMINAL":
            return DQLTerminalNode(
                http_client=http_client, headers=headers, raw_element=raw_element
            )
        if node_type == "CONTAINER":
            return DQLContainerNode(
                http_client=http_client, headers=headers, raw_element=raw_element
            )
        if node_type == "ALTERNATIVE":
            return DQLAlternativeNode(
                http_client=http_client, headers=headers, raw_element=raw_element
            )
        return DQLNode(
            http_client=http_client, headers=headers, raw_element=raw_element
        )

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.is_optional: bool | None = raw_element.get("isOptional")
        self.node_type: str | None = raw_element.get("nodeType")
        self.token_position: TokenPosition | None = (
            TokenPosition(raw_element=raw_element.get("tokenPosition"))
            if raw_element.get("tokenPosition")
            else None
        )


class DQLTerminalNode(DQLNode):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        super()._create_from_raw_data(raw_element)
        self.canonical_string: str | None = raw_element.get("canonicalString")
        self.is_mandatory_on_user_order: bool | None = raw_element.get(
            "isMandatoryOnUserOrder"
        )
        self.type: str | None = raw_element.get("type")


class DQLContainerNode(DQLNode):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        super()._create_from_raw_data(raw_element)
        self.type: str | None = raw_element.get("type")
        self.children: list[DQLNode] = [
            DQLNode.from_dict(child, self._http_client, self._headers)
            for child in raw_element.get("children", [])
        ]


class DQLAlternativeNode(DQLNode):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        super()._create_from_raw_data(raw_element)
        alternatives = raw_element.get("alternatives") or {}
        self.alternatives: dict[str, DQLNode] = {
            key: DQLNode.from_dict(value, self._http_client, self._headers)
            for key, value in alternatives.items()
        }
