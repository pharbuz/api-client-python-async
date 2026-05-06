"""Subscription rate card API wrappers."""

from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class RateCardService:
    """/sub/v1 Rate-cards API"""

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    # Rate card listing endpoint.
    async def list(self, account_uuid: str) -> list["RateCard"]:
        resp = (
            await self.__http_client.make_request(
                f"/sub/v1/accounts/{account_uuid}/rate-cards"
            )
        ).json()
        return [RateCard(raw_element=e) for e in resp]


class RateCardCapability(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        # Response models.
        self.key: str | None = raw_element.get("key")
        self.name: str | None = raw_element.get("name")
        self.quoted_price: str | None = raw_element.get("quotedPrice")
        self.quoted_unit_of_measure: str | None = raw_element.get("quotedUnitOfMeasure")
        self.price: str | None = raw_element.get("price")


class RateCard(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.quote_number: str | None = raw_element.get("quoteNumber")
        self.start_time: str | None = raw_element.get("startTime")
        self.end_time: str | None = raw_element.get("endTime")
        self.currency_code: str | None = raw_element.get("currencyCode")
        self.capabilities: list[RateCardCapability] = [
            RateCardCapability(raw_element=c)
            for c in raw_element.get("capabilities", [])
        ]
