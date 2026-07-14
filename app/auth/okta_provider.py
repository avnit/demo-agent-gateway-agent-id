"""Okta OIDC front-door for the Agent Gateway.

In a real deployment the human completes the Okta OIDC authorization-code flow in a
browser and the gateway receives an ID token. For a self-contained demo we model that
step behind ``get_subject_token`` so the federation path can be exercised without a
live browser session. Swap ``_demo_id_token`` for your real Okta token acquisition.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class OktaIdentity:
    subject: str
    email: str
    groups: list[str]
    id_token: str


class OktaProvider:
    idp_name = "okta"
    provider_id = "okta-oidc"

    def __init__(self) -> None:
        self.issuer = os.environ.get("OKTA_ISSUER", "https://your-org.okta.com/oauth2/default")
        self.client_id = os.environ.get("OKTA_CLIENT_ID", "0oaEXAMPLEokta1234")

    def get_subject_token(self) -> OktaIdentity:
        """Return the OIDC ID token to be exchanged at Google STS.

        Replace the demo token with a real Okta authorization-code flow result.
        The returned token's ``aud`` must equal ``self.client_id`` and its ``iss``
        must equal the issuer configured on the GCP workforce provider.
        """
        token = os.environ.get("OKTA_ID_TOKEN") or self._demo_id_token()
        return OktaIdentity(
            subject=os.environ.get("OKTA_SUBJECT", "avnit@asbsolutions.example"),
            email=os.environ.get("OKTA_EMAIL", "avnit@asbsolutions.example"),
            groups=["gemini-agent-users"],
            id_token=token,
        )

    def _demo_id_token(self) -> str:
        # Placeholder. A real value is a signed JWT from Okta.
        return "DEMO.okta.oidc.id_token"
