"""The core federation logic: STS token exchange + agent service-account impersonation.

This is where the human's IdP token becomes a short-lived agent credential.

Two hops:
  1. Google STS ``token()`` exchange  — IdP OIDC token  -> federated access token
  2. IAM Credentials ``generateAccessToken`` — federated token -> agent SA token

The real HTTP calls are shown so the trust chain is auditable. Set ``DEMO_MODE=0`` and
provide real tokens/ADC to exercise them against Google APIs.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import requests  # type: ignore

STS_ENDPOINT = "https://sts.googleapis.com/v1/token"
IAM_CREDENTIALS_ENDPOINT = (
    "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{sa}:generateAccessToken"
)

TOKEN_EXCHANGE_GRANT = "urn:ietf:params:oauth:grant-type:token-exchange"
ACCESS_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:access_token"
JWT_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:jwt"


def _demo_mode() -> bool:
    return os.environ.get("DEMO_MODE", "1") != "0"


@dataclass
class AgentCredential:
    """A short-lived credential minted for the agent, plus the human it acts for."""

    access_token: str
    agent_sa_email: str
    on_behalf_of_subject: str
    idp: str
    expires_in: int


def exchange_idp_token_for_federated_token(
    subject_token: str, audience: str, idp: str, user_project: str | None = None
) -> str:
    """Hop 1 — exchange the IdP OIDC token for a Google federated access token (STS).

    ``user_project`` is required for workforce federation: the resulting token is
    billed/quota'd against that project when it calls Google APIs.
    """
    if _demo_mode():
        return f"DEMO.federated.access_token.for.{idp}"

    payload = {
        "grant_type": TOKEN_EXCHANGE_GRANT,
        "audience": audience,
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "requested_token_type": ACCESS_TOKEN_TYPE,
        "subject_token": subject_token,
        "subject_token_type": JWT_TOKEN_TYPE,
    }
    if user_project:
        payload["options"] = json.dumps({"userProject": user_project})
    resp = requests.post(STS_ENDPOINT, data=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


def impersonate_agent_sa(
    federated_token: str, agent_sa_email: str, lifetime_seconds: int
) -> tuple[str, int]:
    """Hop 2 — use the federated token to mint a short-lived token for the agent SA.

    Requires the federated principal to hold ``roles/iam.serviceAccountTokenCreator``
    on ``agent_sa_email`` (granted in ``terraform/agent_identity.tf``).
    """
    if _demo_mode():
        return (f"DEMO.agent_sa.access_token.{agent_sa_email}", lifetime_seconds)

    url = IAM_CREDENTIALS_ENDPOINT.format(sa=agent_sa_email)
    body = {
        "scope": ["https://www.googleapis.com/auth/cloud-platform"],
        "lifetime": f"{lifetime_seconds}s",
    }
    headers = {
        "Authorization": f"Bearer {federated_token}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
    resp.raise_for_status()
    return resp.json()["accessToken"], lifetime_seconds


def mint_agent_credential(
    *,
    subject_token: str,
    subject: str,
    audience: str,
    idp: str,
    agent_sa_email: str,
    lifetime_seconds: int,
    user_project: str | None = None,
) -> AgentCredential:
    """Run both federation hops and return the agent credential + OBO subject."""
    federated = exchange_idp_token_for_federated_token(subject_token, audience, idp, user_project)
    agent_token, expires_in = impersonate_agent_sa(federated, agent_sa_email, lifetime_seconds)
    return AgentCredential(
        access_token=agent_token,
        agent_sa_email=agent_sa_email,
        on_behalf_of_subject=subject,
        idp=idp,
        expires_in=expires_in,
    )
