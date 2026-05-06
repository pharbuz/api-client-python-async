from authlib.integrations.base_client import InvalidTokenError, TokenExpiredError
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.integrations.httpx_client.oauth2_client import USE_CLIENT_DEFAULT


class AutoRefreshingOAuth2Client(AsyncOAuth2Client):
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
        kwargs.setdefault("token_endpoint", token_url)
        kwargs.setdefault("grant_type", "client_credentials")
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            **kwargs,
        )
        self._token_url = token_url
        self._scope = scope
        self._resource = resource
        self._token_timeout = token_timeout

    async def _refetch_token(self):
        return await self.fetch_token(
            url=self._token_url,
            grant_type="client_credentials",
            scope=self._scope,
            resource=self._resource,
            include_client_id=True,
            timeout=self._token_timeout,
        )

    async def ensure_active_token(self, token):
        if self.metadata.get("grant_type") != "client_credentials":
            return await super().ensure_active_token(token)

        async with self._token_refresh_lock:
            if token.is_expired(leeway=self.leeway):
                await self._refetch_token()

    async def request(
        self, method, url, withhold_token=False, auth=USE_CLIENT_DEFAULT, **kwargs
    ):
        manage_token = not withhold_token and auth is USE_CLIENT_DEFAULT

        if manage_token and not self.token:
            await self._refetch_token()

        try:
            response = await super().request(
                method,
                url,
                withhold_token=withhold_token,
                auth=auth,
                **kwargs,
            )
        except (TokenExpiredError, InvalidTokenError):
            if not manage_token:
                raise
            await self._refetch_token()
            response = await super().request(
                method,
                url,
                withhold_token=withhold_token,
                auth=auth,
                **kwargs,
            )
        else:
            if manage_token and response.status_code == 401:
                await self._refetch_token()
                response = await super().request(
                    method,
                    url,
                    withhold_token=withhold_token,
                    auth=auth,
                    **kwargs,
                )

        return response


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
) -> AutoRefreshingOAuth2Client:
    token_url = f"{sso_base_url.rstrip('/')}/sso/oauth2/token"
    resource = f"urn:dtaccount:{account_uuid}"
    return AutoRefreshingOAuth2Client(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope or "account-uac-read",
        resource=resource,
        verify_ssl=verify_ssl,
        token_timeout=token_timeout,
        **kwargs,
    )
