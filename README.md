# dt-async - Dynatrace Python API Client

**dt-async** is a Python client for the [Dynatrace Rest API].   
It focuses on ease of use and nice type hints, perfect to explore the API and create quick scripts

This project is a modified fork of the original library released by Dynatrace.

[Dynatrace Rest API]: https://www.dynatrace.com/support/help/dynatrace-api

## Install

```bash
$ pip install dt-async
```

## Authentication

This library uses OAuth 2.0 client credentials flow for authentication.

When creating `DynatraceAsync(...)`, you must provide:
- `client_id`
- `client_secret`
- `account_uuid`
- `scope`

The `scope` value must include the permissions required by the APIs you want to call. For example, if you want to read entities and metrics, pass the corresponding OAuth scopes in the constructor, for example `scope="environment-api:entities:read environment-api:metrics:read"`.

## Simple Demo

```python
import asyncio
from datetime import datetime, timedelta

from dynatrace import DynatraceAsync
from dynatrace import TOO_MANY_REQUESTS_WAIT
from dynatrace.environment_v2.credential_vault import PublicCertificateCredentials
from dynatrace.environment_v2.settings import SettingsObjectCreate
from dynatrace.environment_v2.tokens_api import (
    SCOPE_METRICS_INGEST,
    SCOPE_METRICS_READ,
)

async def main():
    # Create a Dynatrace client
    async with DynatraceAsync(
        client_id="oauth_client_id",
        client_secret="oauth_client_secret",
        account_uuid="your-account-uuid",
        base_url="environment_url",
    ) as dt:
        # Create a client that handles too many requests (429)
        # dt = DynatraceAsync(
        #     client_id="oauth_client_id",
        #     client_secret="oauth_client_secret",
        #     account_uuid="your-account-uuid",
        #     base_url="environment_url",
        #     too_many_requests_strategy=TOO_MANY_REQUESTS_WAIT,
        # )

        # Create a client that automatically retries on errors, up to 5 times, with a 1 second delay between retries
        # dt = DynatraceAsync(
        #     client_id="oauth_client_id",
        #     client_secret="oauth_client_secret",
        #     account_uuid="your-account-uuid",
        #     base_url="environment_url",
        #     retries=5,
        #     retry_delay_ms=1000,
        # )

        # Create a client with a custom HTTP timeout of 10 seconds
        # dt = DynatraceAsync(
        #     client_id="oauth_client_id",
        #     client_secret="oauth_client_secret",
        #     account_uuid="your-account-uuid",
        #     base_url="environment_url",
        #     timeout=10,
        # )

        # Get all hosts and some properties
        async for entity in await dt.entities.list(
            'type("HOST")',
            fields="properties.memoryTotal,properties.monitoringMode",
        ):
            print(entity.entity_id, entity.display_name, entity.properties)

        # Get idle CPU for all hosts
        async for metric in await dt.metrics.query(
            "builtin:host.cpu.idle",
            resolution="Inf",
        ):
            print(metric)

        # Print dimensions, timestamp and values for the AWS Billing Metric
        async for metric in await dt.metrics.query(
            "ext:cloud.aws.billing.estimatedChargesByRegionCurrency"
        ):
            for data in metric.data:
                for timestamp, value in zip(data.timestamps, data.values):
                    print(data.dimensions, timestamp, value)

        # Get all ActiveGates
        async for ag in await dt.activegates.list():
            print(ag)

        # Get metric descriptions for all host metrics
        async for metric in await dt.metrics.list("builtin:host.*"):
            print(metric)

        # Delete endpoints that contain the word test
        async for plugin in await dt.plugins.list():
            # This could also be dt.get_endpoints(plugin.id)
            async for endpoint in plugin.endpoints:
                if "test" in endpoint.name:
                    await endpoint.delete(plugin.id)

        # Prints dashboard ID, owner and number of tiles
        async for dashboard in await dt.dashboards.list():
            full_dashboard = await dashboard.get_full_dashboard()
            print(full_dashboard.id, dashboard.owner, len(full_dashboard.tiles))

        # Delete API Tokens that haven't been used for more than 3 months
        async for token in await dt.tokens.list(fields="+lastUsedDate,+scopes"):
            if token.last_used_date and token.last_used_date < datetime.now() - timedelta(
                days=90
            ):
                print(
                    f"Deleting token! {token}, last used date: {token.last_used_date}"
                )

        # Create an API Token that can read and ingest metrics
        new_token = await dt.tokens.create(
            "metrics_token",
            scopes=[SCOPE_METRICS_READ, SCOPE_METRICS_INGEST],
        )
        print(new_token.token)

        # Upload a public PEM certificate to the Credential Vault
        with open("ca.pem", "r") as f:
            ca_cert = f.read()

        my_cred = PublicCertificateCredentials(
            name="my_cred",
            scopes=["EXTENSION"],
            description="my_cred description",
            owner_access_only=False,
            certificate=ca_cert,
            password="",
            certificate_format="PEM",
        )

        credential = await dt.credentials.post(my_cred)
        print(credential.id)

        # Create a new settings 2.0 object
        settings_value = {
            "enabled": True,
            "summary": "DT API TEST 1",
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
            schema_id="builtin:anomaly-detection.metric-events",
            value=settings_value,
            scope="environment",
        )
        await dt.settings.create_object(validate_only=False, body=settings_object)


asyncio.run(main())
```

