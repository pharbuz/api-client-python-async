from collections.abc import Generator
from unittest import mock

import pytest

from dynatrace import DynatraceAccessToken, DynatraceAsync
from dynatrace.http_client import HttpClient
from test.async_utils import local_make_request


@pytest.fixture
def dt() -> Generator[DynatraceAsync]:
    with mock.patch.object(HttpClient, "make_request", new=local_make_request):
        dt = DynatraceAsync(
            base_url="mock_tenant",
            credentials=DynatraceAccessToken(token="mock_token"),
        )
        yield dt
