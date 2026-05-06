import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.http_client import HttpClient
from dynatrace.platform.appengine.registry import (
    AppDefaultCsp,
    AppEngineRegistryService,
    AppInfoList,
    AppStub,
    SearchAppActionList,
)


class MockResponse:
    def __init__(self, json_data=None, text=None):
        self._json_data = json_data
        self.headers = {}
        self.text = (
            text
            if text is not None
            else json.dumps(json_data) if json_data is not None else ""
        )
        self.status_code = 200

    def json(self):
        return self._json_data


async def test_appengine_registry_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.platform.appengine_registry, AppEngineRegistryService)


async def test_appengine_registry_endpoints(dt: DynatraceAsync):
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
        if (method, path) == ("GET", "/platform/app-engine/registry/v1/apps"):
            assert params["include-all-app-versions"] is True
            return MockResponse(
                {
                    "apps": [
                        {
                            "id": "my.example.appid",
                            "name": "Example app",
                            "version": "1.0.0",
                            "description": "Example description",
                            "resourceStatus": {"status": "OK"},
                            "signatureInfo": {"signed": True, "publisher": "Dynatrace"},
                            "modificationInfo": {
                                "createdBy": "user-1",
                                "createdAt": "2026-01-01T00:00:00.000Z",
                                "lastModifiedBy": "user-1",
                                "lastModifiedAt": "2026-01-01T00:00:00.000Z",
                            },
                        }
                    ]
                }
            )

        if (method, path) == ("POST", "/platform/app-engine/registry/v1/apps"):
            assert headers["Content-Type"] == "application/zip"
            assert data == b"zip-bundle"
            return MockResponse({"id": "my.example.appid", "warnings": []})

        if (method, path) == (
            "GET",
            "/platform/app-engine/registry/v1/apps:search-actions",
        ):
            assert params["query"] == "example"
            return MockResponse(
                {
                    "apps": [
                        {
                            "id": "my.example.appid",
                            "name": "Example app",
                            "actions": [
                                {
                                    "name": "example-action",
                                    "description": "Description of an example action.",
                                }
                            ],
                        }
                    ],
                    "totalCount": 1,
                }
            )

        if (
            method,
            path,
        ) == ("GET", "/platform/app-engine/registry/v1/apps/my.example.appid"):
            assert params["latest-app-version"] is True
            return MockResponse(
                {
                    "id": "my.example.appid",
                    "name": "Example app",
                    "version": "1.0.0",
                    "description": "Example description",
                    "resourceStatus": {"status": "OK"},
                    "signatureInfo": {"signed": True},
                    "modificationInfo": {
                        "createdBy": "user-1",
                        "createdAt": "2026-01-01T00:00:00.000Z",
                        "lastModifiedBy": "user-1",
                        "lastModifiedAt": "2026-01-01T00:00:00.000Z",
                    },
                    "resourceContext": {"operations": ["run", "update"]},
                }
            )

        if (
            method,
            path,
        ) == ("DELETE", "/platform/app-engine/registry/v1/apps/my.example.appid"):
            return MockResponse(None, text="accepted")

        if (method, path) == (
            "GET",
            "/platform/app-engine/registry/v1/app.manifest.schema.json",
        ):
            return MockResponse({"$schema": "https://json-schema.org/draft-07/schema#"})

        if (method, path) == (
            "GET",
            "/platform/app-engine/registry/v1/app.default.csp.json",
        ):
            return MockResponse({"policyDirectives": {"default-src": ["'self'"]}})

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        apps = await dt.platform.appengine_registry.list_apps(
            include_all_app_versions=True
        )
        installed = await dt.platform.appengine_registry.install_app(b"zip-bundle")
        actions = await dt.platform.appengine_registry.search_actions("example")
        app = await dt.platform.appengine_registry.get_app(
            "my.example.appid", latest_app_version=True
        )
        uninstall_response = await dt.platform.appengine_registry.uninstall_app(
            "my.example.appid"
        )
        manifest_schema = await dt.platform.appengine_registry.get_app_manifest_schema()
        default_csp = await dt.platform.appengine_registry.get_default_csp_properties()

    assert isinstance(apps, AppInfoList)
    assert apps.apps[0].name == "Example app"
    assert isinstance(installed, AppStub)
    assert installed.id == "my.example.appid"
    assert isinstance(actions, SearchAppActionList)
    assert actions.total_count == 1
    assert app.resource_context is not None
    assert app.resource_context.operations == ["run", "update"]
    assert uninstall_response.text == "accepted"
    assert manifest_schema["$schema"] == "https://json-schema.org/draft-07/schema#"
    assert isinstance(default_csp, AppDefaultCsp)
    assert default_csp.policy_directives["default-src"] == ["'self'"]