## Implementation Progress

### Environment API V2

 API                                     |       Level        | Access                                    |
:----------------------------------------|:------------------:|:------------------------------------------|
 Access Tokens - API tokens              | :heavy_check_mark: | `dt.tokens`                               |
 Access tokens - Tenant tokens           | :heavy_check_mark: | `dt.tenant_tokens`                        |
 ActiveGates                             | :heavy_check_mark: | `dt.activegates`                          |
 ActiveGates - Auto-update configuration | :heavy_check_mark: | `dt.activegates_autoupdate_configuration` |
 ActiveGates - Auto-update jobs          | :heavy_check_mark: | `dt.activegates_autoupdate_jobs`          |
 ActiveGates - Remote configuration      | :heavy_check_mark: | `dt.activegates_remote_configuration`     |
 Audit Logs                              | :heavy_check_mark: | `dt.audit_logs`                           |
 Events                                  |     :warning:      | `dt.events_v2`                            |
 Extensions 2.0                          | :heavy_check_mark: | `dt.extensions_v2`                        |
 Logs                                    |     :warning:      | `dt.logs`                                 |
 Metrics                                 | :heavy_check_mark: | `dt.metrics`                              |
 Monitored entities                      |     :warning:      | `dt.entities`                             |
 Monitored entities - Custom tags        | :heavy_check_mark: | `dt.custom_tags`                          |
 Network zones                           |     :warning:      | `dt.network_zones`                        |
 OneAgents - Remote configuration        | :heavy_check_mark: | `dt.oneagents_remote_configuration`       |
 Problems                                | :heavy_check_mark: | `dt.problems`                             |
 Security problems                       | :heavy_check_mark: | `dt.security_problems`                    |
 Service-level objectives                | :heavy_check_mark: | `dt.slos`                                 |
 Settings                                |     :warning:      | `dt.settings`                             | 
 Credential vault                        | :heavy_check_mark: | `dt.credentials`                          |

### Environment API V1

 API                                   |       Level        | Access                          |
