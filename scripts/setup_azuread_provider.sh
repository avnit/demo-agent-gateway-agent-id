#!/usr/bin/env bash
# Idempotent gcloud setup for the Microsoft Entra ID (Azure AD) workforce provider.
set -euo pipefail

: "${ORG_ID:?set ORG_ID}"
: "${AZUREAD_TENANT_ID:?set AZUREAD_TENANT_ID}"
: "${AZUREAD_CLIENT_ID:?set AZUREAD_CLIENT_ID}"
: "${AZUREAD_GROUP_OID:?set AZUREAD_GROUP_OID (Entra group object ID allowed to use the agent)}"
POOL_ID="${POOL_ID:-agent-gateway-workforce}"
PROVIDER_ID="${PROVIDER_ID:-azuread-oidc}"
ISSUER="https://login.microsoftonline.com/${AZUREAD_TENANT_ID}/v2.0"

echo ">> Ensuring workforce pool ${POOL_ID}"
gcloud iam workforce-pools describe "${POOL_ID}" --organization="${ORG_ID}" --location=global >/dev/null 2>&1 || \
gcloud iam workforce-pools create "${POOL_ID}" \
  --organization="${ORG_ID}" --location=global \
  --display-name="Agent Gateway Workforce" \
  --session-duration=3600s

echo ">> Ensuring Entra ID OIDC provider ${PROVIDER_ID}"
gcloud iam workforce-pools providers describe "${PROVIDER_ID}" \
  --workforce-pool="${POOL_ID}" --location=global >/dev/null 2>&1 || \
gcloud iam workforce-pools providers create-oidc "${PROVIDER_ID}" \
  --workforce-pool="${POOL_ID}" --location=global \
  --display-name="Microsoft Entra ID" \
  --issuer-uri="${ISSUER}" \
  --client-id="${AZUREAD_CLIENT_ID}" \
  --web-sso-response-type=code \
  --web-sso-assertion-claims-behavior=merge-user-info-over-id-token-claims \
  --attribute-mapping="google.subject=assertion.sub,google.groups=assertion.groups,attribute.email=assertion.email,attribute.idp='azuread'" \
  --attribute-condition="'${AZUREAD_GROUP_OID}' in assertion.groups"

echo ">> Done. Entra ID users in group ${AZUREAD_GROUP_OID} can now federate."
