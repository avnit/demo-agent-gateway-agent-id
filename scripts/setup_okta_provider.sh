#!/usr/bin/env bash
# Idempotent gcloud setup for the Okta workforce provider.
# Prefer Terraform (../terraform) for real deployments; this script is for demos and drift checks.
set -euo pipefail

: "${ORG_ID:?set ORG_ID}"
: "${OKTA_ISSUER:?set OKTA_ISSUER e.g. https://your-org.okta.com/oauth2/default}"
: "${OKTA_CLIENT_ID:?set OKTA_CLIENT_ID}"
POOL_ID="${POOL_ID:-agent-gateway-workforce}"
PROVIDER_ID="${PROVIDER_ID:-okta-oidc}"

echo ">> Ensuring workforce pool ${POOL_ID}"
gcloud iam workforce-pools describe "${POOL_ID}" --organization="${ORG_ID}" --location=global >/dev/null 2>&1 || \
gcloud iam workforce-pools create "${POOL_ID}" \
  --organization="${ORG_ID}" --location=global \
  --display-name="Agent Gateway Workforce" \
  --session-duration=3600s

echo ">> Ensuring Okta OIDC provider ${PROVIDER_ID}"
gcloud iam workforce-pools providers describe "${PROVIDER_ID}" \
  --workforce-pool="${POOL_ID}" --location=global >/dev/null 2>&1 || \
gcloud iam workforce-pools providers create-oidc "${PROVIDER_ID}" \
  --workforce-pool="${POOL_ID}" --location=global \
  --display-name="Okta" \
  --issuer-uri="${OKTA_ISSUER}" \
  --client-id="${OKTA_CLIENT_ID}" \
  --web-sso-response-type=code \
  --web-sso-assertion-claims-behavior=merge-user-info-over-id-token-claims \
  --attribute-mapping="google.subject=assertion.sub,google.groups=assertion.groups,attribute.email=assertion.email,attribute.idp='okta'" \
  --attribute-condition="'gemini-agent-users' in assertion.groups"

echo ">> Done. Okta users in group 'gemini-agent-users' can now federate."
