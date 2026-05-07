import json
from datetime import datetime, timezone
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.notifications import (
    Notification,
    NotificationDetails,
    NotificationList,
    NotificationService,
    NotificationSeverity,
    NotificationSortField,
    NotificationType,
)
from dynatrace.http_client import HttpClient


class MockResponse:
    def __init__(self, json_data=None):
        self._json_data = json_data
        self.headers = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = 200

    def json(self):
        return self._json_data


async def test_notifications_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.notifications, NotificationService)


async def test_notifications_list_returns_models(dt: DynatraceAsync):
    account_uuid = "account-123"
    start_date_time = datetime(2025, 12, 1, 10, 0, tzinfo=timezone.utc)
    end_date_time = datetime(2025, 12, 31, 23, 59, tzinfo=timezone.utc)

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
        expected_body = {
            "startDateTime": "2025-12-01T10:00:00.000",
            "endDateTime": "2025-12-31T23:59:00.000",
            "types": ["BUDGET", "BYOK_REVOKED"],
            "severities": ["WARN", "INFO"],
            "capabilities": ["LOG_MANAGEMENT_ANALYZE"],
            "environments": ["abc12345"],
            "page": 1,
            "pageSize": 20,
            "sorts": ["-date"],
        }
        if (method, path) == ("POST", f"/v1/accounts/{account_uuid}/notifications"):
            assert params == expected_body
            return MockResponse(
                {
                    "records": [
                        {
                            "key": "budget-key-example",
                            "accountUuid": account_uuid,
                            "message": "Message for budget 0 0",
                            "severity": "WARN",
                            "type": "budget",
                            "details": {
                                "environments": ["env-uuid"],
                                "capabilities": ["cap1"],
                                "allEnvironments": False,
                                "allCapabilities": True,
                            },
                            "date": "2025-12-14T10:02:09.297Z",
                        },
                        {
                            "key": "byok-key-example",
                            "accountUuid": account_uuid,
                            "message": "BYOK event message",
                            "severity": "WARN",
                            "type": "byok-revoked",
                            "details": {
                                "environmentUuid": "env-uuid",
                                "keyName": "key-name",
                            },
                            "date": "2025-12-14T10:02:09.297Z",
                        },
                    ],
                    "totalRecordCount": 2,
                    "hasNextPage": False,
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        notifications = await dt.account.notifications.list(
            account_uuid,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            types=[NotificationType.BUDGET, NotificationType.BYOK_REVOKED],
            severities=[NotificationSeverity.WARN, NotificationSeverity.INFO],
            capabilities=["LOG_MANAGEMENT_ANALYZE"],
            environments=["abc12345"],
            page=1,
            page_size=20,
            sorts=[NotificationSortField.DATE_DESC],
        )

    assert isinstance(notifications, NotificationList)
    assert len(notifications.records) == 2
    assert isinstance(notifications.records[0], Notification)
    assert isinstance(notifications.records[0].details, NotificationDetails)
    assert notifications.records[0].details.capabilities == ["cap1"]
    assert notifications.records[1].details.key_name == "key-name"
    assert notifications.total_record_count == 2
    assert notifications.has_next_page is False
