import asyncio
import time
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class DynatraceOAuthCredentials:
    client_id: str
    client_secret: str
    account_uuid: str
    scope: str = "account-uac-read"
    sso_base_url: str = "https://sso.dynatrace.com"


@dataclass(frozen=True)
class DynatraceAccessToken:
    token: str


class DynatraceOAuthClient(httpx.AsyncClient):
    def __init__(
        self,
        *,
        token_url: str,
        client_id: str,
        client_secret: str,
        scope: str,
        resource: str,
        verify_ssl: bool,
        token_timeout: int = 30,
        **kwargs,
    ):
        kwargs.setdefault("verify", verify_ssl)
        super().__init__(**kwargs)
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._scope = scope
        self._resource = resource
        self._token_timeout = token_timeout
        self._token: dict[str, Any] | None = None
        self._token_refresh_lock = asyncio.Lock()

    async def _refetch_token(self):
        response = await super().request(
            "POST",
            self._token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": self._scope,
                "resource": self._resource,
            },
            timeout=self._token_timeout,
        )
        response.raise_for_status()

        token = response.json()
        if "access_token" not in token:
            raise RuntimeError("OAuth token response does not contain access_token")
        if "expires_at" not in token and "expires_in" in token:
            token["expires_at"] = time.time() + int(token["expires_in"])

        self._token = token
        return token

    def _token_is_expired(self, token: dict[str, Any], leeway: int = 60) -> bool:
        expires_at = token.get("expires_at")
        if expires_at is None:
            return False
        return float(expires_at) <= time.time() + leeway

    async def _ensure_active_token(self) -> None:
        async with self._token_refresh_lock:
            if self._token is None or self._token_is_expired(self._token):
                await self._refetch_token()

    async def request(
        self,
        method: str,
        url: httpx.URL | str,
        *,
        withhold_token: bool = False,
        auth: (
            httpx.AuthTypes | httpx.UseClientDefault | None
        ) = httpx.USE_CLIENT_DEFAULT,
        **kwargs,
    ):
        manage_token = not withhold_token and auth is httpx.USE_CLIENT_DEFAULT

        if manage_token:
            await self._ensure_active_token()
            headers = httpx.Headers(kwargs.pop("headers", None))
            headers["Authorization"] = f"Bearer {self._token['access_token']}"
            kwargs["headers"] = headers

        response = await super().request(method, url, auth=auth, **kwargs)
        if manage_token and response.status_code == 401:
            await self._refetch_token()
            headers = httpx.Headers(kwargs.pop("headers", None))
            headers["Authorization"] = f"Bearer {self._token['access_token']}"
            kwargs["headers"] = headers
            response = await super().request(method, url, auth=auth, **kwargs)

        return response


AutoRefreshingOAuth2Client = DynatraceOAuthClient


def build_dynatrace_oauth_client(
    *,
    sso_base_url: str,
    client_id: str,
    client_secret: str,
    account_uuid: str,
    scope: str = "account-uac-read",
    verify_ssl: bool = False,
    token_timeout: int = 30,
    **kwargs,
) -> DynatraceOAuthClient:
    token_url = f"{sso_base_url.rstrip('/')}/sso/oauth2/token"
    resource = f"urn:dtaccount:{account_uuid}"
    return DynatraceOAuthClient(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope or "account-uac-read",
        resource=resource,
        verify_ssl=verify_ssl,
        token_timeout=token_timeout,
        **kwargs,
    )
