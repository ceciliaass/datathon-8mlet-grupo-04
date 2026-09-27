#!/bin/sh
# Monta o comando `mlflow server` a partir de env vars, para a mesma imagem
# funcionar tanto local (docker-compose, SQLite + disco) quanto na AWS
# (RDS Postgres + S3), sem precisar de dois Dockerfiles.
set -e

BACKEND_STORE_URI="${MLFLOW_BACKEND_STORE_URI:-sqlite:///mlflow.db}"
ARTIFACT_ROOT="${MLFLOW_DEFAULT_ARTIFACT_ROOT:-./mlruns}"
ALLOWED_HOSTS="${MLFLOW_ALLOWED_HOSTS:-mlflow:5000,mlflow,localhost,localhost:5000,localhost:5002,127.0.0.1,127.0.0.1:5000,127.0.0.1:5002}"
WORKERS="${MLFLOW_WORKERS:-1}"

exec mlflow server \
  --backend-store-uri "$BACKEND_STORE_URI" \
  --default-artifact-root "$ARTIFACT_ROOT" \
  --host 0.0.0.0 \
  --port 5000 \
  --workers "$WORKERS" \
  --allowed-hosts "$ALLOWED_HOSTS"
