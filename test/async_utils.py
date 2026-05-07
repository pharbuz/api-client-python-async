import hashlib
import json
import os
from pathlib import Path

from dynatrace.utils import slugify


class MockResponse:
    def __init__(self, json_data):
        self.json_data = json_data
        self.headers = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.content = self.text.encode() if self.text else None
        self.status_code = 200

    def json(self):
        return self.json_data


current_file_path = os.path.dirname(os.path.realpath(__file__))


async def local_make_request(
    self,
    path: str,
    params: dict | None = None,
    headers: dict | None = None,
    method="GET",
    data=None,
    query_params=None,
    **kwargs,
) -> MockResponse:

    params = f"{params}" if params else ""
    if query_params:
        params += f"{query_params}"
    if params:
        encoded = f"{params}".encode()
        params = f"_{hashlib.sha256(encoded).hexdigest()}"[:16]

    path = slugify(path)
    file_name = f"{method}{path}{params}.json"
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


async def collect(async_iterable):
    return [item async for item in async_iterable]


async def first(async_iterable):
    async for item in async_iterable:
        return item
    raise AssertionError("Expected at least one item")
