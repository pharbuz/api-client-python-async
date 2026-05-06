import dynatrace.environment_v2.networkzones as nz
from dynatrace import DynatraceAsync
from dynatrace.pagination import PaginatedList
from test.async_utils import collect

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
