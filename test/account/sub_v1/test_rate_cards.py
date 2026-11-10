import json
from typing import Any
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.sub_v1.rate_cards import RateCard, RateCardService
from dynatrace.http_client import HttpClient


class MockResponse:
    def __init__(self, json_data: Any = None) -> None:
        self._json_data = json_data
        self.headers: dict[str, str] = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = 200

    def json(self) -> Any:
        return self._json_data


async def test_rate_cards_service_is_exposed(dt: DynatraceAsync) -> None:
    assert isinstance(dt.account.sub_v1_rate_cards, RateCardService)


async def test_rate_cards_list_returns_models(dt: DynatraceAsync) -> None:
    account_uuid = "account-123"

    async def fake_make_request(
        self: Any,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        method: str = "GET",
        data: Any = None,
        files: Any = None,
        query_params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> MockResponse:
        if (method, path) == ("GET", f"/sub/v1/accounts/{account_uuid}/rate-cards"):
            return MockResponse(
                [
                    {
                        "quoteNumber": "quote-1",
                        "startTime": "2026-01-01T00:00:00Z",
                        "endTime": "2026-12-31T23:59:59Z",
                        "currencyCode": "USD",
                        "capabilities": [
                            {
                                "key": "metric",
                                "name": "Metrics",
                                "quotedPrice": "1.0",
                                "quotedUnitOfMeasure": "1",
                                "price": "1.0",
                            }
                        ],
                    }
                ]
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        rate_cards = await dt.account.sub_v1_rate_cards.list(account_uuid)

    assert isinstance(rate_cards, list)
    assert isinstance(rate_cards[0], RateCard)
    assert rate_cards[0].capabilities[0].name == "Metrics"
