# Workforce Identity Federation pool — brings enterprise humans into GCP.
# One pool holds multiple providers (Okta + Entra ID share this pool).
resource "google_iam_workforce_pool" "main" {
  provider          = google-beta
  parent            = "organizations/${var.organization_id}"
  location          = "global"
  workforce_pool_id = var.workforce_pool_id
  display_name      = "Agent Gateway Workforce"
  description       = "Federated humans (Okta + Entra ID) that agents can act on-behalf-of."
  session_duration  = "3600s"
}

# Okta OIDC provider.
resource "google_iam_workforce_pool_provider" "okta" {
  provider            = google-beta
  workforce_pool_id   = google_iam_workforce_pool.main.workforce_pool_id
  location            = "global"
  provider_id         = "okta-oidc"
  display_name        = "Okta"
  description         = "Okta OIDC federation for workforce users."
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "google.groups"        = "assertion.groups"
    "attribute.email"      = "assertion.email"
    "attribute.idp"        = "'okta'"
  }
  # Only accept tokens for users in the security-cleared Okta group.
  attribute_condition = "'gemini-agent-users' in assertion.groups"

  oidc {
    issuer_uri = var.okta_issuer_uri
    client_id  = var.okta_client_id
    web_sso_config {
      response_type             = "CODE"
      assertion_claims_behavior = "MERGE_USER_INFO_OVER_ID_TOKEN_CLAIMS"
    }
  }
}
