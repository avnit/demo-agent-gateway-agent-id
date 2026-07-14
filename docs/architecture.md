# Architecture: Agent Identity, federation, and the Agent Gateway

This document explains the trust chain end to end. It is deliberately vendor-precise so it
survives a security review, not just a slide.

## The problem with agentic AI identity

A naive agent holds a long-lived API key or a JSON service-account key baked into an image.
That key is:

- **Shared** — every request looks the same; you cannot attribute an action to a human or an agent.
- **Static** — it does not expire; a leak is a standing compromise.
- **Over-scoped** — one key usually grants far more than one agent needs.

This demo replaces that with **short-lived, federated, per-agent identity** and a broker that
enforces authorization before Gemini Enterprise is ever called.

## Three identity primitives

### 1. Workforce Identity Federation (human → GCP)

Brings **Okta** and **Microsoft Entra ID (Azure AD)** users into GCP as first-class principals
without provisioning Google passwords. The IdP issues an OIDC ID token; Google's Security Token
Service (STS) exchanges it for a federated access token scoped to a **workforce pool**.

- Subject: `principal://iam.googleapis.com/locations/global/workforcePools/POOL/subject/USER`
- Attribute mapping pulls `email`, `groups`, etc. from the IdP claims for use in IAM conditions.

### 2. Agent Identity (the agent → GCP resources)

Each agent runs as its **own service account** — never a shared one. The agent obtains
credentials one of two ways:

- **Workload Identity Federation** when the agent runs outside GCP (e.g. another cloud, on-prem,
  or a CI runner) — the workload's platform token is exchanged for GCP credentials, no key file.
- **Service-account impersonation** when the Agent Gateway (running on GCP) mints a short-lived
  token (`iam.serviceAccounts.getAccessToken`) for the specific agent SA.

The agent SA holds only the IAM roles that one agent needs — typically `roles/aiplatform.user`
scoped to the Gemini Enterprise resource, and nothing else.

### 3. On-Behalf-Of (OBO)

The Agent Gateway carries the **original human subject** from the Workforce token into the Gemini
call as context, so audit logs show *both* the acting agent SA and the human who initiated the
request. This is what lets you answer "which employee's action caused this model call?".

## The token exchange, concretely

```
Okta / Entra ID  --(1) OIDC id_token-->  Google STS
Google STS       --(2) federated token-->  Agent Gateway
Agent Gateway    --(3) generateAccessToken(agent-sa)-->  IAM Credentials API
IAM Credentials  --(4) short-lived SA token-->  Agent Gateway
Agent Gateway    --(5) Vertex AI predict + OBO subject-->  Gemini Enterprise
```

1. **OIDC**: the human's IdP token, audience-bound to the workforce provider.
2. **STS `token.exchange`**: `grant_type=urn:ietf:params:oauth:grant-type:token-exchange`,
   `requested_token_type=urn:ietf:params:oauth:token-type:access_token`, subject token = the OIDC token.
3. **Impersonation**: gateway calls `iamcredentials.googleapis.com generateAccessToken` for the
   agent SA, with the federated principal as the caller. IAM checks
   `roles/iam.serviceAccountTokenCreator` on that SA.
4. Short-lived (default 1h, tune down) SA access token returned.
5. Gateway calls Vertex AI (`aiplatform.googleapis.com`) with the SA token. IAM + Org Policy
   authorize the model + method; the human subject rides along as a request attribute for audit.

## Trust boundaries

| Boundary | Who is trusted | Control |
|----------|----------------|---------|
| IdP → STS | Only the configured Okta/Entra issuer + audience | Provider config, `attribute_condition` |
| STS → Agent SA | Only principals granted `serviceAccountTokenCreator` | IAM binding on the SA |
| Agent SA → Gemini | Only the roles bound to the SA | IAM + Org Policy (`aiplatform` restrictions) |
| Gateway network | Private egress to `*.googleapis.com` | VPC-SC perimeter (recommended) |

## Hardening checklist (production, beyond this demo)

- Put Gemini Enterprise / Vertex AI inside a **VPC Service Controls** perimeter.
- Constrain the workforce provider with an `attribute_condition` (e.g. require a specific Okta group).
- Set SA token lifetime to the minimum (`--lifetime` on impersonation) — minutes, not the 1h default.
- Enable **Data Access audit logs** for `aiplatform.googleapis.com` so OBO subjects are recorded.
- Bind `roles/aiplatform.user` on the **specific model/endpoint resource**, not project-wide.
- Rotate nothing manually — there are no long-lived keys in this design. That's the point.
