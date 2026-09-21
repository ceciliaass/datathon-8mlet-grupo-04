"""
Configuração centralizada do MLflow para todos os ambientes.
Detecta automaticamente: Local (SQLite) vs AWS (RDS + S3).

Uso:
    from app.mlflow_config import ENVIRONMENT, MLFLOW_TRACKING_URI
    import mlflow
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
"""
import os
import logging
from typing import Literal

logger = logging.getLogger(__name__)

# ============================================================================
# DETECÇÃO DE AMBIENTE
# ============================================================================

ENVIRONMENT: Literal["local", "aws"] = os.getenv("ENVIRONMENT", "local").lower()

# MLflow Tracking Server URI (onde está rodando o MLflow)
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://localhost:5002" if ENVIRONMENT == "local" else "http://mlflow:5000"
)

# ============================================================================
# LOCAL (Development) - SQLite + ./mlruns
# ============================================================================
if ENVIRONMENT == "local":
    # Backend store: onde os metadados (runs, params, metrics, tags) são salvos
    MLFLOW_BACKEND_STORE_URI = os.getenv(
        "MLFLOW_BACKEND_STORE_URI",
        "sqlite:///mlflow.db"
    )

    # Artifact store: onde os arquivos (modelos, CSVs, etc) são salvos
    MLFLOW_ARTIFACT_ROOT = os.getenv(
        "MLFLOW_ARTIFACT_ROOT",
        "./mlruns"
    )

    MLFLOW_ARTIFACT_STORE = "file"

# ============================================================================
# AWS (Production) - RDS PostgreSQL + S3
# ============================================================================
elif ENVIRONMENT == "aws":
    # RDS PostgreSQL para metadados
    RDS_HOST = os.getenv("RDS_HOST")
    RDS_PORT = os.getenv("RDS_PORT", "5432")
    RDS_USER = os.getenv("RDS_USER")
    RDS_PASSWORD = os.getenv("RDS_PASSWORD")
    RDS_DB = os.getenv("RDS_DB", "mlflow")

    if not all([RDS_HOST, RDS_USER, RDS_PASSWORD]):
        raise ValueError(
            "ENVIRONMENT=aws mas RDS_HOST, RDS_USER ou RDS_PASSWORD não definidos"
        )

    MLFLOW_BACKEND_STORE_URI = (
        f"postgresql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB}"
    )

    # S3 para artefatos
    AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
    S3_BUCKET = os.getenv("S3_BUCKET")

    if not S3_BUCKET:
        raise ValueError("ENVIRONMENT=aws mas S3_BUCKET não definido")

    MLFLOW_ARTIFACT_STORE = "s3"
    MLFLOW_ARTIFACT_ROOT = f"s3://{S3_BUCKET}/mlflow"

else:
    raise ValueError(f"ENVIRONMENT inválido: {ENVIRONMENT}. Use 'local' ou 'aws'")

# ============================================================================
# CONFIGURAÇÕES COMUNS
# ============================================================================

# Nome do experimento padrão (SEMPRE model-production)
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT", "model-production")

# Habilitar/desabilitar tracking (útil para testes)
ENABLE_TRACKING = os.getenv("ENABLE_MLFLOW_TRACKING", "true").lower() == "true"

# Tags padrão para todo run (contexto)
DEFAULT_TAGS = {
    "environment": ENVIRONMENT,
    "project": "datathon-8mlet-grupo-04",
    "etapa": "7-mlflow-tracking",
    "timestamp": os.getenv("DEPLOY_TIMESTAMP", ""),
}

# ============================================================================
# LOGGING DA CONFIGURAÇÃO
# ============================================================================

def log_config():
    """Exibir configuração na inicialização (para debug)."""
    logger.info(f"🎛️  MLflow Environment: {ENVIRONMENT}")
    logger.info(f"🎯 MLflow Tracking URI: {MLFLOW_TRACKING_URI}")
    logger.info(f"💾 MLflow Backend: {MLFLOW_BACKEND_STORE_URI[:60]}...")
    logger.info(f"📦 MLflow Artifacts: {MLFLOW_ARTIFACT_ROOT}")
    logger.info(f"📡 Tracking Enabled: {ENABLE_TRACKING}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    log_config()
