"""Account platform tokens management API wrappers."""

import builtins
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class AccountPlatformTokensService:
    """
    /iam/v1 Platform tokens management API

    - GET /iam/v1/accounts/{accountUuid}/platform-tokens
    - POST /iam/v1/accounts/{accountUuid}/platform-tokens
    - DELETE /iam/v1/accounts/{accountUuid}/platform-tokens/{platformTokenId}
    - PUT /iam/v1/accounts/{accountUuid}/platform-tokens/{platformTokenId}/expiration-date
    - PUT /iam/v1/accounts/{accountUuid}/platform-tokens/{platformTokenId}/status
    """

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def list(
        self,
        account_uuid: str,
        search_term: str | None = None,
        status: str | None = None,
        page: int | None = None,
        size: int | None = None,
    ) -> "PlatformTokenPage":
        """List all platform tokens within account."""
        params = {}
        if search_term is not None:
            params["searchTerm"] = search_term
        if status is not None:
            params["status"] = status
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size

        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/accounts/{account_uuid}/platform-tokens",
                params=params,
            )
        ).json()
        return PlatformTokenPage(raw_element=resp)

    async def create(
        self,
        account_uuid: str,
        name: str,
        scopes: builtins.list[str],
        expiration_date: str | None = None,
    ) -> "PlatformTokenSecret":
        """Create a new platform token for user."""
        body = {"name": name, "scopes": scopes}
        if expiration_date:
            body["expirationDate"] = expiration_date

        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/accounts/{account_uuid}/platform-tokens",
                method="POST",
                json=body,
            )
        ).json()
        return PlatformTokenSecret(raw_element=resp)

    async def delete(self, account_uuid: str, platform_token_id: str) -> Response:
        """Delete a platform token."""
        return await self.__http_client.make_request(
            f"/iam/v1/accounts/{account_uuid}/platform-tokens/{platform_token_id}",
            method="DELETE",
        )

    async def set_expiration_date(
        self,
        account_uuid: str,
        platform_token_id: str,
        expiration_date: str,
    ) -> Response:
        """Update platform token expiration date."""
        body = {"expirationDate": expiration_date}
        return await self.__http_client.make_request(
            f"/iam/v1/accounts/{account_uuid}/platform-tokens/{platform_token_id}/expiration-date",
            method="PUT",
            json=body,
        )

    async def set_status(
        self,
        account_uuid: str,
        platform_token_id: str,
        status: str,
    ) -> Response:
        """Update platform token status."""
        body = {"status": status}
        return await self.__http_client.make_request(
            f"/iam/v1/accounts/{account_uuid}/platform-tokens/{platform_token_id}/status",
            method="PUT",
            json=body,
        )


# Response models
class PlatformToken(DynatraceObject):
    """Platform token object."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.token_id: str | None = raw_element.get("tokenId")
        self.name: str | None = raw_element.get("name")
        self.status: str | None = raw_element.get("status")
        self.created_by: str | None = raw_element.get("createdBy")
        self.created_at: str | None = raw_element.get("createdAt")
        self.last_used_at: str | None = raw_element.get("lastUsedAt")
        self.expiration_date: str | None = raw_element.get("expirationDate")
        self.scopes: list[str] = raw_element.get("scopes", [])


class PlatformTokenPage(DynatraceObject):
    """Page of platform tokens."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.items: list[PlatformToken] = [
            PlatformToken(raw_element=e) for e in raw_element.get("items", [])
        ]
        self.page_size: int | None = raw_element.get("pageSize")
        self.total_items: int | None = raw_element.get("totalItems")


class PlatformTokenSecret(DynatraceObject):
    """Platform token secret (returned on creation)."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.token_id: str | None = raw_element.get("tokenId")
        self.secret: str | None = raw_element.get("secret")
        self.name: str | None = raw_element.get("name")
        self.scopes: list[str] = raw_element.get("scopes", [])
        self.expiration_date: str | None = raw_element.get("expirationDate")
        self.created_at: str | None = raw_element.get("createdAt")
