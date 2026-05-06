"""
Copyright 2021 Dynatrace LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging

from dynatrace.account.schemas import AccountAPI
from dynatrace.configuration_v1.alerting_profiles import AlertingProfileService
from dynatrace.configuration_v1.anomaly_detection_process_groups import (
    AnomalyDetectionPGService,
)
from dynatrace.configuration_v1.api import ConfigurationV1
from dynatrace.configuration_v1.auto_tags import AutoTagService
from dynatrace.configuration_v1.dashboard import DashboardService
from dynatrace.configuration_v1.extensions import ExtensionService
from dynatrace.configuration_v1.maintenance_windows import MaintenanceWindowService
from dynatrace.configuration_v1.management_zones import ManagementZoneService
from dynatrace.configuration_v1.metric_events import MetricEventService
from dynatrace.configuration_v1.notifications import NotificationService
from dynatrace.configuration_v1.oneagent_environment_wide_configuration import (
    OneAgentEnvironmentWideConfigService,
)
from dynatrace.configuration_v1.oneagent_in_a_hostgroup import (
    OneAgentInAHostGroupService,
)
from dynatrace.configuration_v1.oneagent_on_a_host import (
    OneAgentOnAHostService as OneAgentOnAHostConfigService,
)
from dynatrace.configuration_v1.plugins import PluginService
from dynatrace.environment_v1.cluster_time import ClusterTimeService
from dynatrace.environment_v1.custom_device import CustomDeviceService
from dynatrace.environment_v1.deployment import DeploymentService
from dynatrace.environment_v1.event import EventService
from dynatrace.environment_v1.oneagents import OneAgentOnAHostService
from dynatrace.environment_v1.smartscape_hosts import SmartScapeHostsService
from dynatrace.environment_v1.synthetic_monitors import SyntheticMonitorsService
from dynatrace.environment_v1.synthetic_third_party import (
    ThirdPartySyntheticTestsService,
)
from dynatrace.environment_v1.timeseries import TimeSerieService
from dynatrace.environment_v2.activegates import ActiveGateService
from dynatrace.environment_v2.activegates_autoupdate_configuration import (
    ActiveGateAutoUpdateConfigurationService,
)
from dynatrace.environment_v2.activegates_autoupdate_jobs import (
    ActiveGateAutoUpdateJobsService,
)
from dynatrace.environment_v2.audit_logs import AuditLogsService
from dynatrace.environment_v2.credential_vault import CredentialVaultService
from dynatrace.environment_v2.custom_tags import CustomTagService
from dynatrace.environment_v2.events import EventServiceV2
from dynatrace.environment_v2.extensions import ExtensionsServiceV2
from dynatrace.environment_v2.logs import LogService
from dynatrace.environment_v2.metrics import MetricService
from dynatrace.environment_v2.monitored_entities import EntityService
from dynatrace.environment_v2.networkzones import NetworkZoneService
from dynatrace.environment_v2.problems import ProblemService
from dynatrace.environment_v2.remote_configuration import (
    ActiveGatesRemoteConfigurationService,
    OneAgentsRemoteConfigurationService,
)
from dynatrace.environment_v2.security_problems import SecurityProblemService
from dynatrace.environment_v2.service_level_objectives import SloService
from dynatrace.environment_v2.settings import SettingService
from dynatrace.environment_v2.tokens_api import TokenService
from dynatrace.environment_v2.tokens_tenant import TenantTokenService
from dynatrace.http_client import HttpClient
from dynatrace.platform.schemas import PlatformAPI


class DynatraceAsync:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        account_uuid: str,
        scope: str = "account-uac-read",
        sso_base_url: str = "https://sso.dynatrace.com",
        base_url: str = "https://api.dynatrace.com",
        log: logging.Logger = None,
        proxies: dict = None,
        too_many_requests_strategy=None,
        retries: int = 0,
        retry_delay_ms: int = 0,
        mc_jsession_id: str | None = None,
        mc_b925d32c: str | None = None,
        mc_sso_csrf_cookie: str | None = None,
        print_bodies=False,
        timeout: int | None = None,
        headers: dict | None = None,
        verify_ssl: bool = False,
        token_timeout: int = 30,
    ):
        if not base_url:
            raise ValueError("base_url is required")
        if not client_id:
            raise ValueError("client_id is required")
        if not client_secret:
            raise ValueError("client_secret is required")
        if not account_uuid:
            raise ValueError("account_uuid is required")

        self.__http_client = HttpClient(
            base_url,
            client_id,
            client_secret,
            account_uuid,
            log,
            proxies,
            too_many_requests_strategy,
            retries,
            retry_delay_ms,
            mc_jsession_id,
            mc_b925d32c,
            mc_sso_csrf_cookie,
            print_bodies,
            timeout,
            headers,
            scope,
            sso_base_url,
            verify_ssl,
            token_timeout,
        )

        self.activegates: ActiveGateService = ActiveGateService(self.__http_client)
        self.activegates_autoupdate_configuration: (
            ActiveGateAutoUpdateConfigurationService
        ) = ActiveGateAutoUpdateConfigurationService(self.__http_client)
        self.activegates_autoupdate_jobs = ActiveGateAutoUpdateJobsService(
            self.__http_client
        )
        self.activegates_remote_configuration: ActiveGatesRemoteConfigurationService = (
            ActiveGatesRemoteConfigurationService(self.__http_client)
        )
        self.alerting_profiles: AlertingProfileService = AlertingProfileService(
            self.__http_client
        )
        self.anomaly_detection_metric_events = MetricEventService(self.__http_client)
        self.anomaly_detection_process_groups = AnomalyDetectionPGService(
            self.__http_client
        )
        self.audit_logs: AuditLogsService = AuditLogsService(self.__http_client)
        self.auto_tags: AutoTagService = AutoTagService(self.__http_client)
        self.cluster_time: ClusterTimeService = ClusterTimeService(self.__http_client)
        self.custom_devices: CustomDeviceService = CustomDeviceService(
            self.__http_client
        )
        self.custom_tags: CustomTagService = CustomTagService(self.__http_client)
        self.dashboards: DashboardService = DashboardService(self.__http_client)
        self.deployment: DeploymentService = DeploymentService(self.__http_client)
        self.entities: EntityService = EntityService(self.__http_client)
        self.events: EventService = EventService(self.__http_client)
        self.events_v2: EventServiceV2 = EventServiceV2(self.__http_client)
        self.extensions: ExtensionService = ExtensionService(self.__http_client)
        self.extensions_v2: ExtensionsServiceV2 = ExtensionsServiceV2(
            self.__http_client
        )
        self.logs: LogService = LogService(self.__http_client)
        self.maintenance_windows = MaintenanceWindowService(self.__http_client)
        self.management_zones: ManagementZoneService = ManagementZoneService(
            self.__http_client
        )
        self.metrics: MetricService = MetricService(self.__http_client)
        self.network_zones: NetworkZoneService = NetworkZoneService(self.__http_client)
        self.notifications: NotificationService = NotificationService(
            self.__http_client
        )
        self.oneagents: OneAgentOnAHostService = OneAgentOnAHostService(
            self.__http_client
        )
        self.oneagents_config_environment: OneAgentEnvironmentWideConfigService = (
            OneAgentEnvironmentWideConfigService(self.__http_client)
        )
        self.oneagents_config_host: OneAgentOnAHostConfigService = (
            OneAgentOnAHostConfigService(self.__http_client)
        )
        self.oneagents_config_hostgroup: OneAgentInAHostGroupService = (
            OneAgentInAHostGroupService(self.__http_client)
        )
        self.oneagents_remote_configuration: OneAgentsRemoteConfigurationService = (
            OneAgentsRemoteConfigurationService(self.__http_client)
        )
        self.settings: SettingService = SettingService(self.__http_client)
        self.plugins: PluginService = PluginService(self.__http_client)
        self.problems: ProblemService = ProblemService(self.__http_client)
        self.security_problems: SecurityProblemService = SecurityProblemService(
            self.__http_client
        )
        self.slos: SloService = SloService(self.__http_client)
        self.smartscape_hosts: SmartScapeHostsService = SmartScapeHostsService(
            self.__http_client
        )
        self.synthetic_monitors: SyntheticMonitorsService = SyntheticMonitorsService(
            self.__http_client
        )
        self.tenant_tokens = TenantTokenService(self.__http_client)
        self.third_part_synthetic_tests: ThirdPartySyntheticTestsService = (
            ThirdPartySyntheticTestsService(self.__http_client)
        )
        self.timeseries: TimeSerieService = TimeSerieService(self.__http_client)
        self.tokens: TokenService = TokenService(self.__http_client)
        self.credentials = CredentialVaultService(self.__http_client)
        self.platform: PlatformAPI = PlatformAPI(self.__http_client)
        self.account: AccountAPI = AccountAPI(self.__http_client)

        # New implementations should be done here, above is deprecated
        self.config_v1: ConfigurationV1 = ConfigurationV1(self.__http_client)

    async def aclose(self) -> None:
        await self.__http_client.aclose()

    async def __aenter__(self) -> "DynatraceAsync":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()
