import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.env_v2.settings import (
    EffectiveSettingsValue,
    FieldValue,
    FieldValuesPage,
    FieldValuesRequest,
    SettingService,
)
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from test.async_utils import collect


class MockResponse:
    def __init__(self, json_data=None):
        self._json_data = json_data
        self.headers = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = 200

    def json(self):
        return self._json_data


async def test_env_v2_settings_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.settings, SettingService)


async def test_env_v2_settings_list_effective_values(dt: DynatraceAsync):
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
        if (method, path) == ("GET", "/api/v2/settings/effectiveValues"):
            return MockResponse(
                {
                    "items": [
                        {
                            "author": "author-1",
                            "created": 1710000000000,
                            "createdBy": "user-1",
                            "externalId": "ext-1",
                            "modified": 1710000100000,
                            "modifiedBy": "user-2",
                            "origin": "ENVIRONMENT",
                            "schemaId": "builtin:test",
                            "schemaVersion": "1.0.0",
                            "searchSummary": "summary",
                            "summary": "effective",
                            "value": {"enabled": True},
                        }
                    ],
                    "totalCount": 1,
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        effective_values = await dt.account.settings.list_effective_values(
            scope="environment"
        )

    assert isinstance(effective_values, PaginatedList)
    effective_values_list = await collect(effective_values)
    assert len(effective_values_list) == 1
    assert isinstance(effective_values_list[0], EffectiveSettingsValue)
    assert effective_values_list[0].schema_id == "builtin:test"


async def test_account_settings_costcenters_and_products(dt: DynatraceAsync):
    account_uuid = "account-123"

    async def fake_make_request(
        self,
        path,
        params=None,
        headers=None,
        method="GET",
        data=None,
        files=None,
        query_params=None,
        json=None,
        **kwargs,
    ):
        if (method, path) == (
            "GET",
            f"/v1/accounts/{account_uuid}/settings/costcenters",
        ):
            assert params == {"page": 2, "page-size": 50}
            return MockResponse(
                {
                    "records": [{"key": "costcenter-1"}, {"key": "costcenter-2"}],
                    "hasNextPage": False,
                }
            )

        if (method, path) == (
            "POST",
            f"/v1/accounts/{account_uuid}/settings/costcenters",
        ):
            assert json == {"values": [{"key": "costcenter-3"}]}
            return MockResponse()

        if (method, path) == (
            "PUT",
            f"/v1/accounts/{account_uuid}/settings/costcenters",
        ):
            assert json == {"values": [{"key": "costcenter-4"}]}
            return MockResponse()

        if (method, path) == (
            "DELETE",
            f"/v1/accounts/{account_uuid}/settings/costcenters/costcenter-1",
        ):
            return MockResponse()

        if (method, path) == (
            "GET",
            f"/v1/accounts/{account_uuid}/settings/products",
        ):
            assert params == {"page": None, "page-size": None}
            return MockResponse(
                {
                    "records": [{"key": "product-1"}],
                    "hasNextPage": True,
                }
            )

        if (method, path) == (
            "POST",
            f"/v1/accounts/{account_uuid}/settings/products",
        ):
            assert json == {"values": [{"key": "product-2"}]}
            return MockResponse()

        if (method, path) == (
            "PUT",
            f"/v1/accounts/{account_uuid}/settings/products",
        ):
            assert json == {"values": [{"key": "product-3"}]}
            return MockResponse()

        if (method, path) == (
            "DELETE",
            f"/v1/accounts/{account_uuid}/settings/products/product-1",
        ):
            return MockResponse()

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        costcenters = await dt.account.settings.list_costcenters(
            account_uuid, page=2, page_size=50
        )
        add_costcenters_response = await dt.account.settings.add_costcenters(
            account_uuid, ["costcenter-3"]
        )
        replace_costcenters_response = await dt.account.settings.replace_costcenters(
            account_uuid, FieldValuesRequest(values=[FieldValue(key="costcenter-4")])
        )
        delete_costcenter_response = await dt.account.settings.delete_costcenter(
            account_uuid, "costcenter-1"
        )
        products = await dt.account.settings.list_products(account_uuid)
        add_products_response = await dt.account.settings.add_products(
            account_uuid, {"values": [{"key": "product-2"}]}
        )
        replace_products_response = await dt.account.settings.replace_products(
            account_uuid, [FieldValue(key="product-3")]
        )
        delete_product_response = await dt.account.settings.delete_product(
            account_uuid, "product-1"
        )

    assert isinstance(costcenters, FieldValuesPage)
    assert [record.key for record in costcenters.records] == [
        "costcenter-1",
        "costcenter-2",
    ]
    assert costcenters.has_next_page is False
    assert add_costcenters_response.status_code == 200
    assert replace_costcenters_response.status_code == 200
    assert delete_costcenter_response.status_code == 200
    assert isinstance(products.records[0], FieldValue)
    assert products.records[0].key == "product-1"
    assert products.has_next_page is True
    assert add_products_response.status_code == 200
    assert replace_products_response.status_code == 200
    assert delete_product_response.status_code == 200
