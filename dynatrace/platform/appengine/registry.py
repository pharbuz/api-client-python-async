"""AppEngine Registry API wrappers."""

from pathlib import Path
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class AppEngineRegistryService:
    BASE_PATH = "/platform/app-engine/registry/v1"
    ENDPOINT_APPS = f"{BASE_PATH}/apps"
    ENDPOINT_SEARCH_ACTIONS = f"{BASE_PATH}/apps:search-actions"
    ENDPOINT_APP_MANIFEST_SCHEMA = f"{BASE_PATH}/app.manifest.schema.json"
    ENDPOINT_APP_DEFAULT_CSP = f"{BASE_PATH}/app.default.csp.json"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list_apps(
        self,
        add_fields: str | None = None,
        include_deactivated: bool | None = None,
        include_non_runnable: bool | None = None,
        include_all_app_versions: bool | None = None,
        filter_expression: str | None = None,
    ) -> "AppInfoList":
        """List installed apps."""
        params = {
            "add-fields": add_fields,
            "include-deactivated": include_deactivated,
            "include-non-runnable": include_non_runnable,
            "include-all-app-versions": include_all_app_versions,
            "filter": filter_expression,
        }
        response = await self.__http_client.make_request(
            self.ENDPOINT_APPS, params=params
        )
        return AppInfoList(self.__http_client, response.headers, response.json())

    async def install_app(
        self, app_bundle: str | Path | bytes | bytearray
    ) -> "AppStub":
        """Install or update an app from a zipped bundle."""
        bundle_data = self.__load_bundle_data(app_bundle)
        response = await self.__http_client.make_request(
            self.ENDPOINT_APPS,
            method="POST",
            headers={"Content-Type": "application/zip"},
            data=bundle_data,
        )
        return AppStub(self.__http_client, response.headers, response.json())

    async def search_actions(self, query: str | None = None) -> "SearchAppActionList":
        """Search actions of installed apps."""
        params = {"query": query}
        response = await self.__http_client.make_request(
            self.ENDPOINT_SEARCH_ACTIONS, params=params
        )
        return SearchAppActionList(
            self.__http_client, response.headers, response.json()
        )

    async def get_app(
        self,
        app_id: str,
        add_fields: str | None = None,
        latest_app_version: bool | None = None,
    ) -> "AppInfo":
        """Get details of an installed app."""
        params = {
            "add-fields": add_fields,
            "latest-app-version": latest_app_version,
        }
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT_APPS}/{app_id}", params=params
        )
        return AppInfo(self.__http_client, response.headers, response.json())

    async def uninstall_app(self, app_id: str) -> Response:
        """Uninstall an app."""
        return await self.__http_client.make_request(
            f"{self.ENDPOINT_APPS}/{app_id}", method="DELETE"
        )

    async def get_app_manifest_schema(self) -> dict[str, Any]:
        """Get JSON schema for app manifests."""
        response = await self.__http_client.make_request(
            self.ENDPOINT_APP_MANIFEST_SCHEMA
        )
        return response.json()

    async def get_default_csp_properties(self) -> "AppDefaultCsp":
        """Get default CSP rules for apps."""
        response = await self.__http_client.make_request(self.ENDPOINT_APP_DEFAULT_CSP)
        return AppDefaultCsp(self.__http_client, response.headers, response.json())

    @staticmethod
    def __load_bundle_data(app_bundle: str | Path | bytes | bytearray) -> bytes:
        if isinstance(app_bundle, (str, Path)):
            with open(Path(app_bundle), "rb") as file:
                return file.read()
        return bytes(app_bundle)


