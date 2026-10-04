#!/usr/bin/env bash
# Envia os CSVs do dataset Olist para o GCS e (opcional) carrega no BigQuery.
# Os CSVs não são versionados (≈450 MB); baixe-os do repositório original
# ou do Kaggle ("Brazilian E-Commerce Public Dataset by Olist") para data/.
#
# Uso: ./deploy/upload_data.sh            -> só GCS
#      LOAD_BQ=1 ./deploy/upload_data.sh  -> GCS + BigQuery
set -euo pipefail
source "$(dirname "$0")/config.sh"
cd "$(dirname "$0")/.."

BQ_DATASET="${BQ_DATASET:-decision_intelligence}"

gcloud storage cp -r data/raw "gs://$GCS_BUCKET/data/"
gcloud storage cp -r data/processed "gs://$GCS_BUCKET/data/"

if [ "${LOAD_BQ:-0}" = "1" ]; then
  bq --project_id "$PROJECT_ID" show "$BQ_DATASET" >/dev/null 2>&1 \
    || bq --project_id "$PROJECT_ID" mk --location "$REGION" "$BQ_DATASET"

  for f in data/raw/*.csv data/processed/*.csv; do
    table="$(basename "$f" .csv)"
    folder="$(basename "$(dirname "$f")")"
    echo ">> $BQ_DATASET.$table"
    bq --project_id "$PROJECT_ID" load --replace --autodetect \
      --source_format CSV --skip_leading_rows 1 \
      "$BQ_DATASET.$table" "gs://$GCS_BUCKET/data/$folder/$(basename "$f")"
  done
fi
