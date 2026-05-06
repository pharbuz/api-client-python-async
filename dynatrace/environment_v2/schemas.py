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

from enum import Enum
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject

# Schemas that don't belong to a specific api tag


class ConfigurationMetadata(DynatraceObject):
    def _create_from_raw_data(self, raw_element):
        self.cluster_version: str = raw_element.get("clusterVersion")
        self.configuration_versions: list[int] = raw_element.get(
            "configurationVersions"
        )
        self.current_configuration_versions: list[str] = raw_element.get(
            "currentConfigurationVersions"
        )


class VersionCompareType(Enum):
    EQUAL = "EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    LOWER = "LOWER"
    LOWER_EQUAL = "LOWER_EQUAL"

    def __repr__(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value


class ManagementZone(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.name: str = raw_element.get("name", "")
        self.id: str = raw_element["id"]

    def to_json(self) -> dict[str, Any]:
        return {"name": self.name, "id": self.id}
