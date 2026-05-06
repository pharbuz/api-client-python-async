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
from typing import Optional

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient

SYNTHETIC_EVENT_TYPE_OUTAGE = "testOutage"
SYNTHETIC_EVENT_TYPE_SLOWDOWN = "testSlowdown"


class ThirdPartySyntheticTestsService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def report_simple_thirdparty_synthetic_test(
        self,
        engine_name: str,
        timestamp: datetime,
        location_id: str,
        location_name: str,
        test_id: str,
        test_title: str,
        schedule_interval: int,
        success: bool,
        response_time: int,
        icon_url: str = None,
        edit_link: str = None,
        step_title: str | None = None,
        detailed_steps: list["SyntheticTestStep"] | None = None,
        detailed_step_results: list["SyntheticMonitorStepResult"] | None = None,
    ):

        location = ThirdPartySyntheticLocation(
            self.__http_client, location_id, location_name
        )
        synthetic_location = SyntheticTestLocation(self.__http_client, location_id)
        if detailed_steps is None:
            detailed_steps = [SyntheticTestStep(self.__http_client, 1, step_title)]

        monitor = ThirdPartySyntheticMonitor(
            self.__http_client,
            test_id,
            test_title,
            [synthetic_location],
            schedule_interval,
            steps=detailed_steps,
            edit_link=edit_link,
        )
        if detailed_step_results is None:
            detailed_step_results = [
                SyntheticMonitorStepResult(
                    self.__http_client, 1, timestamp, response_time_millis=response_time
                )
            ]
        location_result = ThirdPartySyntheticLocationTestResult(
            self.__http_client,
            location_id,
            timestamp,
            success,
            step_results=detailed_step_results,
        )
        test_result = ThirdPartySyntheticResult(
            self.__http_client, test_id, len(detailed_steps), [location_result]
        )
        tests = ThirdPartySyntheticTests(
            self.__http_client,
            engine_name,
            timestamp,
            [location],
            [monitor],
            [test_result],
            synthetic_engine_icon_url=icon_url,
        )
        return await tests.post()

    def create_synthetic_test_step_result(
        self, step_id: int, timestamp: datetime, response_time: int
    ) -> "SyntheticMonitorStepResult":
        return SyntheticMonitorStepResult(
            self.__http_client, step_id, timestamp, response_time_millis=response_time
        )

    def create_synthetic_test_step(
        self, step_id: int, step_title: str
    ) -> "SyntheticTestStep":
        return SyntheticTestStep(self.__http_client, step_id, step_title)

    async def report_simple_thirdparty_synthetic_test_event(
        self,
        test_id: str,
        name: str,
        location_id: str,
        timestamp: datetime,
        state: str,
        event_type: str,
        reason: str,
        engine_name: str,
    ):
        opened_events: list[ThirdPartyEventOpenNotification] = []
        resolved_events = []
        event_id = f"{test_id}_event"
        if state == "open":
            opened_events.append(
                ThirdPartyEventOpenNotification(
                    self.__http_client,
                    test_id,
                    event_id,
                    name,
                    event_type,
                    reason,
                    timestamp,
                    [location_id],
                )
            )
        else:
            resolved_events.append(
                ThirdPartyEventResolvedNotification(
                    self.__http_client, test_id, event_id, timestamp
                )
            )

        if opened_events or resolved_events:
            events = ThirdPartySyntheticEvents(
                self.__http_client, engine_name, opened_events, resolved_events
            )
            return await events.post()


class ThirdPartySyntheticTests(DynatraceObject):
    def __init__(
        self,
        http_client,
        synthetic_engine_name: str,
        message_timestamp: datetime,
        locations: list["ThirdPartySyntheticLocation"],
        tests: list["ThirdPartySyntheticMonitor"],
        test_results: list["ThirdPartySyntheticResult"] | None = None,
        synthetic_engine_icon_url: str | None = None,
    ):

        raw_element = {
            "syntheticEngineName": synthetic_engine_name,
            "syntheticEngineIconUrl": synthetic_engine_icon_url,
            "messageTimestamp": int(message_timestamp.timestamp() * 1000),
            "locations": [location._raw_element for location in locations],
            "tests": [test._raw_element for test in tests],
            "testResults": (
                [test_result._raw_element for test_result in test_results]
                if test_results
                else None
            ),
        }
        super().__init__(http_client, None, raw_element)

    async def post(self):
        return await self._http_client.make_request(
            "/api/v1/synthetic/ext/tests", params=self._raw_element, method="POST"
        )


class ThirdPartySyntheticLocation(DynatraceObject):
    def __init__(self, http_client, location_id: str, name: str, ip: str | None = None):

        raw_element = {"id": location_id, "name": name, "ip": ip}
        super().__init__(http_client, None, raw_element)