:--------------------------------------|:------------------:|:--------------------------------|
 Anonymization                         |        :x:         |                                 |
 Cluster time                          | :heavy_check_mark: | `dt.cluster_time`               |
 Cluster version                       |        :x:         |                                 |
 Custom devices                        | :heavy_check_mark: | `dt.custom_devices`             |
 Deployment                            | :heavy_check_mark: | `dt.deployment`                 |
 Events                                |     :warning:      | `dt.events`                     |
 JavaScript tag management             |        :x:         |                                 |
 Log monitoring - Custom devices       |        :x:         |                                 |
 Log monitoring - Hosts                |        :x:         |                                 |
 Log monitoring - Process groups       |        :x:         |                                 |
 Maintenance window                    |        :x:         |                                 |
 OneAgent on a host                    |     :warning:      | `dt.oneagents`                  |
 Problem                               |        :x:         |                                 |
 Synthetic - Locations and nodes       |        :x:         |                                 |
 Synthetic - Monitors                  |     :warning:      | `dt.synthetic_monitors`         |
 Synthetic - Third party               | :heavy_check_mark: | `dt.third_part_synthetic_tests` |
 Threshold                             |        :x:         |                                 |
 Timeseries                            |     :warning:      | `dt.timeseries`                 |
 Tokens                                |        :x:         |                                 |
 Topology & Smartscape - Application   |        :x:         |                                 |
 Topology & Smartscape - Custom device |     :warning:      | `dt.custom_devices`             |
 Topology & Smartscape - Host          |     :warning:      | `dt.smartscape_hosts`           |
 Topology & Smartscape - Process       |        :x:         |                                 |
 Topology & Smartscape - Process group |        :x:         |                                 |
 Topology & Smartscape - Service       |        :x:         |                                 |
 User sessions                         |        :x:         |                                 |

### Configuration API V1

 API                                                 |       Level        | Access                                |
:----------------------------------------------------|:------------------:|:--------------------------------------|
 Alerting Profiles                                   |     :warning:      | `dt.alerting_profiles`                |
 Anomaly detection - Applications                    |        :x:         |                                       |
 Anomaly detection - AWS                             |        :x:         |                                       |
 Anomaly detection - Database services               |        :x:         |                                       |
 Anomaly detection - Disk events                     |        :x:         |                                       |
 Anomaly detection - Hosts                           |        :x:         |                                       |
 Anomaly detection - Metric events                   |     :warning:      | `dt.anomaly_detection_metric_events`  |
 Anomaly detection - Process groups                  |     :warning:      | `dt.anomaly_detection_process_groups` |
 Anomaly detection - Services                        |        :x:         |                                       |
 Anomaly detection - VMware                          |        :x:         |                                       |
 Automatically applied tags                          |     :warning:      | `dt.auto_tags`                        |
 AWS credentials configuration                       |        :x:         |                                       |
 AWS PrivateLink                                     |        :x:         |                                       |
 Azure credentials configuration                     |        :x:         |                                       |
 Calculated metrics - Log monitoring                 |        :x:         |                                       |
 Calculated metrics - Mobile & custom applications   |        :x:         |                                       |
 Calculated metrics - Services                       |        :x:         |                                       |
 Calculated metrics - Synthetic                      |        :x:         |                                       |
 Calculated metrics - Web applications               |        :x:         |                                       |
 Cloud Foundry credentials configuration             |        :x:         |                                       |
 Conditional naming                                  |        :x:         |                                       |
 Custom tags                                         | :heavy_check_mark: | `dt.custom_tags`                      |
 Dashboards                                          |     :warning:      | `dt.dashboards`                       |
 Data privacy and security                           |        :x:         |                                       |
 Extensions                                          | :heavy_check_mark: | `dt.extensions`                       |
 Frequent issue detection                            |        :x:         |                                       |
 Kubernetes credentials configuration                |        :x:         |                                       |
 Maintenance windows                                 |     :warning:      | `dt.maintenance_windows`              |
 Management zones                                    |     :warning:      | `dt.management_zones`                 |
 Notifications                                       |     :warning:      | `dt.notifications`                    |
 OneAgent - Environment-wide configuration           | :heavy_check_mark: | `dt.oneagents_config_environment`     |
 OneAgent in a host group                            | :heavy_check_mark: | `dt.oneagents_config_hostgroup`       |
 OneAgent on a host                                  | :heavy_check_mark: | `dt.oneagents_config_host`            |
 Plugins                                             |     :warning:      | `dt.plugins`                          |
 Remote environments                                 |        :x:         |                                       |
 Reports                                             |        :x:         |                                       |
 RUM - Allowed beacon origins for CORS               |        :x:         |                                       |
 RUM - Application detection rules                   |        :x:         |                                       |
 RUM - Application detection rules - Host detection  |        :x:         |                                       |
 RUM - Content resources                             |        :x:         |                                       |
 RUM - Geographic regions - custom client IP headers |        :x:         |                                       |
 RUM - Geographic regions - IP address mapping       |        :x:         |                                       |
 RUM - Mobile and custom application configuration   |        :x:         |                                       |
 RUM - Web application configuration                 |        :x:         |                                       |
 Service - Custom services                           |        :x:         |                                       |
 Service - Detection full web request                |        :x:         |                                       |
 Service - Detection full web service                |        :x:         |                                       |
 Service - Detection opaque and external web request |        :x:         |                                       |
 Service - Detection opaque and external web service |        :x:         |                                       |
 Service - Failure detection parameter sets          |        :x:         |                                       |
 Service - Failure detection rules                   |        :x:         |                                       |
 Service - IBM MQ tracing                            |        :x:         |                                       |
 Service - Request attributes                        |        :x:         |                                       |
 Service - Request naming                            |        :x:         |                                       |

