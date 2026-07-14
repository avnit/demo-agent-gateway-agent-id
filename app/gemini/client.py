"""Gemini Enterprise (Vertex AI) call wrapper.

The gateway calls Gemini with the AGENT's short-lived token, and passes the original
human subject as an on-behalf-of label so the Vertex AI audit log records both.
"""
from __future__ import annotations

import json
import os

import requests  # type: ignore

VERTEX_ENDPOINT = (
    "https://{region}-aiplatform.googleapis.com/v1/projects/{project}/locations/"
    "{region}/publishers/google/models/{model}:generateContent"
)


def _demo_mode() -> bool:
    return os.environ.get("DEMO_MODE", "1") != "0"


class GeminiEnterpriseClient:
    def __init__(self, project_id: str, region: str, model: str) -> None:
        self.project_id = project_id
        self.region = region
        self.model = model

    def generate(self, *, agent_access_token: str, on_behalf_of: str, prompt: str) -> str:
        """Call Gemini Enterprise. Authorization is the agent SA; OBO subject is labeled."""
        if _demo_mode():
            return (
                f"[DEMO Gemini Enterprise response]\n"
                f"model={self.model} region={self.region}\n"
                f"acting_identity=agent-sa on_behalf_of={on_behalf_of}\n"
                f"answer: (a real call would return the model completion for: {prompt!r})"
            )

        url = VERTEX_ENDPOINT.format(region=self.region, project=self.project_id, model=self.model)
        headers = {
            "Authorization": f"Bearer {agent_access_token}",
            "Content-Type": "application/json",
            # Surface the human subject for audit correlation.
            "X-Goog-Request-Reason": f"agent-obo:{on_behalf_of}",
        }
        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "labels": {"on_behalf_of": on_behalf_of.replace("@", "_at_")},
        }
        resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
