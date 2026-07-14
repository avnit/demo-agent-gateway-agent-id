# ---------------------------------------------------------------------------
# Gemini Enterprise (Vertex AI) — least-privilege access for the agent SA.
# ---------------------------------------------------------------------------

# The agent SA can invoke Gemini models but holds NO other Vertex privileges.
# In production, prefer binding this on a specific model/endpoint resource
# rather than project-wide.
resource "google_project_iam_member" "agent_gemini_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

# Allow federated workforce users to view (but not administer) so a human can
# trace their own OBO calls. Scope tighter as needed.
resource "google_project_iam_member" "workforce_viewer" {
  project = var.project_id
  role    = "roles/aiplatform.viewer"
  member  = "principalSet://iam.googleapis.com/locations/global/workforcePools/${var.workforce_pool_id}/*"
}

# Org Policy guardrail (illustrative): restrict which Vertex AI regions the
# agent may use. Uncomment and adapt for your org.
#
# resource "google_project_organization_policy" "vertex_regions" {
#   project    = var.project_id
#   constraint = "constraints/gcp.resourceLocations"
#   list_policy {
#     allow {
#       values = ["in:us-locations"]
#     }
#   }
# }
