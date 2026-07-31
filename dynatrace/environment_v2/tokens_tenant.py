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

from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.utils import raw_optional_object, raw_required_str


class TenantTokenService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def cancel_rotation(self) -> "TenantTokenConfig":
        return TenantTokenConfig(
            raw_element=(
                await self.__http_client.make_request(
                    "/api/v2/tenantTokenRotation/cancel", method="POST"
                )
            ).json()
        )

    async def start_rotation(self) -> "TenantTokenConfig":
        return TenantTokenConfig(
            raw_element=(
                await self.__http_client.make_request(
                    "/api/v2/tenantTokenRotation/start", method="POST"
                )
            ).json()
        )

    async def finish_rotation(self) -> "TenantTokenConfig":
        return TenantTokenConfig(
            raw_element=(
                await self.__http_client.make_request(
                    "/api/v2/tenantTokenRotation/finish", method="POST"
                )
            ).json()
        )


class TenantTokenConfig(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.active: TenantToken | None = raw_optional_object(
            raw_element, "active", lambda value: TenantToken(raw_element=value)
        )
        self.old: TenantToken | None = raw_optional_object(
            raw_element, "old", lambda value: TenantToken(raw_element=value)
        )


class TenantToken(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.value: str = raw_required_str(raw_element, "value")
