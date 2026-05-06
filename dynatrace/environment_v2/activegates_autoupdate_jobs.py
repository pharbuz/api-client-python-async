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

from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.environment_v2.schemas import VersionCompareType
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import timestamp_to_string


class UpdateType(Enum):
    ACTIVE_GATE = "ACTIVE_GATE"
    REMOTE_PLUGIN_AGENT = "REMOTE_PLUGIN_AGENT"
    SYNTHETIC = "SYNTHETIC"
    Z_REMOTE = "Z_REMOTE"


class ActiveGateAutoUpdateJobsService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
        start_version_compare_type: str | VersionCompareType | None = None,
        start_version: str | None = None,
        update_type: str | UpdateType | None = None,
        target_version_compare_type: str | VersionCompareType | None = None,
        target_version: str | None = None,
    ) -> PaginatedList["UpdateJobList"]:
        params = {
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
            "startVersionCompareType": start_version_compare_type,
            "startVersion": start_version,
            "updateType": update_type,
            "targetVersionCompareType": target_version_compare_type,
            "targetVersion": target_version,
        }
        return await PaginatedList(
            UpdateJobList,
            self.__http_client,
            "/api/v2/activeGates/updateJobs",
            list_item="allUpdateJobs",
            target_params=params,
        ).initialize()

    async def get(
        self,
        activegate_id: str,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
        start_version_compare_type: str | VersionCompareType | None = None,
        start_version: str | None = None,
        update_type: str | UpdateType | None = None,
        target_version_compare_type: str | VersionCompareType | None = None,
        target_version: str | None = None,
    ) -> "UpdateJobList":
        params = {
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
            "startVersionCompareType": start_version_compare_type,
            "startVersion": start_version,
            "updateType": update_type,
            "targetVersionCompareType": target_version_compare_type,
            "targetVersion": target_version,
        }
        return UpdateJobList(
            raw_element=(
                await self.__http_client.make_request(
                    f"/api/v2/activeGates/{activegate_id}/updateJobs", params=params
                )
            ).json()
        )

    async def post(self, activegate_id: str, target_version: str):
        params = {"targetVersion": target_version}
        return UpdateJob(
            raw_element=(
                await self.__http_client.make_request(
                    f"/api/v2/activeGates/{activegate_id}/updateJobs",
                    params=params,
                    method="POST",
                )
            ).json()
        )

    async def validate(self, activegate_id: str, target_version: str):
        params = {"targetVersion": target_version}
        return await self.__http_client.make_request(
            f"/api/v2/activeGates/{activegate_id}/updateJobs/validator",
            params=params,
            method="POST",
        )

    async def get_job(self, activegate_id: str, job_id: str):
        return UpdateJob(
            raw_element=(
                await self.__http_client.make_request(
                    f"/api/v2/activeGates/{activegate_id}/updateJobs/{job_id}"
                )
            ).json()
        )

    async def delete_job(self, activegate_id: str, job_id: str):
        return await self.__http_client.make_request(
            f"/api/v2/activeGates/{activegate_id}/updateJobs/{job_id}", method="DELETE"
        )


class UpdateJobList(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.activegate_id: str = raw_element.get("agId")
        self.update_jobs: list[UpdateJob] = [
            UpdateJob(raw_element=update_job)
            for update_job in raw_element.get("updateJobs", [])
        ]


class UpdateJob(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.job_id: str = raw_element.get("jobId")
        self.job_state: str = raw_element.get("jobState")
        self.update_method: str = raw_element.get("updateMethod")
        self.update_type: str = raw_element.get("updateType")
        self.cancelable: bool = raw_element.get("cancelable")
        self.start_version: str = raw_element.get("startVersion")
        self.target_version: str = raw_element.get("targetVersion")
        self.timestamp: datetime = datetime.fromtimestamp(
            raw_element.get("timestamp") / 1000,
            UTC,
        )
        self.ag_type: str = raw_element.get("agType")
        self.environments: list[str] = raw_element.get("environments")
        self.error: str = raw_element.get("error")
        self.duration: timedelta | None = (
            timedelta(milliseconds=raw_element.get("duration"))
            if raw_element.get("duration")
            else None
        )
