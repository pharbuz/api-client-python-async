from collections.abc import Iterator
from typing import Any
from unittest import mock

import httpx
import pytest

from dynatrace import DynatraceAccessToken, DynatraceAsync
from dynatrace.http_client import HttpClient


def test_sanitize_params_removes_none_values() -> None:
    params = {
        "entitySelector": 'type("HOST")',
        "from": "now-3d",
        "to": None,
        "sort": None,
        "pageSize": 2,
    }

    sanitized = HttpClient._sanitize_params(params)

    assert sanitized == {
        "entitySelector": 'type("HOST")',
        "from": "now-3d",
        "pageSize": 2,
    }


@pytest.fixture
def sent_requests() -> Iterator[list[dict[str, Any]]]:
    """Capture what ``make_request`` hands to the transport layer."""
    sent: list[dict[str, Any]] = []

    async def fake_request_with_retries(
        self: HttpClient, **kwargs: Any
    ) -> httpx.Response:
        sent.append(kwargs)
        return httpx.Response(200, json={"items": []})

    with mock.patch.object(
        HttpClient, "_request_with_retries", new=fake_request_with_retries
    ):
        yield sent


def _client() -> HttpClient:
    return HttpClient("https://tenant", credentials=DynatraceAccessToken(token="t"))


def test_merge_query_params_combines_dicts_and_drops_none() -> None:
    merged = HttpClient._merge_query_params(
        {"a": 1, "b": None, "c": 3}, {"c": 30, "d": None, "e": 5}
    )

    assert merged == httpx.QueryParams({"a": 1, "c": 30, "e": 5})


@pytest.mark.parametrize(
    ("params", "query_params", "expected"),
    [
        (None, None, None),
        ({"a": 1}, None, {"a": 1}),
        (None, {"a": 1}, {"a": 1}),
        ({"a": None}, {"b": 2}, {"b": 2}),
    ],
)
def test_merge_query_params_handles_missing_values(
    params: Any, query_params: Any, expected: Any
) -> None:
    assert HttpClient._merge_query_params(params, query_params) == expected


async def test_make_request_merges_query_pairs_and_dict() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    http_client = httpx.AsyncClient(transport=transport)

    with mock.patch.object(HttpClient, "_create_client", return_value=http_client):
        async with _client() as client:
            response = await client.make_request(
                "/api/v2/path",
                params=[("tag", "first"), ("tag", "second"), ("limit", 10)],
                query_params={"limit": 20, "enabled": False, "skipped": None},
            )

    assert response.request.url.params.multi_items() == [
        ("tag", "first"),
        ("tag", "second"),
        ("limit", "20"),
        ("enabled", "false"),
    ]


@pytest.mark.parametrize("method", ["GET", "DELETE", "PATCH"])
async def test_query_params_are_sent_for_requests_without_body(
    sent_requests: list[dict[str, Any]], method: str
) -> None:
    await _client().make_request(
        "/api/v2/path",
        method=method,
        params={"pageSize": 10},
        query_params={"adminAccess": True, "skipped": None},
    )

    assert sent_requests[0]["request_params"] == httpx.QueryParams(
        {"pageSize": 10, "adminAccess": True}
    )
    assert sent_requests[0]["body"] is None


@pytest.mark.parametrize("method", ["POST", "PUT"])
async def test_post_and_put_send_params_as_body(
    sent_requests: list[dict[str, Any]], method: str
) -> None:
    await _client().make_request(
        "/api/v2/path",
        method=method,
        params={"value": 1},
        query_params={"validateOnly": True},
    )

    assert sent_requests[0]["request_params"] == {"validateOnly": True}
    assert sent_requests[0]["body"] == {"value": 1}


async def test_hub_list_items_sends_filters_as_query_params(
    sent_requests: list[dict[str, Any]],
) -> None:
    async with DynatraceAsync(
        "https://tenant", credentials=DynatraceAccessToken(token="t")
    ) as dt:
        await dt.hub.list_items(item_type="TECHNOLOGY", query="Azul", page_size=20)

    assert sent_requests[0]["url"] == "https://tenant/api/v2/hub/items"
    assert sent_requests[0]["request_params"] == {
        "pageSize": 20,
        "itemType": "TECHNOLOGY",
        "query": "Azul",
    }


async def test_settings_get_and_delete_send_query_params(
    sent_requests: list[dict[str, Any]],
) -> None:
    async with DynatraceAsync(
        "https://tenant", credentials=DynatraceAccessToken(token="t")
    ) as dt:
        await dt.settings.get_object("object-id", admin_access=True)
        await dt.settings.delete_object(
            "object-id", update_token="token", admin_access=False
        )

    assert sent_requests[0]["method"] == "GET"
    assert sent_requests[0]["request_params"] == {"adminAccess": True}
    assert sent_requests[1]["method"] == "DELETE"
    assert sent_requests[1]["request_params"] == {
        "updateToken": "token",
        "adminAccess": False,
    }


async def test_hub_list_items_sends_only_next_page_key_when_paging(
    sent_requests: list[dict[str, Any]],
) -> None:
    async with DynatraceAsync(
        "https://tenant", credentials=DynatraceAccessToken(token="t")
    ) as dt:
        await dt.hub.list_items(
            item_type="TECHNOLOGY", page_size=100, next_page_key="page-2"
        )

    assert sent_requests[0]["request_params"] == {"nextPageKey": "page-2"}
