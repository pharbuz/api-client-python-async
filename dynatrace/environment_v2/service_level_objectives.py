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

from datetime import datetime
from enum import Enum
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import timestamp_to_string


class SloService:
    ENDPOINT = "/api/v2/slo"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self,
        page_size: int | None = 10,
        time_from: datetime | str | None = "now-2w",
        time_to: datetime | str | None = None,
        slo_selector: str | None = None,
        sort: str | None = "name",
        time_frame: str | None = "CURRENT",
        page_idx: int | None = 1,
        demo: bool | None = False,
        evaluate: bool | None = False,
        enabled_slos: str | None = "all",
        show_global_slos: bool | None = None,
    ) -> PaginatedList["Slo"]:
        """Lists all available SLOs along with calculated values

        :param page_size: The amount of SLOs in a single response payload. Max 10,000.
        :param time_from: The start of the requested timeframe.
        :param time_to: The end of the requested timeframe.
        :param slo_selector: The scope of the query. Only SLOs matching the provided criteria are included in the response.
        :param sort: The sorting of SLO entries. Default is by name in ascending order.
        :param time_frame: The timeframe to calculate the SLO values. CURRENT: SLO's own timeframe. GTF: timeframe specified by from and to parameters.
        :param page_idx: Only SLOs on the given page are included in the response. The first page has the index '1'.
        :param demo: Get your SLOs (false) or a set of demo SLOs (true)
        :param evaluate: Get your SLOs without them being evaluated (`False`) or with evaluations (`True`).
        :param enabled_slos: Get your enabled SLOs ("true"), disabled ones ("false") or both enabled and disabled ones ("all"). This value must be a lowercase string.
        :param show_global_slos: Include global SLOs regardless of selected filter.

        :returns PaginatedList[Slo]: the list of SLOs matching criteria
        """
        params = {
            "pageSize": page_size,
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
            "sloSelector": slo_selector,
            "sort": sort,
            "timeFrame": time_frame,
            "pageIdx": page_idx,
            "demo": demo,
            "evaluate": evaluate,
            "enabledSlos": enabled_slos,
            "showGlobalSlos": show_global_slos,
        }
        return await PaginatedList(
            target_class=Slo,
            http_client=self.__http_client,
            target_params=params,
            target_url=f"{self.ENDPOINT}",
            list_item="slo",
        ).initialize()

    async def get(
        self,
        slo_id: str,
        time_from: datetime | str | None = "now-2w",
        time_to: datetime | str | None = None,
        time_frame: str | None = "CURRENT",
    ) -> "Slo":
        """Gets parameters and the calculated value of an SLO

        :param slo_id: The ID of the required SLO.
        :param time_from: The start of the requested timeframe.
        :param time_to: The end of the requested timeframe.
        :param time_frame: The timeframe to calculate the SLO values. CURRENT: SLO's own timeframe. GTF: timeframe specified by from and to parameters.

        :returns Slo: the requested SLO
        """
        params = {
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
            "timeFrame": time_frame,
        }
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{slo_id}", params=params
            )
        ).json()
        return Slo(raw_element=response)

    async def post(self, slo: "Slo") -> "Response":
        """Creates a new SLO in Dynatrace.

        :param slo: the Slo that should be created.

        :returns Response: HTTP response for the request
        """
        return await slo.post()

    async def put(self, slo: "Slo") -> "Response":
        """Updates an existing SLO in Dynatrace.

        :param slo: the Slo with udpated details

        :returns Response: HTTP response for the request
        """
        return await slo.put()

    async def delete(self, slo_id: str) -> "Response":
        """Deletes an SLO

        :param slo_id: The ID of the existing SLO.

        :returns Response: HTTP response for the request
        """
        return await self.__http_client.make_request(
            path=f"{self.ENDPOINT}/{slo_id}", method="DELETE"
        )

    def create(
        self,
        name: str,
        target: float,
        warning: float,
        timeframe: str,
        use_rate_metric: bool | None = None,
        metric_rate: str | None = None,
        metric_numerator: str | None = None,
        metric_denominator: str | None = None,
        metric_expression: str | None = None,
        metric_name: str | None = None,
        filter: str | None = None,
        evaluation_type: str | None = "AGGREGATE",
        custom_description: str | None = None,
        enabled: bool | None = False,
    ) -> "Slo":
        """Creates an Slo object from scratch.

        :param name: The name of the SLO.
        :param target: The target value of the SLO.
        :param warning: The warning value of the SLO. At warning state the SLO is still fulfilled but is getting close to failure.
        :param timeframe: The timeframe for the SLO evaluation. Use the syntax of the global timeframe selector.
        :param use_rate_metric: [DEPRECATED] The type of the metric to use for SLO calculation - an existing percentage-based metric (true) or a ratio of two metrics (false)
        :param metric_rate: [DEPRECATED] The percentage-based metric for the calculation of the SLO. Required when the useRateMetric is set to true.
        :param metric_numerator: [DEPRECATED] The metric for the count of successes (the numerator in rate calculation).Required when the useRateMetric is set to false.
        :param metric_denominator: [DEPRECATED] The total count metric (the denominator in rate calculation). Required when the useRateMetric is set to false.
        :param metric_expression: The percentage-based metric expression for the calculation of the SLO.
        :param evaluation_type: The evaluation type of the SLO.
        :param filter_: The entity filter for the SLO evaluation. Use the syntax of entity selector.
        :param custom_description: The custom description of the SLO.
        :param enabled: The SLO is enabled (true) or disabled (false).

        :returns Slo: the resulting Slo. This can now be used in POST and PUT calls
        """
        raw_slo = {
            "name": name,
            "target": target,
            "warning": warning,
            "timeframe": timeframe,
            "useRateMetric": use_rate_metric,
            "metricRate": metric_rate if use_rate_metric else "",
            "metricNumerator": metric_numerator if not use_rate_metric else "",
            "metricDenominator": metric_denominator if not use_rate_metric else "",
            "metricExpression": metric_expression,
            "metricName": metric_name,
            "filter": filter,
            "evaluationType": evaluation_type,
            "description": custom_description,
            "enabled": enabled,
        }
        return Slo(raw_element=raw_slo, http_client=self.__http_client)


