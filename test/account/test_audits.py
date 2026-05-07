import json
from datetime import datetime, timezone
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.audits import AccountAuditsService, Audit, AuditsByAccount
from dynatrace.http_client import HttpClient


class MockResponse:
    def __init__(self, json_data=None):
        self._json_data = json_data
        self.headers = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = 200

    def json(self):
        return self._json_data


async def test_audits_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.audits, AccountAuditsService)


async def test_audits_list_returns_models(dt: DynatraceAsync):
    account_uuid = "account-123"
    start_time = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    end_time = datetime(2026, 1, 31, 23, 59, tzinfo=timezone.utc)

    async def fake_make_request(
        self,
        path,
        params=None,
        headers=None,
        method="GET",
        data=None,
        files=None,
        query_params=None,
        **kwargs,
    ):
        expected_params = {
            "startTime": "2026-01-01T00:00:00.000",
            "endTime": "2026-01-31T23:59:00.000",
            "addFields": "details,eventOutcome",
            "filter": "eventType = 'CREATE'",
            "limit": 25,
            "scanLimitGigabyte": 10,
            "resultSizeLimitMegabyte": 5,
        }
        if (method, path) == ("GET", f"/audit/v1/accounts/{account_uuid}"):
            assert params == expected_params
            return MockResponse(
                {
                    "audits": [
                        {
                            "eventId": "af1f98c9-c611-4056-841b-d039b1af3f98",
                            "timestamp": "2026-01-01T10:00:00Z",
                            "user": "user@example.com",
                            "resource": "POLICY",
                            "resourceName": "Standard User",
                            "eventProvider": "Identity & Account Management",
                            "eventType": "CREATE",
                            "accountUuid": account_uuid,
                            "authenticationClientId": "client-1",
                            "authenticationGrantType": "AUTHORIZATION_CODE",
                            "authenticationToken": "token-1",
                            "authenticationType": "OAUTH2",
                            "details": {
                                "json_before": '{"enabled": false}',
                                "json_after": '{"enabled": true}',
                            },
                            "eventOutcome": "SUCCESS",
                            "eventReason": "Created from UI",
                            "eventVersion": "1.0.0",
                            "originAddress": "0.0.0.0",
                            "originSession": "session-1",
                            "originType": "REST",
                            "originXForwardedFor": "192.168.1.1",
                            "resourceId": "resource-1",
                            "environmentUuid": "environment-1",
                            "userOrganization": "CUSTOMER",
                        }
                    ],
                    "warnings": [{"message": "Your result has been limited to 1."}],
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        audits = await dt.account.audits.list(
            account_uuid,
            start_time=start_time,
            end_time=end_time,
            add_fields=["details", "eventOutcome"],
            filter="eventType = 'CREATE'",
            limit=25,
            scan_limit_gigabyte=10,
            result_size_limit_megabyte=5,
        )

    assert isinstance(audits, AuditsByAccount)
    assert len(audits.audits) == 1
    assert isinstance(audits.audits[0], Audit)
    assert audits.audits[0].resource_name == "Standard User"
    assert audits.audits[0].details["json_after"] == '{"enabled": true}'
    assert len(audits.warnings) == 1
    assert audits.warnings[0].message == "Your result has been limited to 1."
