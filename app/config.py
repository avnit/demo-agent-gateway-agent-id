"""Central configuration for the Agent Gateway demo.

All values are read from environment variables so nothing sensitive is committed.
See ``terraform/outputs.tf`` for where these values come from after ``terraform apply``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    project_id: str = os.environ.get("GCP_PROJECT_ID", "my-gemini-agent-project")
    region: str = os.environ.get("GCP_REGION", "us-central1")

    # Workforce Identity Federation (humans)
    workforce_pool: str = os.environ.get("WORKFORCE_POOL", "agent-gateway-workforce")
    okta_provider: str = os.environ.get("OKTA_PROVIDER", "okta-oidc")
    azuread_provider: str = os.environ.get("AZUREAD_PROVIDER", "azuread-oidc")

    # Agent identity (the service account each agent runs as)
    agent_sa_email: str = os.environ.get(
        "AGENT_SA_EMAIL", "gemini-support-agent@my-gemini-agent-project.iam.gserviceaccount.com"
    )

    # Gemini Enterprise
    gemini_model: str = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")

    # Short-lived agent token lifetime (seconds). Keep this small.
    agent_token_lifetime_seconds: int = int(os.environ.get("AGENT_TOKEN_LIFETIME", "900"))

    @property
    def sts_audience(self) -> str:
        return (
            "//iam.googleapis.com/locations/global/workforcePools/"
            f"{self.workforce_pool}"
        )


SETTINGS = Settings()
