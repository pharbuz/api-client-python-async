from dynatrace import DynatraceAsync
from dynatrace.environment_v2.management_zones import (
    ManagementZoneDetails,
)

OBJECT_ID = "MANAGEMENT-ZONE-SETTING-ID"


async def test_get(dt: DynatraceAsync):
    management_zone_details = await dt.management_zones_v2.get(object_id=OBJECT_ID)

    assert isinstance(management_zone_details, ManagementZoneDetails)
    assert management_zone_details.id == "MANAGEMENT-ZONE-8E2ED64F4F19AC15"
