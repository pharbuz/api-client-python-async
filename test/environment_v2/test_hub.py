from typing import Any
from unittest.mock import AsyncMock, patch

from dynatrace import DynatraceAsync
from dynatrace.environment_v2.hub import (
    Category,
    ExtensionReleaseNotes,
    ItemDetails,
    ItemOverview,
    RegisteredExtensionResult,
)
from dynatrace.http_client import HttpClient


class MockResponse:
    def __init__(self, payload: dict[str, Any] | None = None, content: bytes = b""):
        self._payload = payload or {}
        self.content = content

    def json(self) -> dict[str, Any]:
        return self._payload


async def test_hub_endpoints_use_expected_paths(dt: DynatraceAsync) -> None:
    make_request = AsyncMock(
        side_effect=[
            MockResponse(content=b"image"),
            MockResponse({"items": [{"id": "cloud", "name": "Cloud"}]}),
            MockResponse({"itemId": "extension1"}),
            MockResponse(content=b"artifact"),
            MockResponse({"itemId": "extension2"}),
            MockResponse({"extensionName": "ext", "extensionVersion": "1.0"}),
            MockResponse({"extensionName": "ext", "extensionVersion": "2.0"}),
            MockResponse(),
            MockResponse(),
            MockResponse({"items": [{"itemId": "item"}], "totalCount": 1}),
            MockResponse({"itemId": "technology"}),
        ]
    )
    request_patch = patch.object(HttpClient, "make_request", make_request)
    request_patch.start()

    assert await dt.hub.get_image("image-url") == b"image"
    categories = await dt.hub.list_categories()
    assert isinstance(categories.items[0], Category)
    assert (await dt.hub.get_extension1_details("extension1")).item_id == "extension1"
    assert await dt.hub.get_extension1_artifact("extension1", "1.0") == b"artifact"
    assert isinstance(await dt.hub.get_extension2_details("extension2"), ItemDetails)
    assert isinstance(
        await dt.hub.add_extension2_to_environment("ext"), RegisteredExtensionResult
    )
    assert isinstance(
        await dt.hub.update_extension2("ext", "2.0"), RegisteredExtensionResult
    )
    await dt.hub.upload_extension2_metadata("ext", description="Description")
    await dt.hub.update_extension2_release_notes(
        "ext", "2.0", ExtensionReleaseNotes("# Notes")
    )
    items = await dt.hub.list_items(page_size=10, item_type="EXTENSION2")
    assert isinstance(items.items[0], ItemOverview)
    assert (await dt.hub.get_technology_details("technology")).item_id == "technology"
    request_patch.stop()

    assert [call.args[0] for call in make_request.await_args_list] == [
        "/api/v2/hub/assets/images/image-url",
        "/api/v2/hub/categories",
        "/api/v2/hub/extensions1/extension1",
        "/api/v2/hub/extensions1/extension1/releases/1.0",
        "/api/v2/hub/extensions2/extension2",
        "/api/v2/hub/extensions2/ext/actions/addToEnvironment",
        "/api/v2/hub/extensions2/ext/actions/update",
        "/api/v2/hub/extensions2/ext/metadata",
        "/api/v2/hub/extensions2/ext/releases/2.0/releaseNotes",
        "/api/v2/hub/items",
        "/api/v2/hub/technologies/technology",
    ]

    assert make_request.await_args_list[5].kwargs == {
        "query_params": {"extensionVersion": None},
        "method": "POST",
    }
    assert make_request.await_args_list[8].kwargs == {
        "params": {"markdown": "# Notes"},
        "method": "PUT",
    }
