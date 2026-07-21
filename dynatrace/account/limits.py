"""Account limits API wrappers."""

import builtins
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


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

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.current_value: float | None = raw_element.get("currentValue")
        self.limit_type: str | None = raw_element.get("limitType")
        self.limit_value: float | None = raw_element.get("limitValue")


class AccountLimitsPage(DynatraceObject):
    """Page of account limits."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.page_size: float | None = raw_element.get("pageSize")
        self.page_number: float | None = raw_element.get("pageNumber")
        self.total: float | None = raw_element.get("total")
        self.results: builtins.list[AccountLimit] = [
            AccountLimit(raw_element=result)
            for result in raw_element.get("results", [])
        ]
