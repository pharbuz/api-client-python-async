from dynatrace import DynatraceAsync
from dynatrace.environment_v2.settings import (
    EffectiveSettingsValue,
    SchemaStub,
    SettingsObject,
    SettingsObjectCreate,
    SettingsObjectUpdate,
)
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from test.async_utils import MockResponse, collect

settings_dict = {
    "enabled": True,
    "summary": "DT API TEST 22",
    "queryDefinition": {
        "type": "METRIC_KEY",
        "metricKey": "netapp.ontap.node.fru.state",
        "aggregation": "AVG",
        "entityFilter": {
            "dimensionKey": "dt.entity.netapp_ontap:fru",
            "conditions": [],
        },
        "dimensionFilter": [],
    },
    "modelProperties": {
        "type": "STATIC_THRESHOLD",
        "threshold": 100.0,
        "alertOnNoData": False,
        "alertCondition": "BELOW",
        "violatingSamples": 3,
        "samples": 5,
        "dealertingSamples": 5,
    },
    "eventTemplate": {
        "title": "OnTap {dims:type} {dims:fru_id} is in Error State",
        "description": "OnTap field replaceable unit (FRU) {dims:type} with id {dims:fru_id} on node {dims:node} in cluster {dims:cluster} is in an error state.\n",
        "eventType": "RESOURCE",
        "davisMerge": True,
        "metadata": [],
    },
    "eventEntityDimensionKey": "dt.entity.netapp_ontap:fru",
}
settings_object = SettingsObjectCreate(
    "builtin:anomaly-detection.metric-events", settings_dict, "environment"
)
settings_object_update = SettingsObjectUpdate(settings_dict)
test_object_id = "vu9U3hXa3q0AAAABACdidWlsdGluOmFub21hbHktZGV0ZWN0aW9uLm1ldHJpYy1ldmVudHMABnRlbmFudAAGdGVuYW50ACRiYmYzZWNhNy0zMmZmLTM2ZTEtOTFiOS05Y2QxZjE3OTc0YjC-71TeFdrerQ"


async def test_list_schemas(dt: DynatraceAsync):
    schemas = await dt.settings.list_schemas()
    assert isinstance(schemas, PaginatedList)
    schema_list = await collect(schemas)
    assert len(schema_list) == 3
    assert all(isinstance(s, SchemaStub) for s in schema_list)


async def test_list_objects(dt: DynatraceAsync):
    settings = await dt.settings.list_objects(
        schema_id="builtin:anomaly-detection.metric-events"
    )
    assert isinstance(settings, PaginatedList)
    settings_list = await collect(settings)
    assert len(settings_list) == 2
    assert all(isinstance(s, SettingsObject) for s in settings_list)


async def test_list_effective_values(dt: DynatraceAsync, monkeypatch):
    async def make_request(
        self,
        path: str,
        params: dict | None = None,
        headers: dict | None = None,
        method="GET",
        data=None,
        query_params=None,
        **kwargs,
    ):
        assert path == "/api/v2/settings/effectiveValues"
        return MockResponse(
            {
                "items": [
                    {
                        "author": "Alice",
                        "created": 1710000000000,
                        "createdBy": "user-1",
                        "externalId": "external-1",
                        "modified": 1710001000000,
                        "modifiedBy": "user-2",
                        "origin": "USER",
                        "schemaId": "builtin:anomaly-detection.metric-events",
                        "schemaVersion": "1.0.0",
                        "searchSummary": "summary",
                        "summary": "effective value",
                        "value": {"enabled": True},
                    }
                ],
                "totalCount": 1,
            }
        )

    monkeypatch.setattr(HttpClient, "make_request", make_request)

    effective_values = await dt.settings.list_effective_values(scope="environment")

    assert isinstance(effective_values, PaginatedList)
    effective_values_list = await collect(effective_values)
    assert len(effective_values_list) == 1
    assert all(isinstance(v, EffectiveSettingsValue) for v in effective_values_list)
    assert (
        effective_values_list[0].schema_id == "builtin:anomaly-detection.metric-events"
    )
    assert effective_values_list[0].value == {"enabled": True}


async def test_get_object(dt: DynatraceAsync):
    setting = await dt.settings.get_object(object_id=test_object_id)
    assert isinstance(setting, SettingsObject)
    assert setting.schema_version == "1.0.16"


async def test_post_object(dt: DynatraceAsync):
    response = await dt.settings.create_object(body=settings_object)
    assert response[0].get("code") == 200


async def test_put_object(dt: DynatraceAsync):
    response = await dt.settings.update_object(test_object_id, settings_object_update)
    print(response)