### Platform API

 API                                  |       Level        | Access                                                                    |
:-------------------------------------|:------------------:|:--------------------------------------------------------------------------|
 AppEngine - Registry - Apps          | :heavy_check_mark: | `dt.platform.appengine_registry`                                          |
 AppEngine - Registry - Schema Manifest | :heavy_check_mark: | `dt.platform.appengine_registry`                                        |
 Davis CoPilot API                    | :heavy_check_mark: | `dt.platform.davis_copilot`                                               |
 Davis AI - Predictive and Causal     |     :warning:      | `dt.platform.davis_analyzers`                                             |
 DQL Query                            | :heavy_check_mark: | `dt.platform.grail_query_execution`, `dt.platform.grail_query_assistance` |

### Account API

 API                                                        |       Level        | Access                               |
:-----------------------------------------------------------|:------------------:|:-------------------------------------|
 Account Management - Account limits                        |        :x:         |                                      |
 Account Management - User management                       |        :x:         |                                      |
 Account Management - Group management                      |        :x:         |                                      |
 Account Management - Permission management                 |        :x:         |                                      |
 Account Management - Policy management                     |        :x:         |                                      |
 Account Management - Service user management               |        :x:         |                                      |
 Account Management - Platform tokens                       |        :x:         |                                      |
 Environment management API v1                              | :heavy_check_mark: | `dt.account.env_v1`                  |
 Environment management API v2                              | :heavy_check_mark: | `dt.account.env_v2`                  |
 Dynatrace Platform Subscription - Subscription management  | :heavy_check_mark: | `dt.account.sub_v2`                  |
 Dynatrace Platform Subscription - Subscription environments v2 |        :x:         |                                      |
 Dynatrace Platform Subscription - Subscription environments v3 | :heavy_check_mark: | `dt.account.sub_v3`                  |
 Dynatrace Platform Subscription - Rate cards               | :heavy_check_mark: | `dt.account.sub_v1_rate_cards`       |
 Dynatrace Platform Subscription - Cost allocation          | :heavy_check_mark: | `dt.account.sub_v1_cost_allocation`  |
 Account Settings                                           |        :x:         |                                      |
 Account Audits                                             |        :x:         |                                      |
 Reference data                                             |        :x:         |                                      |
 Notifications                                              |        :x:         |                                      |
