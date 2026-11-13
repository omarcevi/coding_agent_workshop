#!/usr/bin/env bash
# Prepares the repo to call Gemini in your Google Cloud project (Vertex AI). Safe to run more than once.
# Run it from the repo root, in Cloud Shell or on a laptop with gcloud:  bash scripts/setup.sh
set -uo pipefail

ok()   { echo "✅ $*"; }
warn() { echo "⚠️  $*"; }
fail() { echo "❌ $*"; exit 1; }

cd "$(dirname "$0")/.." || exit 1

# 1. Project
PROJECT="$(gcloud config get-value project 2>/dev/null)"
[ -n "$PROJECT" ] || fail "No project is set. Run \`gcloud config set project YOUR_PROJECT_ID\` first."
gcloud projects describe "$PROJECT" --format="value(projectId)" >/dev/null 2>&1 \
  || fail "Can't open project '$PROJECT'. Check the project ID (not the name), run \`gcloud config set project YOUR_PROJECT_ID\` again, then run this script again."
ok "Project: $PROJECT"

# 2. Billing: Gemini on Vertex AI needs it. Free trial credits work.
BILLING="$(gcloud billing projects describe "$PROJECT" --format="value(billingEnabled)" 2>/dev/null)"
case "$BILLING" in
  True)  ok "Billing is linked" ;;
  False) fail "Billing isn't linked to $PROJECT. In the Cloud console, open Billing > Link a billing account, then run this script again." ;;
  *)     warn "Couldn't check billing (no permission to see it, or the billing API is busy). Continuing." ;;
esac

# 3. Credentials: Cloud Shell has them. A laptop needs application-default credentials.
if [ "${CLOUD_SHELL:-}" != "true" ]; then
  gcloud auth application-default print-access-token >/dev/null 2>&1 \
    || fail "No application-default credentials. Run \`gcloud auth application-default login\`, then run this script again."
fi
ok "Credentials found"

# 4. The Vertex AI API (about a minute the first time)
gcloud services enable aiplatform.googleapis.com --project "$PROJECT" --quiet >/dev/null 2>&1 \
  || fail "Couldn't turn on the Vertex AI API. Wait a minute, then run this script again."
ok "Vertex AI API is on"

# 5. uv and the Python packages
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1 || fail "Couldn't install uv. Check your connection, then run this script again."
fi
uv sync --quiet 2>/dev/null || fail "Couldn't install the Python packages. Run this script again."
ok "Packages installed (ADK $(uv run --quiet python -c 'import google.adk; print(google.adk.__version__)'))"

# 6. .env: the agents call Gemini in your project. "global" spreads the load across regions.
if [ -f .env ] && ! grep -q "^GOOGLE_CLOUD_PROJECT=$PROJECT$" .env; then
  cp .env .env.bak && warn "Your old .env is now .env.bak"
fi
cat > .env <<ENV
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=$PROJECT
GOOGLE_CLOUD_LOCATION=global
ENV
ok ".env written"

# 7. The practice project the agent works on
uv run --quiet reset_workspace.py >/dev/null || fail "Couldn't create workspace/. Run this script again."
ok "workspace/ has the buggy demo project"

# 8. One call to Gemini, to prove it all works
echo
uv run --quiet check_setup.py || exit 1
echo
if [ "${CLOUD_SHELL:-}" = "true" ]; then
  echo "✅ Ready. Next: uv run adk web --reload_agents --port 8080 --allow_origins https://8080-\$WEB_HOST agents"
else
  echo "✅ Ready. Next: uv run adk web --reload_agents agents"
fi
