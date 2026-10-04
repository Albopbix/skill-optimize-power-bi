#!/usr/bin/env bash
# Build da imagem (Cloud Build) + deploy no Cloud Run.
set -euo pipefail
source "$(dirname "$0")/config.sh"
cd "$(dirname "$0")/.."

TAG="${TAG:-$(date +%Y%m%d-%H%M%S)}"

gcloud builds submit --tag "$IMAGE:$TAG" --project "$PROJECT_ID" .

# --session-affinity: o estado do Streamlit (dataset carregado, modelo
# treinado) vive na memória da instância; a afinidade mantém o usuário
# na mesma instância durante a sessão.
gcloud run deploy "$SERVICE" \
  --image "$IMAGE:$TAG" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --service-account "$RUN_SA" \
  --add-cloudsql-instances "$INSTANCE_CONNECTION_NAME" \
  --set-env-vars "INSTANCE_CONNECTION_NAME=$INSTANCE_CONNECTION_NAME,DB_NAME=$DB_NAME,DB_USER=$DB_USER,GCS_BUCKET=$GCS_BUCKET,GEMINI_ENABLED=$GEMINI_ENABLED,GEMINI_MODEL=$GEMINI_MODEL,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$GEMINI_LOCATION" \
  --set-secrets "DB_PASS=$DB_PASS_SECRET:latest" \
  --memory 2Gi --cpu 2 --timeout 3600 \
  --min-instances 0 --max-instances 3 \
  --session-affinity \
  --allow-unauthenticated

gcloud run services describe "$SERVICE" --region "$REGION" --project "$PROJECT_ID" \
  --format 'value(status.url)'
