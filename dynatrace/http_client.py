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

import asyncio
import json
import logging
from typing import Any

import httpx

from dynatrace.auth import build_dynatrace_oauth_client

TOO_MANY_REQUESTS_WAIT = "wait"


class HttpClient:
    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        account_uuid: str,
        log: logging.Logger = None,
        proxies: dict[str, str] | None = None,
        too_many_requests_strategy=None,
        retries: int = 0,
        retry_delay_ms: int = 0,
        mc_jsession_id: str | None = None,
        mc_b925d32c: str | None = None,
        mc_sso_csrf_cookie: str | None = None,
        print_bodies: bool = False,
        timeout: int | None = None,
        headers: dict[str, str] | None = None,
        scope: str = "account-uac-read",
        sso_base_url: str = "https://sso.dynatrace.com",
        verify_ssl: bool = False,
        token_timeout: int = 30,
        follow_redirects: bool = True,
    ):
        while base_url.endswith("/"):
            base_url = base_url[:-1]
        self.base_url = base_url

        self.headers = headers.copy() if headers else {}
        self.proxies = proxies or {}
        self.auth_header: dict[str, str] = {}
        self.print_bodies = print_bodies
        self.too_many_requests_strategy = too_many_requests_strategy
        self.timeout = timeout
        self.retries = retries
        self.retry_delay_s = retry_delay_ms / 1000
        self.verify = verify_ssl
        self.follow_redirects = follow_redirects
        self.scope = scope
        self.sso_base_url = sso_base_url
        self.token_timeout = token_timeout
        self.client_id = client_id
        self.client_secret = client_secret
        self.account_uuid = account_uuid

        self.log = log
        if self.log is None:
            self.log = logging.getLogger(__name__)
            self.log.setLevel(logging.WARNING)
            st = logging.StreamHandler()
            fmt = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(thread)d - "
                "%(filename)s:%(lineno)d - %(message)s"
            )
            st.setFormatter(fmt)
            self.log.addHandler(st)

        # Internal Dynatrace cookies
        self.mc_jsession_id = mc_jsession_id
        self.mc_b925d32c = mc_b925d32c
        self.mc_sso_csrf_cookie = mc_sso_csrf_cookie

        self.client = self._create_client()

    async def aclose(self) -> None:
        await self.client.aclose()

    async def __aenter__(self) -> "HttpClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    def _build_headers(
        self, headers: dict[str, str] | None, files: Any
    ) -> dict[str, str]:
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        if files is None and "content-type" not in {
            key.lower() for key in request_headers.keys()
        }:
            request_headers["content-type"] = "application/json"

        request_headers.update(self.auth_header)

        if self.mc_b925d32c and self.mc_sso_csrf_cookie and self.mc_jsession_id:
            request_headers["Cookie"] = (
                f"JSESSIONID={self.mc_jsession_id}; "
                f"ssoCSRFCookie={self.mc_sso_csrf_cookie}; "
                f"b925d32c={self.mc_b925d32c}"
            )

        return request_headers

    def _build_cookies(self) -> dict[str, str] | None:
        if self.mc_b925d32c and self.mc_sso_csrf_cookie and self.mc_jsession_id:
            return {
                "JSESSIONID": self.mc_jsession_id,
                "ssoCSRFCookie": self.mc_sso_csrf_cookie,
                "b925d32c": self.mc_b925d32c,
            }
        return None

    @staticmethod
    def _sanitize_params(params: Any) -> Any:
        if isinstance(params, dict):
            return {key: value for key, value in params.items() if value is not None}
        return params

    def _build_mounts(self) -> dict[str, httpx.AsyncBaseTransport]:
        mounts = {}
        for scheme in ("http", "https"):
            proxy = self.proxies.get(scheme)
            if proxy:
                mounts[f"{scheme}://"] = httpx.AsyncHTTPTransport(
                    proxy=proxy,
                    verify=self.verify,
                    retries=0,
                )
        return mounts

    def _create_client(self):
        mounts = self._build_mounts()
        return build_dynatrace_oauth_client(
            sso_base_url=self.sso_base_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            account_uuid=self.account_uuid,
            scope=self.scope,
            verify_ssl=self.verify,
            token_timeout=self.token_timeout,
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
            mounts=mounts or None,
            transport=httpx.AsyncHTTPTransport(
                verify=self.verify,
                retries=0,
            ),
        )

    def _get_client(self, url: str) -> httpx.AsyncClient:
        return self.client

    @staticmethod
    def _format_response(response: httpx.Response) -> str:
        return f"<Response [{response.status_code}]>"

    async def _request_with_retries(
        self,
        method: str,
        url: str,
        request_headers: dict[str, str],
        request_params: Any,
        body: Any,
        data: Any,
        files: Any,
        cookies: dict[str, str] | None,
    ) -> httpx.Response:
        status_forcelist = {400, 401, 403, 404, 413, 429, 500, 502, 503, 504}
        client = self._get_client(url)
        last_exception: Exception | None = None

        for attempt in range(self.retries + 1):
            try:
                response = await client.request(
                    method,
                    url,
                    headers=request_headers,
                    params=request_params,
                    json=body,
                    data=data,
                    cookies=cookies,
                    files=files,
                )
                self.log.debug("Received response '%s'", response)

                if response.status_code in status_forcelist and attempt < self.retries:
                    if self.retry_delay_s > 0:
                        await asyncio.sleep(self.retry_delay_s)
                    continue

                return response
            except httpx.RequestError as exc:
                last_exception = exc
                if attempt < self.retries:
                    if self.retry_delay_s > 0:
                        await asyncio.sleep(self.retry_delay_s)
                    continue
                raise exc

        if last_exception is not None:
            raise last_exception

        raise RuntimeError("Request retry loop ended unexpectedly")

    async def make_request(
        self,
        path: str,
        params: Any | None = None,
        headers: dict[str, str] | None = None,
        method: str = "GET",
        data: Any = None,
        files: Any = None,
        query_params: Any = None,
    ) -> httpx.Response:
        url = f"{self.base_url}{path}"

        body = None
        request_params = self._sanitize_params(params)

        if method in ["POST", "PUT"]:
            body = params
            request_params = self._sanitize_params(query_params)

        request_headers = self._build_headers(headers=headers, files=files)
        cookies = self._build_cookies()

        self.log.debug(
            "Making %s request to '%s' with params %s and body: %s",
            method,
            url,
            request_params,
            body,
        )

        if self.print_bodies:
            print(method, url)
            if body:
                print(json.dumps(body, indent=2))

        try:
            response = await self._request_with_retries(
                method=method,
                url=url,
                request_headers=request_headers,
                request_params=request_params,
                body=body,
                data=data,
                files=files,
                cookies=cookies,
            )
        except httpx.RequestError as exc:
            raise Exception(f"Error making request to {url}: {exc}") from exc

        while (
            response.status_code == 429
            and self.too_many_requests_strategy == TOO_MANY_REQUESTS_WAIT
        ):
            sleep_amount = int(response.headers.get("retry-after", 5))
            self.log.warning(
                "Sleeping for %ss because we have received an HTTP 429",
                sleep_amount,
            )
            await asyncio.sleep(sleep_amount)
            try:
                response = await self._request_with_retries(
                    method=method,
                    url=url,
                    request_headers=request_headers,
                    request_params=request_params,
                    body=body,
                    data=None,
                    files=None,
                    cookies=None,
                )
            except httpx.RequestError as exc:
                raise Exception(f"Error making request to {url}: {exc}") from exc

        if response.status_code >= 400:
            raise Exception(
                f"Error making request to {url}: {self._format_response(response)}. "
                f"Response: {response.text}"
            )

        return response
