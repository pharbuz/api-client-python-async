from __future__ import annotations

from abc import ABC, abstractmethod
from base64 import b64encode
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList


class CredentialVaultService:
    _ENDPOINT = "/api/v2/credentials"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self,
        credential_type: str | None = None,
        name: str | None = None,
        user: str | None = None,
        scope: str | None = None,
        page_size: int | None = None,
    ) -> PaginatedList[CredentialsResponseElement]:
        """Lists all sets of credentials in your environment."""

        params = {
            "type": credential_type,
            "name": name,
            "user": user,
            "scope": scope,
            "pageSize": page_size,
        }

        return await PaginatedList(
            CredentialsResponseElement,
            self.__http_client,
            self._ENDPOINT,
            target_params=params,
            list_item="credentials",
        ).initialize()

    async def get(self, credential_id: str) -> CredentialsResponseElement:
        response = await self.__http_client.make_request(
            f"{self._ENDPOINT}/{credential_id}", method="GET"
        )
        return CredentialsResponseElement(raw_element=response.json())

    async def create(self, credential: Credentials) -> CredentialsId:
        response = await self.__http_client.make_request(
            path=self._ENDPOINT, params=credential.to_json(), method="POST"
        )
        return CredentialsId(raw_element=response.json())

    async def post(self, credential: Credentials) -> CredentialsId:
        """Backward-compatible alias for create()."""
        return await self.create(credential)

    async def update(
        self, credential_id: str, credential: Credentials
    ) -> CredentialsId | Response:
        response = await self.__http_client.make_request(
            path=f"{self._ENDPOINT}/{credential_id}",
            params=credential.to_json(),
            method="PUT",
        )

        if response.content:
            return CredentialsId(raw_element=response.json())
        return response

    async def put(
        self, credential_id: str, credential: Credentials
    ) -> CredentialsId | Response:
        """Backward-compatible alias for update()."""
        return await self.update(credential_id, credential)

    async def delete(self, credential_id: str) -> Response:
        return await self.__http_client.make_request(
            f"{self._ENDPOINT}/{credential_id}", method="DELETE"
        )


