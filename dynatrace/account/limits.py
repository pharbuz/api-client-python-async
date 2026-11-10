"""Account limits API wrappers."""

import builtins
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.utils import (
    raw_optional_float,
    raw_optional_int,
    raw_optional_object_list,
    raw_optional_str,
)


class AccountLimitsService:
    """/iam/v1 Account limits API."""

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def list(self, account_uuid: str) -> "AccountLimitsPage":
        """Returns limits defined for an account."""
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/accounts/{account_uuid}/limits"
            )
        ).json()
        return AccountLimitsPage(raw_element=resp)


class AccountLimit(DynatraceObject):
    """Account limit entry."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.current_value: float | None = raw_optional_float(
            raw_element, "currentValue"
        )
        self.limit_type: str | None = raw_optional_str(raw_element, "limitType")
        self.limit_value: float | None = raw_optional_float(raw_element, "limitValue")


class AccountLimitsPage(DynatraceObject):
    """Page of account limits."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.page_size: int | None = raw_optional_int(raw_element, "pageSize")
        self.page_number: int | None = raw_optional_int(raw_element, "pageNumber")
        self.total: int | None = raw_optional_int(raw_element, "total")
        self.results: builtins.list[AccountLimit] = (
            raw_optional_object_list(
                raw_element,
                "results",
                lambda value: AccountLimit(raw_element=value),
            )
            or []
        )
