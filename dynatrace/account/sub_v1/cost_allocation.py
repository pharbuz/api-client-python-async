"""Subscription cost allocation API wrappers."""

from enum import Enum
from typing import Any, Union

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class CostAllocationService:
    """/v1/subscriptions/{subscription-uuid}/cost-allocation API"""

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    # Cost allocation endpoint.
    async def get(
        self,
        subscription_uuid: str,
        field: Union[str, "CostAllocationField"] | None = None,
        environment_id: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        page_size: int | None = None,
        page_key: str | None = None,
    ) -> "CostAllocationResponse":
        params: dict[str, Any] = {}
        if page_key:
            params["page-key"] = page_key
        else:
            if field:
                params["field"] = (
                    field.value if isinstance(field, CostAllocationField) else field
                )
            if environment_id:
                params["environment-id"] = environment_id
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date
            if page_size is not None:
                params["page-size"] = page_size

        resp = (
            await self.__http_client.make_request(
                f"/v1/subscriptions/{subscription_uuid}/cost-allocation",
                params=params,
                # Response models.
            )
        ).json()
        return CostAllocationResponse(raw_element=resp)


class CostAllocationResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.environment_id: str | None = raw_element.get("environmentId")
        self.field: str | None = raw_element.get("field")
        self.records = raw_element.get("records", [])
        self.next_page_key: str | None = raw_element.get("nextPageKey")


class CostAllocationField(Enum):
    """
    Allowed values for the `field` query parameter in
    /v1/subscriptions/{subscription-uuid}/cost-allocation

    According to spec: Allowed values are `COSTCENTER`, `PRODUCT`.
    """

    COSTCENTER = "COSTCENTER"
    PRODUCT = "PRODUCT"
