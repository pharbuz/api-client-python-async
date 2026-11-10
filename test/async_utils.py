import hashlib
import json
import os
from collections.abc import AsyncIterable
from pathlib import Path
from typing import Any, TypeVar

from dynatrace.utils import slugify

T = TypeVar("T")


class MockResponse:
    json_data: Any
    headers: dict[str, str]
    text: str
    content: bytes | None
    status_code: int

    def __init__(self, json_data: Any) -> None:
        self.json_data = json_data
        self.headers = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.content = self.text.encode() if self.text else None
        self.status_code = 200

    def json(self) -> Any:
        return self.json_data


current_file_path = os.path.dirname(os.path.realpath(__file__))


async def local_make_request(
    self: Any,
    path: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    method: str = "GET",
    data: Any = None,
    query_params: dict[str, Any] | None = None,
    **kwargs: Any,
) -> MockResponse:

    params_key = f"{params}" if params else ""
    if query_params:
        params_key += f"{query_params}"
    if params_key:
        encoded = f"{params_key}".encode()
        params_key = f"_{hashlib.sha256(encoded).hexdigest()}"[:16]

    path = slugify(path)
    file_name = f"{method}{path}{params_key}.json"
    file_path = Path(current_file_path, "mock_data", file_name)
    if not file_path.exists():
        candidates = sorted(
            Path(current_file_path, "mock_data").glob(f"{method}{path}*.json")
        )
        if path == "api_v2_metrics" and candidates:
            if "writtenSince': None" in str(params) and "fields': None" in str(params):
                preferred_name = "GET_api_v2_metrics_c2452ee3448e535.json"
            else:
                preferred_name = "GET_api_v2_metrics_b9525a59df51eee.json"

            preferred = next(
                (
                    candidate
                    for candidate in candidates
                    if candidate.name == preferred_name
                ),
                None,
            )
            file_path = preferred or candidates[0]
        elif candidates:
            file_path = candidates[0]

    with open(file_path) as f:
        content = f.read()
        json_data = json.loads(content) if content else None
        return MockResponse(json_data)


async def collect(async_iterable: AsyncIterable[T]) -> list[T]:
    return [item async for item in async_iterable]


async def first(async_iterable: AsyncIterable[T]) -> T:
    async for item in async_iterable:
        return item
    raise AssertionError("Expected at least one item")
