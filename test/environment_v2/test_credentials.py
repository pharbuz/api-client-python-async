from dynatrace import DynatraceAsync
from dynatrace.environment_v2.credential_vault import (
    CredentialsId,
    CredentialsResponseElement,
    UserPasswordCredentials,
)
from dynatrace.pagination import PaginatedList


async def test_list_credentials(dt: DynatraceAsync):
    credentials = await dt.credentials.list()
    assert isinstance(credentials, PaginatedList)
    assert len(credentials) == 2


async def test_get_credential(dt: DynatraceAsync):
    credential = await dt.credentials.get("CREDENTIALS_VAULT-123")
    assert isinstance(credential, CredentialsResponseElement)
    assert credential.id == "CREDENTIALS_VAULT-123"


async def test_create_credential(dt: DynatraceAsync):
    response = await dt.credentials.create(
        UserPasswordCredentials(
            name="New user-pass credentials",
            scopes=["SYNTHETIC"],
            user="john.doe@example.com",
            password="test-pass",
        )
    )
    assert isinstance(response, CredentialsId)
    assert response.id == "CREDENTIALS_VAULT-CREATED"


async def test_update_credential(dt: DynatraceAsync):
    response = await dt.credentials.update(
        "CREDENTIALS_VAULT-123",
        UserPasswordCredentials(
            name="Updated user-pass credentials",
            scopes=["SYNTHETIC"],
            user="john.doe@example.com",
            password="changed-pass",
        ),
    )
    assert isinstance(response, CredentialsId)
    assert response.id == "CREDENTIALS_VAULT-UPDATED"


async def test_delete_credential(dt: DynatraceAsync):
    response = await dt.credentials.delete("CREDENTIALS_VAULT-123")
    assert response.json() is None
