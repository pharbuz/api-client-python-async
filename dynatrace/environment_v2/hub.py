"""Client for the Environment API v2 Hub endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class HubService:
    """Provides access to Hub items available in an environment."""

    ENDPOINT = "/api/v2/hub"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def get_image(self, encoded_url: str) -> bytes:
        """Retrieves an image used in a Hub item."""
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/assets/images/{encoded_url}"
        )
        return response.content

    async def list_categories(self) -> CategoryList:
        """Lists the Hub categories available in the environment."""
        response = await self.__http_client.make_request(f"{self.ENDPOINT}/categories")
        return CategoryList(raw_element=response.json())

    async def get_extension1_details(self, extension_fqn: str) -> ItemDetails:
        """Gets details of an Extensions 1.0 Hub item."""
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/extensions1/{extension_fqn}"
        )
        return ItemDetails(raw_element=response.json())

    async def get_extension1_artifact(self, extension_fqn: str, version: str) -> bytes:
        """Downloads the artifact for an Extensions 1.0 Hub release."""
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/extensions1/{extension_fqn}/releases/{version}"
        )
        return response.content

    async def get_extension2_details(self, extension_name: str) -> ItemDetails:
        """Gets details of an Extensions 2.0 Hub item."""
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/extensions2/{extension_name}"
        )
        return ItemDetails(raw_element=response.json())

    async def add_extension2_to_environment(
        self, extension_name: str, extension_version: str | None = None
    ) -> RegisteredExtensionResult:
        """Registers an Extensions 2.0 release in the environment."""
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/extensions2/{extension_name}/actions/addToEnvironment",
            query_params={"extensionVersion": extension_version},
            method="POST",
        )
        return RegisteredExtensionResult(raw_element=response.json())

    async def update_extension2(
        self, extension_name: str, extension_version: str | None = None
    ) -> RegisteredExtensionResult:
        """Updates an Extensions 2.0 item to the requested or recommended release."""
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/extensions2/{extension_name}/actions/update",
            query_params={"extensionVersion": extension_version},
            method="POST",
        )
        return RegisteredExtensionResult(raw_element=response.json())

    async def upload_extension2_metadata(
        self,
        extension_name: str,
        description: str | None = None,
        logo_file_path: str | Path | None = None,
        name: str | None = None,
    ) -> Response:
        """Creates or replaces metadata for a non-distributed Extensions 2.0 item."""
        files: dict[str, Any] = {}
        if description is not None:
            files["description"] = (None, description)
        if name is not None:
            files["name"] = (None, name)

        if logo_file_path is None:
            return await self.__http_client.make_request(
                f"{self.ENDPOINT}/extensions2/{extension_name}/metadata",
                method="PUT",
                files=files,
            )

        with Path(logo_file_path).open("rb") as logo:
            files["logo"] = logo
            return await self.__http_client.make_request(
                f"{self.ENDPOINT}/extensions2/{extension_name}/metadata",
                method="PUT",
                files=files,
            )

    async def update_extension2_release_notes(
        self, extension_name: str, version: str, release_notes: ExtensionReleaseNotes
    ) -> Response:
        """Sets or updates the release notes of an Extensions 2.0 release."""
        return await self.__http_client.make_request(
            f"{self.ENDPOINT}/extensions2/{extension_name}/releases/{version}/releaseNotes",
            params=release_notes.to_json(),
            method="PUT",
        )

    async def list_items(
        self,
        page_size: int | None = None,
        item_type: str | None = None,
        query: str | None = None,
        installed: bool | None = None,
        category_id: str | None = None,
        offset: str | None = None,
        next_page_key: str | None = None,
    ) -> ItemList:
        """Lists Hub items available in the environment."""
        params = {
            "pageSize": page_size,
            "itemType": item_type,
            "query": query,
            "installed": installed,
            "categoryId": category_id,
            "offset": offset,
            "nextPageKey": next_page_key,
        }
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/items", query_params=params
        )
        return ItemList(raw_element=response.json())

    async def get_technology_details(self, slug: str) -> ItemDetails:
        """Gets details of a technology Hub item."""
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/technologies/{slug}"
        )
        return ItemDetails(raw_element=response.json())


class Category(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.id: str | None = raw_element.get("id")
        self.name: str | None = raw_element.get("name")
        self.description: str | None = raw_element.get("description")


class CategoryList(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.items: list[Category] = [
            Category(raw_element=item) for item in raw_element.get("items", [])
        ]


class Image(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.alt: str | None = raw_element.get("alt")
        self.src: str | None = raw_element.get("src")
        self.title: str | None = raw_element.get("title")


class DescriptionBlock(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.images: list[Image] | None = (
            [Image(raw_element=image) for image in raw_element["images"]]
            if raw_element.get("images") is not None
            else None
        )
        self.source: str | None = raw_element.get("source")
        self.source_id: str | None = raw_element.get("sourceId")
        self.title: str | None = raw_element.get("title")
        self.type: str | None = raw_element.get("type")


class Extension1Release(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.artifact_sha256: str | None = raw_element.get("artifactSha256")
        self.artifact_title: str | None = raw_element.get("artifactTitle")
        self.release_notes: str | None = raw_element.get("releaseNotes")
        self.version: str | None = raw_element.get("version")


class Extension1Details(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.releases: list[Extension1Release] = [
            Extension1Release(raw_element=release)
            for release in raw_element.get("releases", [])
        ]


class ExtensionRelease(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.active: bool | None = raw_element.get("active")
        self.artifact_sha256: str | None = raw_element.get("artifactSha256")
        self.assets_info: list[dict[str, Any]] = raw_element.get("assetsInfo", [])
        self.configured_feature_sets: list[str] = raw_element.get(
            "configuredFeatureSets", []
        )
        self.data_sources: list[str] = raw_element.get("dataSources", [])
        self.distributed: bool | None = raw_element.get("distributed")
        self.feature_sets: dict[str, Any] = raw_element.get("featureSets", {})
        self.min_cluster_version: int | None = raw_element.get("minClusterVersion")
        self.registered: bool | None = raw_element.get("registered")
        self.release_notes: str | None = raw_element.get("releaseNotes")
        self.unpublished: bool | None = raw_element.get("unpublished")
        self.unpublished_description: str | None = raw_element.get(
            "unpublishedDescription"
        )
        self.unpublished_severity: int | None = raw_element.get("unpublishedSeverity")
        self.version: str | None = raw_element.get("version")


class Extension2Details(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.distributed: bool | None = raw_element.get("distributed")
        self.extension_name: str | None = raw_element.get("extensionName")
        self.recommended_catalog_version: str | None = raw_element.get(
            "recommendedCatalogVersion"
        )
        self.releases: list[ExtensionRelease] = [
            ExtensionRelease(raw_element=release)
            for release in raw_element.get("releases", [])
        ]


class TechnologyDetails(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.activation_link: str | None = raw_element.get("activationLink")


class RelatedItem(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.description: str | None = raw_element.get("description")
        self.external_link: str | None = raw_element.get("externalLink")
        self.has_cluster_link: bool | None = raw_element.get("hasClusterLink")
        self.icon_url: str | None = raw_element.get("iconUrl")
        self.id: str | None = raw_element.get("id")
        self.name: str | None = raw_element.get("name")
        self.type: str | None = raw_element.get("type")


class ItemOverview(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.activation_link: str | None = raw_element.get("activationLink")
        self.artifact_id: str | None = raw_element.get("artifactId")
        self.author_logo: str | None = raw_element.get("authorLogo")
        self.author_name: str | None = raw_element.get("authorName")
        self.cluster_compatible: bool | None = raw_element.get("clusterCompatible")
        self.coming_soon: bool | None = raw_element.get("comingSoon")
        self.description: str | None = raw_element.get("description")
        self.documentation_link: str | None = raw_element.get("documentationLink")
        self.has_description_blocks: bool | None = raw_element.get(
            "hasDescriptionBlocks"
        )
        self.item_id: str | None = raw_element.get("itemId")
        self.logo: str | None = raw_element.get("logo")
        self.marketing_link: str | None = raw_element.get("marketingLink")
        self.name: str | None = raw_element.get("name")
        self.not_compatible_reason: str | None = raw_element.get("notCompatibleReason")
        self.tags: list[str] = raw_element.get("tags", [])
        self.type: str | None = raw_element.get("type")


class ItemDetails(ItemOverview):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.cluster_max_version: int | None = raw_element.get("clusterMaxVersion")
        self.cluster_min_version: int | None = raw_element.get("clusterMinVersion")
        self.description_blocks: list[DescriptionBlock] = [
            DescriptionBlock(raw_element=block)
            for block in raw_element.get("descriptionBlocks", [])
        ]
        extension1_details = raw_element.get("extension1Details")
        self.extension1_details: Extension1Details | None = (
            Extension1Details(raw_element=extension1_details)
            if extension1_details is not None
            else None
        )
        extension2_details = raw_element.get("extension2Details")
        self.extension2_details: Extension2Details | None = (
            Extension2Details(raw_element=extension2_details)
            if extension2_details is not None
            else None
        )
        self.related_items: list[RelatedItem] = [
            RelatedItem(raw_element=item)
            for item in raw_element.get("relatedItems", [])
        ]
        technology_details = raw_element.get("technologyDetails")
        self.technology_details: TechnologyDetails | None = (
            TechnologyDetails(raw_element=technology_details)
            if technology_details is not None
            else None
        )


class ItemList(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.items: list[ItemOverview] = [
            ItemOverview(raw_element=item) for item in raw_element.get("items", [])
        ]
        self.next_page_key: str | None = raw_element.get("nextPageKey")
        self.page_size: int | None = raw_element.get("pageSize")
        self.total_count: int | None = raw_element.get("totalCount")


class RegisteredExtensionResult(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.extension_name: str | None = raw_element.get("extensionName")
        self.extension_version: str | None = raw_element.get("extensionVersion")


class ExtensionReleaseNotes:
    """Markdown release notes for an Extensions 2.0 release."""

    def __init__(self, markdown: str):
        self.markdown = markdown

    def to_json(self) -> dict[str, str]:
        return {"markdown": self.markdown}
