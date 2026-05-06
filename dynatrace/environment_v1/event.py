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

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient

EVENT_TYPE_AVAILABILITY_EVENT = "AVAILABILITY_EVENT"
EVENT_TYPE_CUSTOM_ALERT = "CUSTOM_ALERT"
EVENT_TYPE_CUSTOM_ANNOTATION = "CUSTOM_ANNOTATION"
EVENT_TYPE_CUSTOM_CONFIGURATION = "CUSTOM_CONFIGURATION"
EVENT_TYPE_CUSTOM_DEPLOYMENT = "CUSTOM_DEPLOYMENT"
EVENT_TYPE_CUSTOM_INFO = "CUSTOM_INFO"
EVENT_TYPE_ERROR_EVENT = "ERROR_EVENT"
EVENT_TYPE_MARKED_FOR_TERMINATION = "MARKED_FOR_TERMINATION"
EVENT_TYPE_PERFORMANCE_EVENT = "PERFORMANCE_EVENT"
EVENT_TYPE_RESOURCE_CONTENTION = "RESOURCE_CONTENTION"


class EventService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def create_event(
        self,
        event_type: str,
        entity_id: str,
        source: str,
        start: datetime | None = None,
        end: datetime | None = None,
        timeout_minutes: int | None = None,
        annotation_type: str | None = None,
        annotation_description: str | None = None,
        description: str | None = None,
        title: str | None = None,
        custom_properties: dict[str, str] | None = None,
        allow_davis_merge: bool | None = None,
    ) -> Response:

        attach_rules = PushEventAttachRules(entity_ids=[entity_id], tag_rule=None)
        return await EventCreation(
            self.__http_client,
            event_type=event_type,
            attach_rules=attach_rules,
            source=source,
            start=start,
            end=end,
            timeout_minutes=timeout_minutes,
            annotation_type=annotation_type,
            annotation_description=annotation_description,
            description=description,
            title=title,
            custom_properties=custom_properties,
            allow_davis_merge=allow_davis_merge,
        ).post()


class EventCreation(DynatraceObject):
    def __init__(
        self,
        http_client,
        event_type: str,
        attach_rules: "PushEventAttachRules",
        source: str,
        start: datetime | None = None,
        end: datetime | None = None,
        timeout_minutes: int | None = None,
        annotation_type: str | None = None,
        annotation_description: str | None = None,
        description: str | None = None,
        title: str | None = None,
        custom_properties: str | None = None,
        allow_davis_merge: bool | None = None,
    ):

        raw_element = {
            "eventType": event_type,
            "start": int(start.timestamp()) * 1000 if start else None,
            "end": int(end.timestamp()) * 1000 if end else None,
            "timeoutMinutes": timeout_minutes,
            "source": source,
            "annotationType": annotation_type,
            "annotationDescription": annotation_description,
            "attachRules": attach_rules._raw_element,
            "description": description,
            "title": title,
            "customProperties": custom_properties,
            "allowDavisMerge": allow_davis_merge,
        }

        super().__init__(http_client, None, raw_element)

    async def post(self):
        return await self._http_client.make_request(
            "/api/v1/events", params=self._raw_element, method="POST"
        )


class PushEventAttachRules:
    def __init__(
        self, entity_ids: list[str] | None, tag_rule: list["TagMatchRule"] | None
    ):

        self._raw_element = {
            "entityIds": entity_ids,
            "tagRule": [t._raw_element for t in tag_rule] if tag_rule else None,
        }


class TagMatchRule:
    def __init__(self, me_types: list[str], tags: list[str]):
        self._raw_element = {
            "meTypes": me_types,
            "tags": tags,
        }


"""
type EventStoreResult struct {
	StoredEventIds       []int    `json:"storedEventIds,omitempty"`
	StoredIds            []string `json:"storedIds,omitempty"`
	StoredCorrelationIds []string `json:"storedCorrelationIds,omitempty"`
}
"""
