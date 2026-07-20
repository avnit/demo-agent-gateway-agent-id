output "workforce_pool_name" {
  description = "Full resource name of the workforce pool."
  value       = google_iam_workforce_pool.main.name
}

output "okta_provider_name" {
  description = "Okta workforce provider resource name."
  value       = google_iam_workforce_pool_provider.okta.name
}

output "azuread_provider_name" {
  description = "Entra ID workforce provider resource name."
  value       = google_iam_workforce_pool_provider.azuread.name
}

output "agent_service_account_email" {
  description = "Email of the per-agent identity."
  value       = google_service_account.agent.email
}

output "workload_identity_pool_name" {
  description = "Full resource name of the workload identity pool for off-GCP agents."
  value       = google_iam_workload_identity_pool.agents.name
}

output "audience_workforce_okta" {
  description = "STS audience for the Okta provider (use in the gateway; must include the provider segment)."
  value       = "//iam.googleapis.com/${google_iam_workforce_pool_provider.okta.name}"
}

output "audience_workforce_azuread" {
  description = "STS audience for the Entra ID provider (use in the gateway; must include the provider segment)."
  value       = "//iam.googleapis.com/${google_iam_workforce_pool_provider.azuread.name}"
}
