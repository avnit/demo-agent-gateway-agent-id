variable "project_id" {
  description = "GCP project ID that hosts the agent, federation pools, and Gemini Enterprise."
  type        = string
}

variable "region" {
  description = "Default region for Vertex AI / Gemini Enterprise."
  type        = string
  default     = "us-central1"
}

variable "workforce_pool_id" {
  description = "ID for the Workforce Identity Federation pool (humans from Okta / Entra ID)."
  type        = string
  default     = "agent-gateway-workforce"
}

variable "organization_id" {
  description = "GCP organization ID (workforce pools are org-scoped)."
  type        = string
}

# ---- Okta OIDC ----
variable "okta_issuer_uri" {
  description = "Okta OIDC issuer, e.g. https://your-org.okta.com/oauth2/default"
  type        = string
}

variable "okta_client_id" {
  description = "Okta application client ID used as the OIDC audience."
  type        = string
}

# ---- Microsoft Entra ID (Azure AD) OIDC ----
variable "azuread_tenant_id" {
  description = "Entra ID tenant (directory) ID."
  type        = string
}

variable "azuread_client_id" {
  description = "Entra ID application (client) ID used as the OIDC audience."
  type        = string
}

# ---- Agent identity ----
variable "agent_name" {
  description = "Logical name of the agent; drives the service account and WIF pool IDs."
  type        = string
  default     = "gemini-support-agent"
}

variable "workload_pool_id" {
  description = "ID for the Workload Identity Federation pool (agents running off-GCP)."
  type        = string
  default     = "agent-gateway-workload"
}
