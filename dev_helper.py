"""
This file can be used during development to automatically generate mock data from the API calls.
Please check CONTRIBUTING.md for details
"""

import asyncio
import hashlib
import json
import logging
import os
from pathlib import Path

import wrapt

from dynatrace import DynatraceAsync
from dynatrace.utils import slugify


@wrapt.patch_function_wrapper("dynatrace.http_client", "HttpClient.make_request")
async def dump_to_json(wrapped, instance, args, kwargs):
    r = await wrapped(*args, **kwargs)
    method = kwargs.get("method", "GET")
    params = kwargs.get("params", "")
    query_params = kwargs.get("query_params", "")

    params = f"{params}" if params else ""
    if query_params:
        params += f"{query_params}"
    if params:
        encoded = f"{params}".encode()
        params = f"_{hashlib.sha256(encoded).hexdigest()}"[:16]

    path = slugify(args[0])
    file_name = f"{method}{path}{params}.json"
    file_path = f"test/mock_data/{file_name}"
    if not Path(file_path).exists():
        with open(file_path, "w") as f:
            if r.text:
                print(f"Dumping response to '{file_name}'")
                json.dump(r.json(), f)
    return r


def setup_log():
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    st = logging.StreamHandler()
    fmt = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(thread)d - %(filename)s:%(lineno)d - %(message)s"
    )
    st.setFormatter(fmt)
    log.addHandler(st)
    return log


async def main():
    async with DynatraceAsync(
        client_id=os.getenv("DYNATRACE_OAUTH_CLIENT_ID"),
        client_secret=os.getenv("DYNATRACE_OAUTH_CLIENT_SECRET"),
        account_uuid=os.getenv("DYNATRACE_ACCOUNT_UUID"),
        base_url=os.getenv("DYNATRACE_TENANT_URL"),
        log=setup_log(),
        scope="environment-api:metrics:read environment-api:entities:read",
    ) as dt:
        # TODO - Code here as you add new endpoints, during development
        # Any requests are going to be recorded in the `test/mock` folder and can later be used to write tests.
        async for metric in await dt.metrics.list(page_size=500):
            print(metric.metric_id)


if __name__ == "__main__":
    asyncio.run(main())
