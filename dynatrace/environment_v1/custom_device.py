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

from collections.abc import MutableSequence
from datetime import UTC, datetime, timedelta

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class CustomDeviceService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    def create(
        self,
        device_id: str,
        display_name: str | None = None,
        group: str | None = None,
        ip_addresses: list[str] | None = None,
        listen_ports: list[int] | None = None,
        technology: str | None = None,
        favicon: str | None = None,
        config_url: str | None = None,
        properties: dict[str, str] | None = None,
        tags: list[str] | None = None,
        series: list | None = None,
        host_names: list[str] | None = None,
    ) -> "CustomDevicePushMessage":
        return CustomDevicePushMessage(
            self.__http_client,
            device_id=device_id,
            display_name=display_name,
            group=group,
            ip_addresses=ip_addresses,
            listen_ports=listen_ports,
            technology=technology,
            favicon=favicon,
            config_url=config_url,
            properties=properties,
            tags=tags,
            series=series,
            host_names=host_names,
        )


class Series(MutableSequence):
    def __init__(self, *args):
        self.list: list[EntityTimeseriesData] = []
        self.extend(list(args))

    def append(self, time_series: "EntityTimeseriesData") -> None:
        for element in self.list:
            if (
                time_series.timeseries_id == element.timeseries_id
                and time_series.dimensions == element.dimensions
            ):
                element.data_points.extend(time_series.data_points)
                return
        self.list.append(time_series)

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]

    def __setitem__(self, i, v):
        self.list[i] = v

    def insert(self, i, v):
        self.list.insert(i, v)

    def __str__(self):
        return str(self.list)


class CustomDevicePushMessage(DynatraceObject):
    def __init__(
        self,
        http_client,
        device_id: str,
        display_name: str | None = None,
        group: str | None = None,
        ip_addresses: list[str] | None = None,
        listen_ports: list[int] | None = None,
        technology: str | None = None,
        favicon: str | None = None,
        config_url: str | None = None,
        properties: dict[str, str] | None = None,
        tags: list[str] | None = None,
        series: Series | None = None,
        host_names: list[str] | None = None,
    ):
        self.device_id = device_id
        self.display_name: str | None = display_name
        self.group: str | None = group
        self.ip_addresses: list[str] | None = ip_addresses
        self.listen_ports: list[int] | None = listen_ports
        self.technology: str | None = technology
        self.favicon: str | None = favicon
        self.config_url: str | None = config_url
        self.properties: dict[str, str] | None = properties
        self.tags: list[str] | None = tags
        self.__series: Series = series
        if self.__series is None:
            self.__series: Series = Series()
        self.host_names: list[str] | None = host_names

        raw_element = {
            "displayName": self.display_name,
            "group": self.group,
            "ipAddresses": self.ip_addresses,
            "listenPorts": self.listen_ports,
            "type": self.technology,
            "favicon": self.favicon,
            "configUrl": self.config_url,
            "properties": self.properties,
            "tags": self.tags,
            "series": (
                [s._raw_element for s in self.__series] if self.__series else None
            ),
            "hostNames": self.host_names,
        }
        super().__init__(http_client, None, raw_element)

    @property
    def series(self) -> Series:
        return self.__series

    @series.setter
    def series(self, series: Series):
        self.__series = series
        self._raw_element["series"] = [s._raw_element for s in self.__series]

    async def post(self, only_valid_data_points=False):
        try:
            response = await self._http_client.make_request(
                f"/api/v1/entity/infrastructure/custom/{self.device_id}",
                params=self._raw_element,
                method="POST",
            )
            return response
        except Exception as e:
            if only_valid_data_points and (
                "configuration.Creation timestamp is:" in f"{e}"
                or "Data point timestamp is too far in the past" in f"{e}"
            ):
                if "configuration.Creation timestamp" in f"{e}":
                    max_timestamp = int(
                        f"{e}".split("configuration.Creation timestamp is:")[1]
                        .split('"')[0]
                        .strip()
                    )
                    max_timestamp = datetime.fromtimestamp(max_timestamp / 1000, tz=UTC)
                else:
                    max_timestamp = datetime.now(tz=UTC) - timedelta(minutes=59)
                self._http_client.log.warning(
                    f"Some data points were invalid, removing data points older than {max_timestamp}"
                )
                for s in self.series:
                    s.data_points = [
                        d
                        for d in s.data_points
                        if d.timestamp.replace(tzinfo=max_timestamp.tzinfo)
                        >= max_timestamp
                    ]
                self._raw_element["series"] = [s._raw_element for s in self.series]
                return await self.post()
            else:
                raise e

    def absolute(
        self,
        key: str,
        value: float,
        timestamp: datetime | None = None,
        dimensions: dict[str, str] | None = None,
    ):
        data_point = DataPoint(value, timestamp)
        self.series.append(
            EntityTimeseriesData(self._http_client, key, [data_point], dimensions)
        )
        self.series = (
            self.series
        )  # Ugly as hell hack because of setter, and I don't want to subclass list


class EntityTimeseriesData(DynatraceObject):
    def __init__(
        self,
        http_client,
        timeseries_id: str,
        data_points: list["DataPoint"],
        dimensions: dict[str, str] | None = None,
    ):
        self.timeseries_id: str = timeseries_id
        self.dimensions = dimensions
        self.__data_points: list[DataPoint] = data_points
        raw_element = {
            "timeseriesId": timeseries_id,
            "dimensions": dimensions,
            "dataPoints": [
                [int(data_point.timestamp.timestamp() * 1000), data_point.value]
                for data_point in data_points
            ],
        }
        super().__init__(http_client, None, raw_element)

    def __repr__(self):
        return f"Series(id={self.timeseries_id}, data_points={self.data_points})"

    @property
    def data_points(self) -> list["DataPoint"]:
        return self.__data_points

    @data_points.setter
    def data_points(self, data_points: list["DataPoint"]):
        self.__data_points = data_points
        self._raw_element["dataPoints"] = [
            [int(data_point.timestamp.timestamp() * 1000), data_point.value]
            for data_point in self.__data_points
        ]


class DataPoint:
    def __init__(self, value: float, timestamp: datetime | None = None):
        self.timestamp = timestamp
        if self.timestamp is None:
            self.timestamp = datetime.now()
        self.value = value

    def __repr__(self):
        return f"[{self.timestamp}, {self.value}]"
