from dynatrace import DynatraceAsync


async def test_get_global(dt: DynatraceAsync):
    alert_profiles = await dt.activegates_autoupdate_configuration.get_global()
    assert alert_profiles.global_setting == "DISABLED"
    assert alert_profiles.metadata.cluster_version == "1.217.96.20210507-181038"
    assert alert_profiles.metadata.configuration_versions[0] == 1
    assert isinstance(alert_profiles.metadata.configuration_versions, list)


async def test_get(dt: DynatraceAsync):
    alert_profiles = await dt.activegates_autoupdate_configuration.get("1513404008")
    assert alert_profiles.setting == "ENABLED"
    assert alert_profiles.effective_setting == "ENABLED"
