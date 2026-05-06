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

from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient

T = TypeVar("T", bound=DynatraceObject)


class PaginatedList(Generic[T]):
    def __init__(
        self,
        target_class,
        http_client,
        target_url,
        target_params=None,
        headers=None,
        list_item="result",
    ):
        self.__target_class = target_class
        self.__http_client: HttpClient = http_client
        self.__target_url = target_url
        self.__target_params = target_params
        self.__headers = headers
        self.__list_item = list_item
        self._has_next_page = True
        self.__total_count = None
        self.__page_size = None
        self.__elements: list[T] = []
        self.__initialized = False

    async def initialize(self) -> "PaginatedList[T]":
        if not self.__initialized:
            self.__elements.extend(await self._get_next_page())
            self.__initialized = True
        return self

    def __getitem__(self, index):
        pass

    def __iter__(self):
        raise TypeError(
            "PaginatedList is asynchronous. Use 'async for' or await to_list()."
        )

    def __len__(self):
        return self.__total_count or len(self.__elements)

    async def __aiter__(self) -> AsyncIterator[T]:
        if not self.__initialized:
            self.__elements.extend(await self._get_next_page())
            self.__initialized = True

        for element in self.__elements:
            yield element

        while self._has_next_page:
            new_elements = await self._get_next_page()
            self.__elements.extend(new_elements)
            for element in new_elements:
                yield element

    async def to_list(self) -> list[T]:
        return [element async for element in self]

    async def _get_next_page(self):
        response = await self.__http_client.make_request(
            self.__target_url, params=self.__target_params, headers=self.__headers
        )
        json_response = response.json()
        data = []
        if json_response.get("nextPageKey", None):
            self._has_next_page = True
            self.__target_params = {"nextPageKey": json_response["nextPageKey"]}
        else:
            self._has_next_page = False

        if self.__list_item in json_response:
            elements = json_response[self.__list_item]
            self.__total_count = json_response.get("totalCount") or len(elements)

            data = [
                self.__target_class(self.__http_client, response.headers, element)
                for element in elements
            ]
        return data


class HeaderPaginatedList(Generic[T]):
    def __init__(
        self, target_class, http_client, target_url, target_params=None, headers=None
    ):
        self.__elements = list()
        self.__target_class = target_class
        self.__http_client: HttpClient = http_client
        self.__target_url = target_url
        self.__target_params = target_params
        self.__headers = headers
        self._has_next_page = True
        self.__total_count = None
        self.__page_size = None
        self.__initialized = False

    async def initialize(self) -> "HeaderPaginatedList[T]":
        if not self.__initialized:
            self.__elements.extend(await self._get_next_page())
            self.__initialized = True
        return self

    def __getitem__(self, index):
        pass

    def __iter__(self):
        raise TypeError(
            "HeaderPaginatedList is asynchronous. Use 'async for' or await to_list()."
        )

    def __len__(self):
        return self.__total_count or len(self.__elements)

    async def __aiter__(self) -> AsyncIterator[T]:
        if not self.__initialized:
            self.__elements.extend(await self._get_next_page())
            self.__initialized = True

        for element in self.__elements:
            yield element

        while self._has_next_page:
            new_elements = await self._get_next_page()
            self.__elements.extend(new_elements)
            for element in new_elements:
                yield element

    async def to_list(self) -> list[T]:
        return [element async for element in self]

    async def _get_next_page(self):
        response = await self.__http_client.make_request(
            self.__target_url, params=self.__target_params, headers=self.__headers
        )
        json_response = response.json()
        headers = response.headers
        if "next-page-key" in headers:
            self._has_next_page = True
            self.__target_params = {"nextPageKey": headers["next-page-key"]}
        else:
            self._has_next_page = False

        elements = json_response
        self.__total_count = headers.get("total-count") or len(elements)
        data = [
            self.__target_class(self.__http_client, response.headers, element)
            for element in elements
        ]
        return data
