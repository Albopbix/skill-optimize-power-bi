#!/usr/bin/env bash
# Provisiona a infraestrutura (rodar uma vez por projeto).
# Idempotente: recursos já existentes são mantidos.
set -euo pipefail
source "$(dirname "$0")/config.sh"

echo ">> Projeto: $PROJECT_ID  Região: $REGION"

gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  aiplatform.googleapis.com \
  --project "$PROJECT_ID"

# Artifact Registry (imagens Docker)
gcloud artifacts repositories describe "$AR_REPO" --location "$REGION" --project "$PROJECT_ID" >/dev/null 2>&1 \
  || gcloud artifacts repositories create "$AR_REPO" \
       --repository-format docker --location "$REGION" --project "$PROJECT_ID"

# Bucket para modelos e dados
gcloud storage buckets describe "gs://$GCS_BUCKET" >/dev/null 2>&1 \
  || gcloud storage buckets create "gs://$GCS_BUCKET" \
       --location "$REGION" --uniform-bucket-level-access --project "$PROJECT_ID"

# Cloud SQL (PostgreSQL)
if ! gcloud sql instances describe "$SQL_INSTANCE" --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud sql instances create "$SQL_INSTANCE" \
    --database-version POSTGRES_16 --edition ENTERPRISE --tier "$SQL_TIER" \
    --region "$REGION" --project "$PROJECT_ID"
fi

gcloud sql databases describe "$DB_NAME" --instance "$SQL_INSTANCE" --project "$PROJECT_ID" >/dev/null 2>&1 \
  || gcloud sql databases create "$DB_NAME" --instance "$SQL_INSTANCE" --project "$PROJECT_ID"

# Senha do banco no Secret Manager (gerada apenas na primeira vez)
if ! gcloud secrets describe "$DB_PASS_SECRET" --project "$PROJECT_ID" >/dev/null 2>&1; then
  DB_PASS="$(openssl rand -base64 24 | tr -d '/+=')"
  printf '%s' "$DB_PASS" | gcloud secrets create "$DB_PASS_SECRET" \
    --data-file=- --replication-policy automatic --project "$PROJECT_ID"
  gcloud sql users create "$DB_USER" --instance "$SQL_INSTANCE" \
    --password "$DB_PASS" --project "$PROJECT_ID"
fi

# Service account do Cloud Run com permissões mínimas
gcloud iam service-accounts describe "$RUN_SA" --project "$PROJECT_ID" >/dev/null 2>&1 \
  || gcloud iam service-accounts create "$RUN_SA_NAME" \
       --display-name "Decision Intelligence (Cloud Run)" --project "$PROJECT_ID"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:$RUN_SA" --role roles/cloudsql.client --condition=None >/dev/null
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:$RUN_SA" --role roles/aiplatform.user --condition=None >/dev/null
gcloud secrets add-iam-policy-binding "$DB_PASS_SECRET" \
  --member "serviceAccount:$RUN_SA" --role roles/secretmanager.secretAccessor --project "$PROJECT_ID" >/dev/null
gcloud storage buckets add-iam-policy-binding "gs://$GCS_BUCKET" \
  --member "serviceAccount:$RUN_SA" --role roles/storage.objectAdmin >/dev/null

echo ">> Infraestrutura pronta. Próximo passo: ./deploy/deploy.sh"
