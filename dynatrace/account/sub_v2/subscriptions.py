"""Subscription management API v2 wrappers."""

import builtins
from datetime import datetime
from enum import Enum
from typing import Any, Union

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.utils import timestamp_to_string


class SubscriptionService:
    """
    /sub/v2 Subscriptions API

    - GET /sub/v2/accounts/{accountUuid}/subscriptions
    - GET /sub/v2/accounts/{accountUuid}/subscriptions/events
    - GET /sub/v2/accounts/{accountUuid}/subscriptions/forecast
    - GET /sub/v2/accounts/{accountUuid}/subscriptions/{subscriptionUuid}
    - GET /sub/v2/accounts/{accountUuid}/subscriptions/{subscriptionUuid}/usage
    - GET /sub/v2/accounts/{accountUuid}/subscriptions/{subscriptionUuid}/cost
    """

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    # Subscription listing and detail endpoints.
    async def list(self, account_uuid: str) -> builtins.list["SubscriptionSummary"]:
        resp = (
            await self.__http_client.make_request(
                f"/sub/v2/accounts/{account_uuid}/subscriptions"
            )
        ).json()
        return [SubscriptionSummary(raw_element=e) for e in resp.get("data", [])]

    async def get(
        self, account_uuid: str, subscription_uuid: str
    ) -> "SubscriptionDetail":
        # Response models.
        resp = (
            await self.__http_client.make_request(
                f"/sub/v2/accounts/{account_uuid}/subscriptions/{subscription_uuid}"
            )
        ).json()
        return SubscriptionDetail(raw_element=resp)

    async def usage(
        self,
        account_uuid: str,
        subscription_uuid: str,
        environment_ids: builtins.list[str] | None = None,
        capability_keys: builtins.list[str] | None = None,
        cluster_ids: builtins.list[str] | None = None,
    ) -> "SubscriptionUsageResponse":
        params: dict[str, Any] = {}
        if environment_ids:
            params["environmentIds"] = ",".join(environment_ids)
        if capability_keys:
            params["capabilityKeys"] = ",".join(capability_keys)
        if cluster_ids:
            params["clusterIds"] = ",".join(cluster_ids)

        resp = (
            await self.__http_client.make_request(
                f"/sub/v2/accounts/{account_uuid}/subscriptions/{subscription_uuid}/usage",
                params=params,
            )
        ).json()
        return SubscriptionUsageResponse(raw_element=resp)

    async def cost(
        self,
        account_uuid: str,
        subscription_uuid: str,
        environment_ids: builtins.list[str] | None = None,
        capability_keys: builtins.list[str] | None = None,
        cluster_ids: builtins.list[str] | None = None,
    ) -> "SubscriptionCostResponse":
        params: dict[str, Any] = {}
        if environment_ids:
            params["environmentIds"] = ",".join(environment_ids)
        if capability_keys:
            params["capabilityKeys"] = ",".join(capability_keys)
        if cluster_ids:
            params["clusterIds"] = ",".join(cluster_ids)

        resp = (
            await self.__http_client.make_request(
                f"/sub/v2/accounts/{account_uuid}/subscriptions/{subscription_uuid}/cost",
                params=params,
            )
        ).json()
        return SubscriptionCostResponse(raw_element=resp)

    async def events(
        self,
        account_uuid: str,
        start_time: str | datetime | None = None,
        end_time: str | datetime | None = None,
        event_type: Union[str, "SubscriptionEventType"] | None = None,
    ) -> builtins.list["SubscriptionEvent"]:
        params: dict[str, Any] = {
            "startTime": timestamp_to_string(start_time),
            "endTime": timestamp_to_string(end_time),
            "eventType": (
                event_type.value
                if isinstance(event_type, SubscriptionEventType)
                else event_type
            ),
        }
        resp = (
            await self.__http_client.make_request(
                f"/sub/v2/accounts/{account_uuid}/subscriptions/events", params=params
            )
        ).json()
        return [SubscriptionEvent(raw_element=e) for e in resp]

    async def forecast(self, account_uuid: str) -> "SubscriptionForecast":
        resp = (
            await self.__http_client.make_request(
                f"/sub/v2/accounts/{account_uuid}/subscriptions/forecast"
            )
        ).json()
        return SubscriptionForecast(raw_element=resp)


