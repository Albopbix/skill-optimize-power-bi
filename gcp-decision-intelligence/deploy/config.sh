#!/usr/bin/env bash
# Configuração compartilhada pelos scripts de deploy. Sobrescreva via env.
export PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
export REGION="${REGION:-southamerica-east1}"
export SERVICE="${SERVICE:-decision-intelligence}"
export AR_REPO="${AR_REPO:-decision-intelligence}"
export SQL_INSTANCE="${SQL_INSTANCE:-decision-intel-db}"
export SQL_TIER="${SQL_TIER:-db-f1-micro}"
export DB_NAME="${DB_NAME:-business_ai}"
export DB_USER="${DB_USER:-app_user}"
export DB_PASS_SECRET="${DB_PASS_SECRET:-decision-intel-db-pass}"
export GCS_BUCKET="${GCS_BUCKET:-${PROJECT_ID}-decision-intel}"
export RUN_SA_NAME="${RUN_SA_NAME:-decision-intel-run}"
export RUN_SA="${RUN_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
export IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${SERVICE}"
export INSTANCE_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${SQL_INSTANCE}"

if [ -z "$PROJECT_ID" ]; then
  echo "Defina PROJECT_ID ou rode: gcloud config set project <id>" >&2
  exit 1
fi
