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

import pprint
from typing import Any

from httpx import Response

from dynatrace.http_client import HttpClient


class DynatraceObject:
    def __init__(
        self,
        http_client: HttpClient | None = None,
        headers: dict[str, str] | None = None,
        raw_element: dict[str, Any] | None = None,
    ) -> None:
        if raw_element is None:
            raw_element = {}
        self._http_client = http_client
        self._headers = headers
        self._raw_element = raw_element
        self._create_from_raw_data(raw_element)

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        pass

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({pprint.pformat(self._raw_element, width=130)})"
        )

    def _require_http_client(self) -> HttpClient:
        if self._http_client is None:
            raise RuntimeError(
                f"{self.__class__.__name__} requires an HTTP client to make requests"
            )
        return self._http_client

    async def _make_request(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        method: str = "GET",
        data: Any = None,
        query_params: Any = None,
    ) -> Response:
        return await self._require_http_client().make_request(
            path,
            params=params,
            headers=headers,
            method=method,
            data=data,
            query_params=query_params,
        )

    def json(self) -> dict[str, Any]:
        return self._raw_element
