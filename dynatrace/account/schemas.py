"""High-level account API aggregators."""

from dynatrace.account.env_v1.environments import AccountEnvironmentsV1Service
from dynatrace.account.env_v2.environments import AccountEnvironmentsV2Service
from dynatrace.account.env_v2.settings import SettingService as AccountSettingService
from dynatrace.account.iam_v1.groups import AccountGroupsService
from dynatrace.account.iam_v1.platform_tokens import AccountPlatformTokensService
from dynatrace.account.iam_v1.policies import AccountPoliciesService
from dynatrace.account.iam_v1.service_users import AccountServiceUsersService
from dynatrace.account.iam_v1.users import AccountUsersService
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

        # Account IAM APIs.
        self.iam_users: AccountUsersService = AccountUsersService(http_client)
        self.iam_groups: AccountGroupsService = AccountGroupsService(http_client)
        self.iam_policies: AccountPoliciesService = AccountPoliciesService(http_client)
        self.iam_service_users: AccountServiceUsersService = AccountServiceUsersService(
            http_client
        )
        self.iam_platform_tokens: AccountPlatformTokensService = (
            AccountPlatformTokensService(http_client)
        )

        # Account subscription APIs.
        self.sub_v1_cost_allocation: CostAllocationService = CostAllocationService(
            http_client
        )
        self.sub_v1_rate_cards: RateCardService = RateCardService(http_client)
        self.sub_v2: SubscriptionService = SubscriptionService(http_client)
        self.sub_v3: SubscriptionEnvironmentService = SubscriptionEnvironmentService(
            http_client
        )
