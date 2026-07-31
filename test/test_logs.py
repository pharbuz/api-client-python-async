from datetime import datetime, timezone

from dynatrace import DynatraceAsync
from dynatrace.environment_v2.logs import (
    AggregatedLog,
    EventType,
    LogRecord,
    LogRecordStatus,
)
from dynatrace.pagination import PaginatedList
from test.async_utils import MockResponse, collect


async def test_export(dt: DynatraceAsync):
    logs = await dt.logs.export(time_from="now-10m")
    assert isinstance(logs, PaginatedList)

    logs_list = await collect(logs)
    assert len(logs_list) == 18

    first = logs_list[0]
    assert isinstance(first, LogRecord)
    assert first.additional_columns is not None
    assert first.additional_columns["dt.extension.ds"][0] == "python"
    assert first.content.startswith("Failed to assign")
    assert first.event_type == EventType.SFM
    assert first.status == LogRecordStatus.ERROR
    assert first.timestamp == datetime.fromtimestamp(1683574915193 / 1000, timezone.utc)


async def test_search(dt: DynatraceAsync, monkeypatch):
    calls = []
    responses = iter(
        [
            MockResponse(
                {
                    "results": [
                        {
                            "timestamp": 1683574915193,
                            "content": "first slice",
                            "eventType": "SFM",
                            "status": "ERROR",
                            "additionalColumns": {},
                        }
                    ],
                    "nextSliceKey": "slice-2",
                }
            ),
            MockResponse(
                {
                    "results": [
                        {
                            "timestamp": 1683574915194,
                            "content": "second slice",
                            "eventType": "LOG",
                            "status": "INFO",
                            "additionalColumns": {},
                        }
                    ]
                }
            ),
        ]
    )

    async def fake_make_request(
        path,
        params=None,
        headers=None,
        method="GET",
        data=None,
        files=None,
        query_params=None,
        **kwargs,
    ):
        calls.append({"path": path, "params": params, "method": method})
        return next(responses)

    monkeypatch.setattr(
        dt._DynatraceAsync__http_client, "make_request", fake_make_request
    )

    records = await dt.logs.search(query='content:"slice"', limit=1)

    assert len(records) == 2
    assert isinstance(records[0], LogRecord)
    assert records[0].content == "first slice"
    assert records[1].content == "second slice"
    assert calls[0]["path"] == "/api/v2/logs/search"
    assert calls[0]["params"]["limit"] == 1
    assert calls[1]["params"] == {"nextSliceKey": "slice-2"}


async def test_aggregate(dt: DynatraceAsync, monkeypatch):
    async def fake_make_request(
        path,
        params=None,
        headers=None,
        method="GET",
        data=None,
        files=None,
        query_params=None,
        **kwargs,
    ):
        return MockResponse(
            {
                "aggregationResult": {
                    "logLevel": {"1683574915": {"ERROR": 3, "INFO": 1}}
                },
                "warnings": "",
            }
        )

    monkeypatch.setattr(
        dt._DynatraceAsync__http_client, "make_request", fake_make_request
    )

    aggregate = await dt.logs.aggregate(query='content:"slice"', time_buckets=1)

    assert isinstance(aggregate, AggregatedLog)
    assert aggregate.aggregation_result is not None
    assert aggregate.aggregation_result["logLevel"]["1683574915"]["ERROR"] == 3
