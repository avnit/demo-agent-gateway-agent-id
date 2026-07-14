#!/usr/bin/env python3
"""Agent Gateway — the auth broker that sits between a federated human and Gemini Enterprise.

Responsibilities, in order:
  1. Accept an authenticated human from Okta or Entra ID (Workforce Identity Federation).
  2. Enforce authorization policy (which agent, which IdP groups are allowed).
  3. Exchange the human's IdP token for a short-lived AGENT identity (per-agent SA).
  4. Call Gemini Enterprise as the agent, on-behalf-of the human.
  5. Emit an audit line binding agent SA + human subject to the model call.

Run:
    python agent_gateway.py --idp okta --prompt "Summarize our Q3 security posture"
    python agent_gateway.py --idp azuread --prompt "Draft an incident timeline"

Set DEMO_MODE=0 (and provide real tokens / ADC) to make live API calls.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from config import SETTINGS
from auth import OktaProvider, AzureADProvider, mint_agent_credential
from gemini import GeminiEnterpriseClient

# Simple per-agent policy: which IdP group is allowed to drive which agent.
ALLOWED_GROUPS = {"gemini-agent-users"}


def _select_provider(idp: str):
    if idp == "okta":
        return OktaProvider()
    if idp == "azuread":
        return AzureADProvider()
    raise SystemExit(f"unknown idp: {idp!r} (expected 'okta' or 'azuread')")


def _authorize(identity, provider) -> None:
    """Policy gate. Entra emits group object IDs, so we allow either the named
    Okta group or any configured Entra group OID to pass."""
    groups = set(identity.groups)
    if provider.idp_name == "okta" and not (groups & ALLOWED_GROUPS):
        raise SystemExit(f"DENIED: {identity.email} not in an authorized group {ALLOWED_GROUPS}")
    # For Entra, membership is validated by the provider's attribute_condition in GCP;
    # here we just confirm a group claim is present.
    if provider.idp_name == "azuread" and not groups:
        raise SystemExit(f"DENIED: {identity.email} has no group claim")


def _audit(line: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[AUDIT {ts}] {line}", file=sys.stderr)


def run(idp: str, prompt: str) -> str:
    provider = _select_provider(idp)

    # 1. Authenticated human arrives from the IdP.
    identity = provider.get_subject_token()
    _audit(f"idp={provider.idp_name} human={identity.email} subject={identity.subject}")

    # 2. Authorization policy.
    _authorize(identity, provider)
    _audit(f"authorized human={identity.email} for agent={SETTINGS.agent_sa_email}")

    # 3. Federate the human token into a short-lived AGENT identity.
    cred = mint_agent_credential(
        subject_token=identity.id_token,
        subject=identity.subject,
        audience=SETTINGS.sts_audience,
        idp=provider.idp_name,
        agent_sa_email=SETTINGS.agent_sa_email,
        lifetime_seconds=SETTINGS.agent_token_lifetime_seconds,
    )
    _audit(
        f"minted agent credential sa={cred.agent_sa_email} "
        f"obo={cred.on_behalf_of_subject} ttl={cred.expires_in}s"
    )

    # 4. Call Gemini Enterprise as the agent, on-behalf-of the human.
    gemini = GeminiEnterpriseClient(SETTINGS.project_id, SETTINGS.region, SETTINGS.gemini_model)
    answer = gemini.generate(
        agent_access_token=cred.access_token,
        on_behalf_of=cred.on_behalf_of_subject,
        prompt=prompt,
    )
    _audit(
        f"gemini call complete model={SETTINGS.gemini_model} "
        f"agent={cred.agent_sa_email} obo={cred.on_behalf_of_subject}"
    )
    return answer


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent Gateway demo")
    parser.add_argument("--idp", choices=["okta", "azuread"], default="okta")
    parser.add_argument("--prompt", default="Summarize our Q3 security posture in three bullets.")
    args = parser.parse_args()

    answer = run(args.idp, args.prompt)
    print("\n=== Gemini Enterprise (via Agent Gateway) ===")
    print(answer)


if __name__ == "__main__":
    main()