class CredentialAccessData(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.id: str = raw_element.get("id", "")
        self.type: str = raw_element.get("type", "")

    def to_json(self) -> dict[str, str]:
        return {"id": self.id, "type": self.type}


class CredentialUsageHandler(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.type: str = raw_element.get("type", "")
        self.count: int = raw_element.get("count", 0)


class CredentialsId(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.id: str = raw_element.get("id", "")


class CredentialsResponseElement(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.name: str = raw_element.get("name", "")
        self.id: str = raw_element.get("id", "")
        self.type: str = raw_element.get("type", "")
        self.description: str = raw_element.get("description", "")
        self.owner: str = raw_element.get("owner", "")
        self.owner_access_only: bool = raw_element.get("ownerAccessOnly", False)
        self.allow_contextless_requests: bool = raw_element.get(
            "allowContextlessRequests", False
        )
        self.scope: str = raw_element.get("scope", "")
        self.scopes: list[str] = raw_element.get("scopes", [])
        self.external_vault: dict[str, Any] | None = raw_element.get("externalVault")
        self.allowed_entities: list[CredentialAccessData] = [
            CredentialAccessData(raw_element=entry)
            for entry in raw_element.get("allowedEntities", [])
        ]
        self.credential_usage_summary: list[CredentialUsageHandler] = [
            CredentialUsageHandler(raw_element=summary)
            for summary in raw_element.get("credentialUsageSummary", [])
        ]


class Credentials(ABC):
    def __init__(
        self,
        name: str,
        scopes: list[str] | None = None,
        description: str | None = None,
        owner_access_only: bool | None = False,
        allow_contextless_requests: bool | None = None,
        allowed_entities: list[CredentialAccessData | dict[str, str]] | None = None,
        external_vault: dict[str, Any] | None = None,
        scope: str | None = None,
        credential_type: str | None = None,
    ):
        self.name = name
        self.scopes = scopes or ([scope] if scope else [])
        self.scope = scope
        self.description = description
        self.owner_access_only = owner_access_only
        self.allow_contextless_requests = allow_contextless_requests
        self.allowed_entities = allowed_entities or []
        self.external_vault = external_vault
        self.type = credential_type

    def _base_json(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "name": self.name,
            "scopes": self.scopes,
            "type": self.type,
        }

        if self.scope is not None:
            body["scope"] = self.scope
        if self.description is not None:
            body["description"] = self.description
        if self.owner_access_only is not None:
            body["ownerAccessOnly"] = self.owner_access_only
        if self.allow_contextless_requests is not None:
            body["allowContextlessRequests"] = self.allow_contextless_requests
        if self.external_vault is not None:
            body["externalVault"] = self.external_vault
        if self.allowed_entities:
            body["allowedEntities"] = [
                entity.to_json() if isinstance(entity, CredentialAccessData) else entity
                for entity in self.allowed_entities
            ]

        return body

    @abstractmethod
    def to_json(self) -> dict[str, Any]:
        pass


class CertificateCredentials(Credentials):
    def __init__(
        self,
        name: str,
        scopes: list[str] | None,
        certificate: str,
        password: str,
        certificate_format: str,
        description: str | None = None,
        owner_access_only: bool | None = False,
        allow_contextless_requests: bool | None = None,
        allowed_entities: list[CredentialAccessData | dict[str, str]] | None = None,
        scope: str | None = None,
        encode_values: bool = True,
    ):
        super().__init__(
            name=name,
            scopes=scopes,
            description=description,
            owner_access_only=owner_access_only,
            allow_contextless_requests=allow_contextless_requests,
            allowed_entities=allowed_entities,
            scope=scope,
            credential_type="CERTIFICATE",
        )
        if encode_values:
            self.certificate = b64encode(certificate.encode()).decode()
            self.password = b64encode(password.encode()).decode()
        else:
            self.certificate = certificate
            self.password = password
        self.certificate_format = certificate_format

    def to_json(self) -> dict[str, Any]:
        body = self._base_json()
        body["certificate"] = self.certificate
        body["password"] = self.password
        body["certificateFormat"] = self.certificate_format
        return body


class PublicCertificateCredentials(Credentials):
    def __init__(
        self,
        name: str,
        scopes: list[str] | None,
        certificate: str,
        password: str,
        certificate_format: str,
        description: str | None = None,
        owner_access_only: bool | None = False,
        allow_contextless_requests: bool | None = None,
        allowed_entities: list[CredentialAccessData | dict[str, str]] | None = None,
        scope: str | None = None,
        encode_certificate: bool = True,
    ):
        super().__init__(
            name=name,
            scopes=scopes,
            description=description,
            owner_access_only=owner_access_only,
            allow_contextless_requests=allow_contextless_requests,
            allowed_entities=allowed_entities,
            scope=scope,
            credential_type="PUBLIC_CERTIFICATE",
        )
        self.certificate = (
            b64encode(certificate.encode()).decode()
            if encode_certificate
            else certificate
        )
        self.password = password
        self.certificate_format = certificate_format

    def to_json(self) -> dict[str, Any]:
        body = self._base_json()
        body["certificate"] = self.certificate
        body["password"] = self.password
        body["certificateFormat"] = self.certificate_format
        return body


class UserPasswordCredentials(Credentials):
    def __init__(
        self,
        name: str,
        scopes: list[str] | None,
        user: str,
        password: str,
        description: str | None = None,
        owner_access_only: bool | None = False,
        allow_contextless_requests: bool | None = None,
        allowed_entities: list[CredentialAccessData | dict[str, str]] | None = None,
        external_vault: dict[str, Any] | None = None,
        scope: str | None = None,
    ):
        super().__init__(
            name=name,
            scopes=scopes,
            description=description,
            owner_access_only=owner_access_only,
            allow_contextless_requests=allow_contextless_requests,
            allowed_entities=allowed_entities,
            external_vault=external_vault,
            scope=scope,
            credential_type="USERNAME_PASSWORD",
        )
        self.user = user
        self.password = password

    def to_json(self) -> dict[str, Any]:
        body = self._base_json()
        body["user"] = self.user
        body["password"] = self.password
        return body


class TokenCredentials(Credentials):
    def __init__(
        self,
        name: str,
        scopes: list[str] | None,
        token: str,
        description: str | None = None,
        owner_access_only: bool | None = False,
        allow_contextless_requests: bool | None = None,
        allowed_entities: list[CredentialAccessData | dict[str, str]] | None = None,
        external_vault: dict[str, Any] | None = None,
        scope: str | None = None,
    ):
        super().__init__(
            name=name,
            scopes=scopes,
            description=description,
            owner_access_only=owner_access_only,
            allow_contextless_requests=allow_contextless_requests,
            allowed_entities=allowed_entities,
            external_vault=external_vault,
            scope=scope,
            credential_type="TOKEN",
        )
        self.token = token

    def to_json(self) -> dict[str, Any]:
        body = self._base_json()
        body["token"] = self.token
        return body


class SNMPV3Credentials(Credentials):
    def __init__(
        self,
        name: str,
        scopes: list[str] | None,
        username: str,
        security_level: str,
        authentication_protocol: str | None = None,
        authentication_password: str | None = None,
        privacy_protocol: str | None = None,
        privacy_password: str | None = None,
        description: str | None = None,
        owner_access_only: bool | None = False,
        allow_contextless_requests: bool | None = None,
        allowed_entities: list[CredentialAccessData | dict[str, str]] | None = None,
        scope: str | None = None,
    ):
        super().__init__(
            name=name,
            scopes=scopes,
            description=description,
            owner_access_only=owner_access_only,
            allow_contextless_requests=allow_contextless_requests,
            allowed_entities=allowed_entities,
            scope=scope,
            credential_type="SNMPV3",
        )
        self.username = username
        self.security_level = security_level
        self.authentication_protocol = authentication_protocol
        self.authentication_password = authentication_password
        self.privacy_protocol = privacy_protocol
        self.privacy_password = privacy_password

    def to_json(self) -> dict[str, Any]:
        body = self._base_json()
        body["username"] = self.username
        body["securityLevel"] = self.security_level
        if self.authentication_protocol is not None:
            body["authenticationProtocol"] = self.authentication_protocol
        if self.authentication_password is not None:
            body["authenticationPassword"] = self.authentication_password
        if self.privacy_protocol is not None:
            body["privacyProtocol"] = self.privacy_protocol
        if self.privacy_password is not None:
            body["privacyPassword"] = self.privacy_password
        return body


class AWSKeyBasedCredentials(Credentials):
    def __init__(
        self,
        name: str,
        scopes: list[str] | None,
        access_key_id: str,
        secret_key: str,
        aws_partition: str,
        description: str | None = None,
        owner_access_only: bool | None = False,
        allow_contextless_requests: bool | None = None,
        allowed_entities: list[CredentialAccessData | dict[str, str]] | None = None,
    ):
        super().__init__(
            name=name,
            scopes=scopes,
            description=description,
            owner_access_only=owner_access_only,
            allow_contextless_requests=allow_contextless_requests,
            allowed_entities=allowed_entities,
            credential_type="AWS_MONITORING_KEY_BASED",
        )
        self.access_key_id = access_key_id
        self.secret_key = secret_key
        self.aws_partition = aws_partition

    def to_json(self) -> dict[str, Any]:
        body = self._base_json()
        body["accessKeyID"] = self.access_key_id
        body["secretKey"] = self.secret_key
        body["awsPartition"] = self.aws_partition
        return body


class AWSRoleBasedCredentials(Credentials):
    def __init__(
        self,
        name: str,
        scopes: list[str] | None,
        account_id: str,
        iam_role: str,
        description: str | None = None,
        owner_access_only: bool | None = False,
        allow_contextless_requests: bool | None = None,
        allowed_entities: list[CredentialAccessData | dict[str, str]] | None = None,
    ):
        super().__init__(
            name=name,
            scopes=scopes,
            description=description,
            owner_access_only=owner_access_only,
            allow_contextless_requests=allow_contextless_requests,
            allowed_entities=allowed_entities,
            credential_type="AWS_MONITORING_ROLE_BASED",
        )
        self.account_id = account_id
        self.iam_role = iam_role

    def to_json(self) -> dict[str, Any]:
        body = self._base_json()
        body["accountID"] = self.account_id
        body["iamRole"] = self.iam_role
        return body