class ThirdPartySyntheticMonitor(DynatraceObject):
    def __init__(
        self,
        http_client,
        test_id: str,
        title: str,
        locations: list["SyntheticTestLocation"],
        schedule_interval_in_seconds: int,
        description: str | None = None,
        test_setup: str | None = None,
        expiration_timestamp: int | None = None,
        drilldown_link: str | None = None,
        edit_link: str | None = None,
        deleted: bool | None = None,
        steps: list["SyntheticTestStep"] | None = None,
        no_data_timeout: int | None = None,
    ):

        raw_element = {
            "id": test_id,
            "title": title,
            "description": description,
            "testSetup": test_setup,
            "expirationTimestamp": expiration_timestamp,
            "drilldownLink": drilldown_link,
            "editLink": edit_link,
            "deleted": deleted,
            "locations": [location._raw_element for location in locations],
            "steps": [step._raw_element for step in steps] if steps else None,
            "scheduleIntervalInSeconds": schedule_interval_in_seconds,
            "noDataTimeout": no_data_timeout,
        }
        super().__init__(http_client, None, raw_element)


class SyntheticTestLocation(DynatraceObject):
    def __init__(self, http_client, location_id: str, enabled: bool | None = None):

        raw_element = {"id": location_id, "enabled": enabled}
        super().__init__(http_client, None, raw_element)


class SyntheticTestStep(DynatraceObject):
    def __init__(self, http_client, step_id: int, title: str):
        self.step_id = step_id
        self.title = title

        raw_element = {"id": step_id, "title": title}
        super().__init__(http_client, None, raw_element)


class ThirdPartySyntheticResult(DynatraceObject):
    def __init__(
        self,
        http_client,
        test_id: str,
        total_step_count: int,
        location_results: list["ThirdPartySyntheticLocationTestResult"],
        schedule_interval_in_seconds: int | None = None,
    ):

        raw_element = {
            "id": test_id,
            "scheduleIntervalInSeconds": schedule_interval_in_seconds,
            "totalStepCount": total_step_count,
            "locationResults": [
                location_result._raw_element for location_result in location_results
            ],
        }
        super().__init__(http_client, None, raw_element)


class ThirdPartySyntheticLocationTestResult(DynatraceObject):
    def __init__(
        self,
        http_client,
        location_id: str,
        start_timestamp: datetime,
        success: bool,
        success_rate: float | None = None,
        response_time_millis: int | None = None,
        step_results: list["SyntheticMonitorStepResult"] | None = None,
    ):

        raw_element = {
            "id": location_id,
            "startTimestamp": int(start_timestamp.timestamp() * 1000),
            "successRate": success_rate,
            "success": success,
            "responseTimeMillis": response_time_millis,
            "stepResults": (
                [step_result._raw_element for step_result in step_results]
                if step_results
                else None
            ),
        }
        super().__init__(http_client, None, raw_element)


class SyntheticMonitorStepResult(DynatraceObject):
    def __init__(
        self,
        http_client,
        step_id: int,
        start_timestamp: datetime,
        response_time_millis: int | None = None,
        error: Optional["SyntheticMonitorError"] = None,
    ):

        raw_element = {
            "id": step_id,
            "startTimestamp": int(start_timestamp.timestamp() * 1000),
            "responseTimeMillis": response_time_millis,
            "error": error._raw_element if error else None,
        }
        super().__init__(http_client, None, raw_element)


class SyntheticMonitorError(DynatraceObject):
    def __init__(self, http_client, code: int, message: str):

        raw_element = {"code": code, "message": message}
        super().__init__(http_client, None, raw_element)


class ThirdPartySyntheticEvents(DynatraceObject):
    def __init__(
        self,
        http_client,
        synthetic_engine_name: str,
        open_events: list["ThirdPartyEventOpenNotification"] | None,
        resolved_events: list["ThirdPartyEventResolvedNotification"] | None,
    ):

        raw_element = {
            "syntheticEngineName": synthetic_engine_name,
            "open": (
                [open_event._raw_element for open_event in open_events]
                if open_events
                else None
            ),
            "resolved": (
                [resolved_event._raw_element for resolved_event in resolved_events]
                if resolved_events
                else None
            ),
        }
        super().__init__(http_client, None, raw_element)

    async def post(self):
        return await self._http_client.make_request(
            "/api/v1/synthetic/ext/events", params=self._raw_element, method="POST"
        )


class ThirdPartyEventOpenNotification(DynatraceObject):
    def __init__(
        self,
        http_client,
        test_id: str,
        event_id: str,
        name: str,
        event_type: str,
        reason: str,
        start_timestamp: datetime,
        location_ids: list[str],
    ):

        raw_element = {
            "testId": test_id,
            "eventId": event_id,
            "name": name,
            "eventType": event_type,
            "reason": reason,
            "startTimestamp": int(start_timestamp.timestamp() * 1000),
            "locationIds": location_ids,
        }
        super().__init__(http_client, None, raw_element)


class ThirdPartyEventResolvedNotification(DynatraceObject):
    def __init__(
        self, http_client, test_id: str, event_id: str, end_timestamp: datetime
    ):

        raw_element = {
            "testId": test_id,
            "eventId": event_id,
            "endTimestamp": int(end_timestamp.timestamp() * 1000),
        }
        super().__init__(http_client, None, raw_element)
