# Colab notebook — end-to-end demo

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/avnit/demo-agent-gateway-agent-id/blob/main/notebooks/demo_agent_gateway.ipynb)

**[`demo_agent_gateway.ipynb`](demo_agent_gateway.ipynb)** walks through the entire flow in the browser —
Okta / Entra ID federation → per-agent identity → Gemini Enterprise → on-behalf-of audit trail.

- **Self-contained.** Runs top to bottom with `Runtime → Run all`. No GCP project, no billing, no tokens.
- **Real logic, stubbed egress.** Every hop (STS exchange, SA impersonation, Gemini call) is the same code
  as `app/`; only outbound Google API calls are stubbed via `DEMO_MODE=1`.
- **Includes the money shot** — a least-privilege cell proving that an unauthorized user is denied at the
  gateway *before* any token is minted or the model is reached.
- **Live mode section** shows exactly what to change (`terraform apply`, `auth.authenticate_user()`,
  `DEMO_MODE=0`) to point at a real project.

> The Colab badge above works once the repo is public on GitHub under `avnit/demo-agent-gateway-agent-id`.
