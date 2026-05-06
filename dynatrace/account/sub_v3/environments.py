"""Subscription by environment API v3 wrappers."""

from datetime import datetime
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.utils import timestamp_to_string


class SubscriptionEnvironmentService:
    """
    /sub/v3 Subscriptions by Environment API

    - GET /sub/v3/accounts/{accountUuid}/subscriptions/{subscriptionUuid}/environments/cost
    - GET /sub/v3/accounts/{accountUuid}/subscriptions/{subscriptionUuid}/environments/usage
    """

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    # Environment cost and usage endpoints.
    async def cost(
        self,
        account_uuid: str,
        subscription_uuid: str,
        start_time: str | datetime,
        end_time: str | datetime,
        environment_ids: list[str] | None = None,
        capability_keys: list[str] | None = None,
        cluster_ids: list[str] | None = None,
        page_key: str | None = None,
        page_size: int | None = None,
    ) -> "EnvironmentCostResponse":
        params: dict[str, Any] = {
            "startTime": timestamp_to_string(start_time),
            "endTime": timestamp_to_string(end_time),
        }
        if environment_ids:
            params["environmentIds"] = environment_ids
        if capability_keys:
            # Response models.
            params["capabilityKeys"] = capability_keys
        if cluster_ids:
            params["clusterIds"] = cluster_ids
        if page_key:
            params["page-key"] = page_key
        if page_size is not None:
            params["page-size"] = page_size

        resp = (
            await self.__http_client.make_request(
                f"/sub/v3/accounts/{account_uuid}/subscriptions/{subscription_uuid}/environments/cost",
                params=params,
            )
        ).json()
        return EnvironmentCostResponse(raw_element=resp)

    async def usage(
        self,
        account_uuid: str,
        subscription_uuid: str,
        start_time: str | datetime,
        end_time: str | datetime,
        environment_ids: list[str] | None = None,
        capability_keys: list[str] | None = None,
        cluster_ids: list[str] | None = None,
        page_key: str | None = None,
        page_size: int | None = None,
    ) -> "EnvironmentUsageResponse":
        params: dict[str, Any] = {
            "startTime": timestamp_to_string(start_time),
            "endTime": timestamp_to_string(end_time),
        }
        if environment_ids:
            params["environmentIds"] = environment_ids
        if capability_keys:
            params["capabilityKeys"] = capability_keys
        if cluster_ids:
            params["clusterIds"] = cluster_ids
        if page_key:
            params["page-key"] = page_key
        if page_size is not None:
            params["page-size"] = page_size

        resp = (
            await self.__http_client.make_request(
                f"/sub/v3/accounts/{account_uuid}/subscriptions/{subscription_uuid}/environments/usage",
                params=params,
            )
        ).json()
        return EnvironmentUsageResponse(raw_element=resp)


class EnvironmentCostEntry(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.start_time: str | None = raw_element.get("startTime")
        self.end_time: str | None = raw_element.get("endTime")
        self.value: float | None = raw_element.get("value")
        self.currency_code: str | None = raw_element.get("currencyCode")
        self.capability_key: str | None = raw_element.get("capabilityKey")
        self.capability_name: str | None = raw_element.get("capabilityName")
        self.booking_date: str | None = raw_element.get("bookingDate")


class EnvironmentCost(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.cluster_id: str | None = raw_element.get("clusterId")
        self.environment_id: str | None = raw_element.get("environmentId")
        self.cost: list[EnvironmentCostEntry] = [
            EnvironmentCostEntry(raw_element=e) for e in raw_element.get("cost", [])
        ]


class EnvironmentCostResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.data: list[EnvironmentCost] = [
            EnvironmentCost(raw_element=e) for e in raw_element.get("data", [])
        ]
        self.last_modified_time: str | None = raw_element.get("lastModifiedTime")
        self.next_page_key: str | None = raw_element.get("nextPageKey")


class EnvironmentUsageEntry(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.capability_key: str | None = raw_element.get("capabilityKey")
        self.capability_name: str | None = raw_element.get("capabilityName")
        self.start_time: str | None = raw_element.get("startTime")
        self.end_time: str | None = raw_element.get("endTime")
        self.value: float | None = raw_element.get("value")
        self.unit_measure: str | None = raw_element.get("unitMeasure")


class EnvironmentUsage(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.cluster_id: str | None = raw_element.get("clusterId")
        self.environment_id: str | None = raw_element.get("environmentId")
        self.usage: list[EnvironmentUsageEntry] = [
            EnvironmentUsageEntry(raw_element=e) for e in raw_element.get("usage", [])
        ]


class EnvironmentUsageResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.data: list[EnvironmentUsage] = [
            EnvironmentUsage(raw_element=e) for e in raw_element.get("data", [])
        ]
        self.last_modified_time: str | None = raw_element.get("lastModifiedTime")
        self.next_page_key: str | None = raw_element.get("nextPageKey")
