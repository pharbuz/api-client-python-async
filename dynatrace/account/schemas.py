"""High-level account API aggregators."""

from dynatrace.account.env_v1.environments import AccountEnvironmentsV1Service
from dynatrace.account.env_v2.environments import AccountEnvironmentsV2Service
from dynatrace.account.env_v2.settings import SettingService as AccountSettingService
from dynatrace.account.sub_v1.cost_allocation import CostAllocationService
from dynatrace.account.sub_v1.rate_cards import RateCardService
from dynatrace.account.sub_v2.subscriptions import SubscriptionService
from dynatrace.account.sub_v3.environments import SubscriptionEnvironmentService
from dynatrace.http_client import HttpClient


class AccountAPI:
    def __init__(self, http_client: HttpClient) -> None:
        # Account environment management APIs.
        self.env_v1: AccountEnvironmentsV1Service = AccountEnvironmentsV1Service(
            http_client
        )
        self.env_v2: AccountEnvironmentsV2Service = AccountEnvironmentsV2Service(
            http_client
        )
        self.settings: AccountSettingService = AccountSettingService(http_client)

        # Account subscription APIs.
        self.sub_v1_cost_allocation: CostAllocationService = CostAllocationService(
            http_client
        )
        self.sub_v1_rate_cards: RateCardService = RateCardService(http_client)
        self.sub_v2: SubscriptionService = SubscriptionService(http_client)
        self.sub_v3: SubscriptionEnvironmentService = SubscriptionEnvironmentService(
            http_client
        )
