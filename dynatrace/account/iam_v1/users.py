"""Account user management API wrappers."""

import builtins
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class AccountUsersService:
    """
    /iam/v1 User management API

    - GET /iam/v1/accounts/{accountUuid}/users
    - POST /iam/v1/accounts/{accountUuid}/users
    - GET /iam/v1/accounts/{accountUuid}/users/{email}
    - POST /iam/v1/accounts/{accountUuid}/users/{email}
    - PUT /iam/v1/accounts/{accountUuid}/users/{email}/groups
    - DELETE /iam/v1/accounts/{accountUuid}/users/{email}/groups
    - DELETE /iam/v1/accounts/{accountUuid}/users/{email}
    """

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def list(self, account_uuid: str, service_users: bool = False) -> "UserList":
        """List all users of an account."""
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/accounts/{account_uuid}/users",
                params={"service-users": service_users},
            )
        ).json()
        return UserList(raw_element=resp)

    async def create(self, account_uuid: str, email: str) -> "UserCreationResponse":
        """Create a new user in an account."""
        body = {"email": email}
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/accounts/{account_uuid}/users",
                method="POST",
                json=body,
            )
        ).json()
        return UserCreationResponse(raw_element=resp)

    async def get_groups(self, account_uuid: str, email: str) -> "UserGroups":
        """List all groups of a user."""
        resp = (
            await self.__http_client.make_request(f"/iam/v1/accounts/{account_uuid}/users/{email}")
        ).json()
        return UserGroups(raw_element=resp)

    async def add_to_groups(
        self, account_uuid: str, email: str, group_uuids: builtins.list[str]
    ) -> Response:
        """Add a user to groups."""
        return await self.__http_client.make_request(
            f"/iam/v1/accounts/{account_uuid}/users/{email}",
            method="POST",
            json=group_uuids,
        )

    async def set_groups(
        self, account_uuid: str, email: str, group_uuids: builtins.list[str]
    ) -> Response:
        """Set group membership of a user (overwrites existing)."""
        return await self.__http_client.make_request(
            f"/iam/v1/accounts/{account_uuid}/users/{email}/groups",
            method="PUT",
            json=group_uuids,
        )

    async def remove_from_groups(
        self,
        account_uuid: str,
        email: str,
        group_uuids: builtins.list[str],
    ) -> Response:
        """Remove a user from groups."""
        return await self.__http_client.make_request(
            f"/iam/v1/accounts/{account_uuid}/users/{email}/groups",
            method="DELETE",
            params={"group-uuid": group_uuids},
        )

    async def delete(self, account_uuid: str, email: str) -> Response:
        """Remove a user from an account."""
        return await self.__http_client.make_request(
            f"/iam/v1/accounts/{account_uuid}/users/{email}",
            method="DELETE",
        )


# Response models
class UserLoginMetadata(DynatraceObject):
    """User login metadata."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.successful_login_counter: int | None = raw_element.get("successfulLoginCounter")
        self.failed_login_counter: int | None = raw_element.get("failedLoginCounter")
        self.last_successful_login: str | None = raw_element.get("lastSuccessfulLogin")
        self.last_failed_login: str | None = raw_element.get("lastFailedLogin")
        self.created_at: str | None = raw_element.get("createdAt")
        self.updated_at: str | None = raw_element.get("updatedAt")


class User(DynatraceObject):
    """User object."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.uid: str | None = raw_element.get("uid")
        self.email: str | None = raw_element.get("email")
        self.name: str | None = raw_element.get("name")
        self.surname: str | None = raw_element.get("surname")
        self.user_status: str | None = raw_element.get("userStatus")
        self.emergency_contact: bool | None = raw_element.get("emergencyContact")
        user_login_metadata = raw_element.get("userLoginMetadata")
        self.user_login_metadata: UserLoginMetadata | None = (
            UserLoginMetadata(raw_element=user_login_metadata) if user_login_metadata else None
        )


class UserList(DynatraceObject):
    """List of users."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.count: int | None = raw_element.get("count")
        self.items: list[User] = [User(raw_element=e) for e in raw_element.get("items", [])]


class UserCreationResponse(DynatraceObject):
    """Response from user creation."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.user_uuid: str | None = raw_element.get("userUuid")


class Group(DynatraceObject):
    """Group object."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.group_name: str | None = raw_element.get("groupName")
        self.uuid: str | None = raw_element.get("uuid")
        self.owner: str | None = raw_element.get("owner")
        self.account_uuid: str | None = raw_element.get("accountUUID")
        self.account_name: str | None = raw_element.get("accountName")
        self.description: str | None = raw_element.get("description")
        self.created_at: str | None = raw_element.get("createdAt")
        self.updated_at: str | None = raw_element.get("updatedAt")


class UserGroups(DynatraceObject):
    """User with their groups."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.uid: str | None = raw_element.get("uid")
        self.email: str | None = raw_element.get("email")
        self.name: str | None = raw_element.get("name")
        self.surname: str | None = raw_element.get("surname")
        self.user_status: str | None = raw_element.get("userStatus")
        self.emergency_contact: bool | None = raw_element.get("emergencyContact")
        self.groups: list[Group] = [Group(raw_element=e) for e in raw_element.get("groups", [])]