class SubscriptionSummary(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.uuid: str = raw_element.get("uuid")
        self.type: str | None = raw_element.get("type")
        self.sub_type: str | None = raw_element.get("subType")
        self.name: str | None = raw_element.get("name")
        self.status: str | None = raw_element.get("status")
        self.start_time: str | None = raw_element.get("startTime")
        self.end_time: str | None = raw_element.get("endTime")


class SubscriptionDetail(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.uuid: str = raw_element.get("uuid")
        self.type: str | None = raw_element.get("type")
        self.sub_type: str | None = raw_element.get("subType")
        self.name: str | None = raw_element.get("name")
        self.status: str | None = raw_element.get("status")
        self.start_time: str | None = raw_element.get("startTime")
        self.end_time: str | None = raw_element.get("endTime")
        account = raw_element.get("account") or {}
        self.account_uuid: str | None = account.get("uuid")
        budget = raw_element.get("budget") or {}
        self.budget_total: float | None = budget.get("total")
        self.budget_used: float | None = budget.get("used")
        self.budget_currency_code: str | None = budget.get("currencyCode")
        cp = raw_element.get("currentPeriod") or {}
        self.current_period_start_time: str | None = cp.get("startTime")
        self.current_period_end_time: str | None = cp.get("endTime")
        self.current_period_days_remaining: int | None = cp.get("daysRemaining")
        self.periods: builtins.list[SubscriptionPeriod] = [
            SubscriptionPeriod(raw_element=p) for p in raw_element.get("periods", [])
        ]
        self.capabilities: builtins.list[SubscriptionCapability] = [
            SubscriptionCapability(raw_element=c)
            for c in raw_element.get("capabilities", [])
        ]


class SubscriptionPeriod(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.start_time: str | None = raw_element.get("startTime")
        self.end_time: str | None = raw_element.get("endTime")


class SubscriptionCapability(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.key: str | None = raw_element.get("key")
        self.name: str | None = raw_element.get("name")


class SubscriptionUsageItem(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.capability_key: str | None = raw_element.get("capabilityKey")
        self.capability_name: str | None = raw_element.get("capabilityName")
        self.start_time: str | None = raw_element.get("startTime")
        self.end_time: str | None = raw_element.get("endTime")
        self.value: float | None = raw_element.get("value")
        self.unit_measure: str | None = raw_element.get("unitMeasure")


class SubscriptionUsageResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.data: builtins.list[SubscriptionUsageItem] = [
            SubscriptionUsageItem(raw_element=e) for e in raw_element.get("data", [])
        ]
        self.last_modified_time: str | None = raw_element.get("lastModifiedTime")


class SubscriptionCostItem(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.start_time: str | None = raw_element.get("startTime")
        self.end_time: str | None = raw_element.get("endTime")
        self.value: float | None = raw_element.get("value")
        self.currency_code: str | None = raw_element.get("currencyCode")
        self.last_booking_date: str | None = raw_element.get("lastBookingDate")


class SubscriptionCostResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.data: builtins.list[SubscriptionCostItem] = [
            SubscriptionCostItem(raw_element=e) for e in raw_element.get("data", [])
        ]
        self.last_modified_time: str | None = raw_element.get("lastModifiedTime")


class SubscriptionEvent(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.environment_uuid: str | None = raw_element.get("environmentUuid")
        self.capability: str | None = raw_element.get("capability")
        self.date: str | None = raw_element.get("date")
        self.created_at: str | None = raw_element.get("createdAt")
        self.severity: str | None = raw_element.get("severity")
        self.message: str | None = raw_element.get("message")
        self.event_type: str | None = raw_element.get("eventType")
        self.notification_level: str | None = raw_element.get("notificationLevel")


class SubscriptionForecast(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.forecast_median: float | None = raw_element.get("forecastMedian")
        self.forecast_lower: float | None = raw_element.get("forecastLower")
        self.forecast_upper: float | None = raw_element.get("forecastUpper")
        self.budget: float | None = raw_element.get("budget")
        self.forecast_budget_pct: float | None = raw_element.get("forecastBudgetPct")
        self.forecast_budget_date: str | None = raw_element.get("forecastBudgetDate")
        self.forecast_created_at: str | None = raw_element.get("forecastCreatedAt")


class SubscriptionEventType(Enum):
    """
    Allowed values for the `eventType` query parameter in
    /sub/v2/accounts/{accountUuid}/subscriptions/events

    According to spec: Allowed values are `cost`, `forecast`, `budget`.
    """

    COST = "cost"
    FORECAST = "forecast"
    BUDGET = "budget"
