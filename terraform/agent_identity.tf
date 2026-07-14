# ---------------------------------------------------------------------------
# Agent Identity: each agent runs as its OWN service account. No shared keys.
# ---------------------------------------------------------------------------
resource "google_service_account" "agent" {
  account_id   = var.agent_name
  display_name = "Agent Identity: ${var.agent_name}"
  description  = "Dedicated identity for the ${var.agent_name} AI agent. Least-privilege."
}

# The Agent Gateway (running on GCP) is allowed to impersonate the agent SA to
# mint short-lived tokens. Replace the member with the gateway's own identity.
resource "google_service_account_iam_member" "gateway_can_impersonate" {
  service_account_id = google_service_account.agent.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${var.agent_name}-gateway@${var.project_id}.iam.gserviceaccount.com"
}

# ---------------------------------------------------------------------------
# Workload Identity Federation: for agents running OFF Google Cloud (other
# cloud / on-prem / CI). Their platform token is exchanged for the agent SA —
# still no downloaded key file.
# ---------------------------------------------------------------------------
resource "google_iam_workload_identity_pool" "agents" {
  workload_identity_pool_id = var.workload_pool_id
  display_name              = "Agent Gateway Workloads"
  description               = "Off-GCP agent workloads federated to per-agent identities."
}

resource "google_iam_workload_identity_pool_provider" "oidc" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.agents.workload_identity_pool_id
  workload_identity_pool_provider_id = "agent-oidc"
  display_name                       = "Agent OIDC"
  attribute_mapping = {
    "google.subject"      = "assertion.sub"
    "attribute.agent"     = "assertion.agent_name"
  }
  attribute_condition = "attribute.agent == \"${var.agent_name}\""
  oidc {
    # Point this at whatever platform issues the off-GCP agent's token.
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Let the federated workload impersonate the agent SA.
resource "google_service_account_iam_member" "wif_can_impersonate" {
  service_account_id = google_service_account.agent.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.agents.name}/attribute.agent/${var.agent_name}"
}
