import dynatrace.environment_v2.networkzones as nz
from dynatrace import DynatraceAsync
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from test.async_utils import MockResponse, collect

NETWORKZONE_ID = "default"


async def test_list(dt: DynatraceAsync):
    network_zones = await dt.network_zones.list()

    # type checks
    assert isinstance(network_zones, PaginatedList)
    zones = await collect(network_zones)
    assert len(zones) == 2
    assert all(isinstance(n, nz.NetworkZone) for n in zones)


async def test_get(dt: DynatraceAsync):
    network_zone = await dt.network_zones.get(networkzone_id=NETWORKZONE_ID)

    # type checks
    assert isinstance(network_zone, nz.NetworkZone)
    assert isinstance(network_zone.alternative_zones, list)

    # value checks
    assert (
        network_zone.description
        == "The default network zone. This is the network zone for OneAgents or ActiveGates that do not have any network zone configured."
    )
    assert network_zone.id == "default"
    assert network_zone.num_configured_activegates == 0
    assert network_zone.num_oneagents_configured == 141
    assert network_zone.num_oneagents_using == 141
    assert network_zone.num_oneagents_from_other_zones == 0


async def test_get_global_config(dt: DynatraceAsync, monkeypatch):
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
        assert path == "/api/v2/networkZoneSettings"
        return MockResponse({"networkZonesEnabled": True})

    monkeypatch.setattr(HttpClient, "make_request", make_request)

    settings = await dt.network_zones.get_global_config()

    assert isinstance(settings, nz.NetworkZoneSettings)
    assert settings.network_zones_enabled is True


async def test_get_host_statistics(dt: DynatraceAsync, monkeypatch):
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
        assert path == "/api/v2/networkZones/default/hostConnectionStatistics"
        assert params == {"filter": "all"}
        return MockResponse(
            {
                "hostsConfiguredButNotConnected": ["host-1"],
                "hostsConnectedAsAlternative": ["host-2"],
                "hostsConnectedAsFailover": ["host-3"],
                "hostsConnectedAsFailoverWithoutActiveGates": ["host-4"],
            }
        )

    monkeypatch.setattr(HttpClient, "make_request", make_request)

    statistics = await dt.network_zones.get_host_statistics(
        networkzone_id=NETWORKZONE_ID,
        filter="all",
    )

    assert isinstance(statistics, nz.NetworkZoneConnectionStatistics)
    assert statistics.hosts_configured_but_not_connected == ["host-1"]
    assert statistics.hosts_connected_as_alternative == ["host-2"]
    assert statistics.hosts_connected_as_failover == ["host-3"]
    assert statistics.hosts_connected_as_failover_without_active_gates == ["host-4"]
