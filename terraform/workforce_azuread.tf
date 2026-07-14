# Microsoft Entra ID (Azure AD) OIDC provider — same workforce pool, different front door.
resource "google_iam_workforce_pool_provider" "azuread" {
  provider          = google-beta
  workforce_pool_id = google_iam_workforce_pool.main.workforce_pool_id
  location          = "global"
  provider_id       = "azuread-oidc"
  display_name      = "Microsoft Entra ID"
  description       = "Entra ID (Azure AD) OIDC federation for workforce users."

  attribute_mapping = {
    "google.subject"  = "assertion.sub"
    "google.groups"   = "assertion.groups"
    "attribute.email" = "assertion.email"
    "attribute.idp"   = "'azuread'"
  }
  # Entra emits group object IDs; require membership in the agent-users group.
  attribute_condition = "'REPLACE_WITH_ENTRA_GROUP_OBJECT_ID' in assertion.groups"

  oidc {
    # Entra ID v2.0 issuer is tenant-scoped.
    issuer_uri = "https://login.microsoftonline.com/${var.azuread_tenant_id}/v2.0"
    client_id  = var.azuread_client_id
    web_sso_config {
      response_type             = "CODE"
      assertion_claims_behavior = "MERGE_USER_INFO_OVER_ID_TOKEN_CLAIMS"
    }
  }
}