class Warning(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.message: str | None = raw_element.get("message")


class AppStub(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.warnings: list[Warning] = [
            Warning(raw_element=element) for element in raw_element.get("warnings", [])
        ]
        self.id: str | None = raw_element.get("id")


class AppIcon(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.href: str | None = raw_element.get("href")


class AppIsolatedUri(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.url: str | None = raw_element.get("url")
        self.base_url: str | None = raw_element.get("baseUrl")
        self.widget_url: str | None = raw_element.get("widgetUrl")


class AppSignatureInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.signed: bool | None = raw_element.get("signed")
        self.publisher: str | None = raw_element.get("publisher")


class ModificationInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.created_by: str | None = raw_element.get("createdBy")
        self.created_at: str | None = raw_element.get("createdAt")
        self.last_modified_by: str | None = raw_element.get("lastModifiedBy")
        self.last_modified_at: str | None = raw_element.get("lastModifiedAt")


class ResourceContext(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.operations: list[str] = raw_element.get("operations", [])


class SubResourceConstraintViolation(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.path: str | None = raw_element.get("path")
        self.message: str | None = raw_element.get("message")


class SubResourceError(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.message: str | None = raw_element.get("message")
        self.error_code: str | None = raw_element.get("errorCode")
        self.error_ref: str | None = raw_element.get("errorRef")
        self.constraint_violations: list[SubResourceConstraintViolation] = [
            SubResourceConstraintViolation(raw_element=element)
            for element in raw_element.get("constraintViolations", [])
        ]


class SubResourceStatus(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.sub_resource_type: str | None = raw_element.get("subResourceType")
        self.status: str | None = raw_element.get("status")
        self.error: SubResourceError | None = (
            SubResourceError(raw_element=raw_element.get("error"))
            if raw_element.get("error")
            else None
        )


class ResourceStatus(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.status: str | None = raw_element.get("status")
        self.sub_resource_types: list[str] = raw_element.get("subResourceTypes", [])
        self.sub_resource_statuses: list[SubResourceStatus] = [
            SubResourceStatus(raw_element=element)
            for element in raw_element.get("subResourceStatuses", [])
        ]
        self.pending_operation: str | None = raw_element.get("pendingOperation")
        self.operation_state_before_error: str | None = raw_element.get(
            "operationStateBeforeError"
        )


class AppInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.id: str | None = raw_element.get("id")
        self.name: str | None = raw_element.get("name")
        self.version: str | None = raw_element.get("version")
        self.description: str | None = raw_element.get("description")
        self.manifest: dict[str, Any] | None = raw_element.get("manifest")
        self.is_builtin: bool | None = raw_element.get("isBuiltin")
        self.resource_status: ResourceStatus | None = (
            ResourceStatus(raw_element=raw_element.get("resourceStatus"))
            if raw_element.get("resourceStatus")
            else None
        )
        self.app_icon: AppIcon | None = (
            AppIcon(raw_element=raw_element.get("appIcon"))
            if raw_element.get("appIcon")
            else None
        )
        self.isolated_uri: AppIsolatedUri | None = (
            AppIsolatedUri(raw_element=raw_element.get("isolatedUri"))
            if raw_element.get("isolatedUri")
            else None
        )
        self.signature_info: AppSignatureInfo | None = (
            AppSignatureInfo(raw_element=raw_element.get("signatureInfo"))
            if raw_element.get("signatureInfo")
            else None
        )
        self.modification_info: ModificationInfo | None = (
            ModificationInfo(raw_element=raw_element.get("modificationInfo"))
            if raw_element.get("modificationInfo")
            else None
        )
        self.deactivation_reasons: list[str] = raw_element.get(
            "deactivationReasons", []
        )
        self.resource_context: ResourceContext | None = (
            ResourceContext(raw_element=raw_element.get("resourceContext"))
            if raw_element.get("resourceContext")
            else None
        )


class AppInfoList(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.apps: list[AppInfo] = [
            AppInfo(raw_element=element) for element in raw_element.get("apps", [])
        ]


class SearchAppActionItem(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.name: str | None = raw_element.get("name")
        self.description: str | None = raw_element.get("description")


class SearchAppAction(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.id: str | None = raw_element.get("id")
        self.name: str | None = raw_element.get("name")
        self.actions: list[SearchAppActionItem] = [
            SearchAppActionItem(raw_element=element)
            for element in raw_element.get("actions", [])
        ]


class SearchAppActionList(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.apps: list[SearchAppAction] = [
            SearchAppAction(raw_element=element)
            for element in raw_element.get("apps", [])
        ]
        self.total_count: int | None = raw_element.get("totalCount")


class AppDefaultCsp(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.policy_directives: dict[str, list[str]] = raw_element.get(
            "policyDirectives", {}
        )
