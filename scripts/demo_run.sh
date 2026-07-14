#!/usr/bin/env bash
# End-to-end local walkthrough in DEMO_MODE (no live GCP calls).
set -euo pipefail
cd "$(dirname "$0")/../app"

export DEMO_MODE="${DEMO_MODE:-1}"

echo "========================================================"
echo " Agent Gateway demo — Okta front door"
echo "========================================================"
python agent_gateway.py --idp okta --prompt "Summarize our Q3 security posture in three bullets."

echo
echo "========================================================"
echo " Agent Gateway demo — Microsoft Entra ID front door"
echo "========================================================"
python agent_gateway.py --idp azuread --prompt "Draft a 3-step incident response timeline."

echo
echo "Note the AUDIT lines above: each Gemini call carries BOTH the agent SA"
echo "and the on-behalf-of human subject. Flip DEMO_MODE=0 with real creds for live calls."
