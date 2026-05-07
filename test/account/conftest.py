from unittest import mock

import pytest

from dynatrace import DynatraceAsync, DynatraceOAuthCredentials
from dynatrace.http_client import HttpClient
from test.async_utils import local_make_request


@pytest.fixture
def dt():
    with mock.patch.object(HttpClient, "make_request", new=local_make_request):
        dt = DynatraceAsync(
            base_url="mock_tenant",
            credentials=DynatraceOAuthCredentials(
                client_id="mock_client_id",
                client_secret="mock_client_secret",
                account_uuid="mock_account_uuid",
            ),
        )
        yield dt
