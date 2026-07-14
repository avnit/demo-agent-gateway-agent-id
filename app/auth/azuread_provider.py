"""Microsoft Entra ID (Azure AD) OIDC front-door for the Agent Gateway.

Mirrors ``okta_provider`` — the same gateway logic works against either IdP. The only
difference is the issuer (tenant-scoped) and the audience (Entra app client ID).
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AzureADIdentity:
    subject: str
    email: str
    groups: list[str]
    id_token: str


class AzureADProvider:
    idp_name = "azuread"
    provider_id = "azuread-oidc"

    def __init__(self) -> None:
        self.tenant_id = os.environ.get("AZUREAD_TENANT_ID", "00000000-0000-0000-0000-000000000000")
        self.client_id = os.environ.get("AZUREAD_CLIENT_ID", "11111111-1111-1111-1111-111111111111")
        self.issuer = f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"

    def get_subject_token(self) -> AzureADIdentity:
        """Return the Entra ID OIDC token to be exchanged at Google STS.

        Replace the demo token with a real Entra authorization-code (or
        client-credentials, for daemon agents) flow result.
        """
        token = os.environ.get("AZUREAD_ID_TOKEN") or self._demo_id_token()
        return AzureADIdentity(
            subject=os.environ.get("AZUREAD_SUBJECT", "avnit@asbsolutions.onmicrosoft.com"),
            email=os.environ.get("AZUREAD_EMAIL", "avnit@asbsolutions.onmicrosoft.com"),
            groups=[os.environ.get("AZUREAD_GROUP_OID", "REPLACE_WITH_ENTRA_GROUP_OBJECT_ID")],
            id_token=token,
        )

    def _demo_id_token(self) -> str:
        return "DEMO.entra.oidc.id_token"
