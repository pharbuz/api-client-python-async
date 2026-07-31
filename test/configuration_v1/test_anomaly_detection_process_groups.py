from typing import Any

import pytest

from dynatrace import DynatraceAsync
from dynatrace.configuration_v1.anomaly_detection_process_groups import (
    AnomalyDetectionPG,
    AvailabilityMonitoringPG,
    Method,
)
from dynatrace.http_client import HttpClient
from test.async_utils import MockResponse

PROCESS_GROUP_ID = "PROCESS_GROUP-1234567890ABCDEF"


def test_anomaly_detection_pg_serializes_availability_monitoring() -> None:
    config = AnomalyDetectionPG.create(Method.MINIMUM_THRESHOLD, minimum_threshold=5)

    assert isinstance(config.availability_monitoring, AvailabilityMonitoringPG)
    assert config.availability_monitoring.method == Method.MINIMUM_THRESHOLD
    assert config.availability_monitoring.minimum_threshold == 5
    assert config.to_json() == {
        "availabilityMonitoring": {
            "method": "MINIMUM_THRESHOLD",
            "minimumThreshold": 5,
        }
    }


def test_anomaly_detection_pg_omits_threshold_when_method_does_not_use_it() -> None:
    config = AnomalyDetectionPG.create(Method.OFF)

    assert config.to_json() == {"availabilityMonitoring": {"method": "OFF"}}


async def test_process_group_anomaly_detection_service_uses_openapi_paths(
    dt: DynatraceAsync, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict[str, Any]] = []

    async def fake_make_request(
        self: HttpClient,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        method: str = "GET",
        data: Any = None,
        query_params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> MockResponse:
        calls.append({"path": path, "params": params, "method": method})
        return MockResponse({"availabilityMonitoring": {"method": "PROCESS_IMPACT"}})

    monkeypatch.setattr(HttpClient, "make_request", fake_make_request)

    config = AnomalyDetectionPG.create(Method.PROCESS_IMPACT)

    response = await dt.anomaly_detection_process_groups.get_configuration(
        PROCESS_GROUP_ID
    )
    await dt.anomaly_detection_process_groups.put_configuration(
        PROCESS_GROUP_ID, config
    )
    await dt.anomaly_detection_process_groups.validate_configuration(
        PROCESS_GROUP_ID, config
    )
    await dt.anomaly_detection_process_groups.delete_configuration(PROCESS_GROUP_ID)

    assert response.availability_monitoring is not None
    assert response.availability_monitoring.method == Method.PROCESS_IMPACT
    assert calls == [
        {
            "path": f"/api/config/v1/anomalyDetection/processGroups/{PROCESS_GROUP_ID}",
            "params": None,
            "method": "GET",
        },
        {
            "path": f"/api/config/v1/anomalyDetection/processGroups/{PROCESS_GROUP_ID}",
            "params": {"availabilityMonitoring": {"method": "PROCESS_IMPACT"}},
            "method": "PUT",
        },
        {
            "path": f"/api/config/v1/anomalyDetection/processGroups/{PROCESS_GROUP_ID}/validator",
            "params": {"availabilityMonitoring": {"method": "PROCESS_IMPACT"}},
            "method": "POST",
        },
        {
            "path": f"/api/config/v1/anomalyDetection/processGroups/{PROCESS_GROUP_ID}",
            "params": None,
            "method": "DELETE",
        },
    ]