class Slo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        # required
        self.name: str = raw_element.get("name")
        self.id: str = raw_element.get("id", "")
        self.target: float = raw_element.get("target")
        self.warning: float = raw_element.get("warning")
        self.timeframe: str = raw_element.get("timeframe")
        self.evaluation_type: SloEvaluationType = SloEvaluationType(
            raw_element.get("evaluationType")
        )

        # optional
        self.status: SloStatus | None = (
            SloStatus(raw_element.get("status")) if raw_element.get("status") else None
        )
        self.metric_rate: str | None = raw_element.get("metricRate")
        self.metric_numerator: str | None = raw_element.get("metricNumerator")
        self.metric_denominator: str | None = raw_element.get("metricDenominator")
        self.metric_expression: str | None = raw_element.get("metricExpression")
        self.metric_name: str | None = raw_element.get("metricName")
        self.error_budget: float | None = raw_element.get("errorBudget", 0)
        self.numerator_value: float | None = raw_element.get("numeratorValue", 0)
        self.denominator_value: float | None = raw_element.get("denominatorValue", 0)
        self.related_open_problems: int | None = raw_element.get(
            "relatedOpenProblems", 0
        )
        self.related_total_problems: int | None = raw_element.get(
            "relatedTotalProblems", 0
        )
        self.evaluated_percentage: float | None = raw_element.get(
            "evaluatedPercentage", 0
        )
        self.filter: str | None = raw_element.get("filter")
        self.enabled: bool | None = raw_element.get("enabled", False)
        self.custom_description: str | None = raw_element.get("description")
        self.error: str | None = raw_element.get("error", "NONE")
        self.error_budget_burn_rate: dict[str, Any] | None = raw_element.get(
            "errorBudgetBurnRate"
        )
        self.use_rate_metric: bool | None = raw_element.get("useRateMetric")

    def to_json(self) -> dict[str, Any]:
        """Translates an Slo to a JSON dict."""
        return {
            "name": self.name,
            "target": self.target,
            "warning": self.warning,
            "timeframe": self.timeframe,
            "evaluationType": str(self.evaluation_type),
            "enabled": self.enabled,
            "useRateMetric": self.use_rate_metric,
            "metricRate": self.metric_rate,
            "metricNumerator": self.metric_numerator,
            "metricDenominator": self.metric_denominator,
            "metricExpression": self.metric_expression,
            "metricName": self.metric_name,
            "filter": self.filter,
            "description": self.custom_description,
            "errorBudgetBurnRate": self.error_budget_burn_rate,
        }

    async def post(self) -> "Response":
        """Creates this object as a new SLO in Dynatrace"""
        response = await self._http_client.make_request(
            path=SloService.ENDPOINT, method="POST", params=self.to_json()
        )
        if response.status_code == 201:
            location = response.headers.get("location")
            self.id = location[location.rfind("/") + 1 :].strip()

        return response

    async def put(self) -> "Response":
        """Updates an existing SLO in Dynatrace based on this object's details"""
        return await self._http_client.make_request(
            path=f"{SloService.ENDPOINT}/{self.id}", method="PUT", params=self.to_json()
        )


class SloEvaluationType(Enum):
    AGGREGATE = "AGGREGATE"

    def __str__(self):
        return self.value


class SloStatus(Enum):
    FAILURE = "FAILURE"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"

    def __str__(self):
        return self.value
