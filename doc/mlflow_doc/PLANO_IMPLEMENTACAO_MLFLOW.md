# 🚀 Plano de Implementação MLflow - Datathon

## Visão Geral

**Objetivo:** Integrar MLflow COMPLETO e ENRIQUECIDO em:
- ✅ Notebooks (03 e 04)
- ✅ API FastAPI (app/main.py)
- ✅ Local com Docker Compose (SQLite)
- ✅ AWS em produção (RDS PostgreSQL + S3)

**Resultado final:** Sistema production-ready com rastreamento completo de experimentos, modelos versionados e monitoramento em tempo real.

---

## 📋 Arquivos a Criar/Modificar

```
datathon-8mlet-grupo-04/
├── app/
│   ├── main.py                    ← MODIFICAR (adicionar MLflow completo)
│   ├── mlflow_config.py           ← CRIAR (configuração centralizada)
│   ├── mlflow_utils.py            ← CRIAR (funções reusáveis de tracking)
│   └── requirements.txt           ← MODIFICAR (adicionar mlflow se não houver)
│
├── notebooks/
│   ├── 03_Baseline_e_Thompson.ipynb      ← MODIFICAR (adicionar tracking)
│   ├── 04_Avaliacao_e_Golden_Set.ipynb   ← MODIFICAR (adicionar tracking)
│   └── 07_MLflow_Tracking.ipynb          ← CRIAR (setup e demo)
│
├── deploy/
│   ├── docker-compose.yml         ← VERIFICAR (MLflow já está lá)
│   └── mlflow-config/
│       └── mlflow.env             ← CRIAR (variáveis de ambiente)
│
├── scripts/
│   └── setup_mlflow.sh            ← CRIAR (setup inicial)
│
└── doc/
    └── PLANO_IMPLEMENTACAO_MLFLOW.md  ← ESTE ARQUIVO

```

---

## 🔧 Etapa 1: Criar Configuração Centralizada

### Arquivo: `app/mlflow_config.py`

Este arquivo centraliza TODA a configuração de MLflow, permitindo trocar de SQLite (local) para RDS (AWS) sem mudar código.

```python
"""
Configuração centralizada do MLflow para todos os ambientes.
Detecta automaticamente: Local (SQLite) vs AWS (RDS + S3).
"""
import os
import logging
from typing import Literal

logger = logging.getLogger(__name__)

# ============================================================================
# DETECÇÃO DE AMBIENTE
# ============================================================================

ENVIRONMENT: Literal["local", "aws"] = os.getenv("ENVIRONMENT", "local").lower()
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://localhost:5000" if ENVIRONMENT == "local" else "http://mlflow:5000"
)

# ============================================================================
# LOCAL (Development) - SQLite + ./mlruns
# ============================================================================
if ENVIRONMENT == "local":
    MLFLOW_BACKEND_STORE_URI = "sqlite:///mlflow.db"
    MLFLOW_ARTIFACT_ROOT = "./mlruns"
    MLFLOW_ARTIFACT_STORE = "file"  # Local filesystem
    
# ============================================================================
# AWS (Production) - RDS PostgreSQL + S3
# ============================================================================
elif ENVIRONMENT == "aws":
    # RDS PostgreSQL
    RDS_HOST = os.getenv("RDS_HOST")
    RDS_PORT = os.getenv("RDS_PORT", "5432")
    RDS_USER = os.getenv("RDS_USER")
    RDS_PASSWORD = os.getenv("RDS_PASSWORD")
    RDS_DB = os.getenv("RDS_DB", "mlflow")
    
    MLFLOW_BACKEND_STORE_URI = (
        f"postgresql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:{RDS_PORT}/{RDS_DB}"
    )
    
    # S3
    AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
    S3_BUCKET = os.getenv("S3_BUCKET")
    MLFLOW_ARTIFACT_STORE = "s3"
    MLFLOW_ARTIFACT_ROOT = f"s3://{S3_BUCKET}/mlflow"

else:
    raise ValueError(f"ENVIRONMENT inválido: {ENVIRONMENT}")

# ============================================================================
# CONFIGURAÇÕES COMUNS
# ============================================================================

EXPERIMENT_NAME = "datathon-bandit-etapa7"
ENABLE_TRACKING = os.getenv("ENABLE_MLFLOW_TRACKING", "true").lower() == "true"

# Tags padrão para todo run
DEFAULT_TAGS = {
    "environment": ENVIRONMENT,
    "project": "datathon-8mlet-grupo-04",
    "etapa": "7-mlflow-tracking"
}

# ============================================================================
# LOGGING
# ============================================================================

def log_config():
    """Exibir configuração na inicialização."""
    logger.info(f"MLflow Environment: {ENVIRONMENT}")
    logger.info(f"MLflow Tracking URI: {MLFLOW_TRACKING_URI}")
    logger.info(f"MLflow Backend: {MLFLOW_BACKEND_STORE_URI[:50]}...")
    logger.info(f"MLflow Artifacts: {MLFLOW_ARTIFACT_ROOT}")
    logger.info(f"Tracking Enabled: {ENABLE_TRACKING}")
```

---

## 🛠️ Etapa 2: Criar Utilitários de Tracking Reusáveis

### Arquivo: `app/mlflow_utils.py`

Encapsula todas as operações de MLflow para facilitar reuso em notebooks e API.

```python
"""
Utilitários reusáveis para tracking MLflow.
Oferece contextos e decoradores que funcionam em qualquer ambiente.
"""
import json
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any
from datetime import datetime

import mlflow

from app.mlflow_config import (
    MLFLOW_TRACKING_URI,
    EXPERIMENT_NAME,
    ENABLE_TRACKING,
    DEFAULT_TAGS,
)

logger = logging.getLogger(__name__)

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

def initialize_mlflow():
    """Inicializar MLflow (executar na startup da API)."""
    if not ENABLE_TRACKING:
        logger.info("MLflow tracking desativado")
        return
    
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(EXPERIMENT_NAME)
        logger.info(f"MLflow inicializado: {MLFLOW_TRACKING_URI}")
    except Exception as e:
        logger.error(f"Erro ao inicializar MLflow: {e}")
        # Continuar mesmo se MLflow falhar (graceful degradation)

# ============================================================================
# CONTEXTOS (para usar em `with` statements)
# ============================================================================

@contextmanager
def track_run(run_name: str, tags: Optional[Dict[str, str]] = None):
    """
    Context manager para rastrear um run do MLflow.
    
    Uso:
        with track_run("minha_etapa", tags={"tipo": "predição"}):
            mlflow.log_param("param1", value1)
            mlflow.log_metric("metric1", value1)
    """
    if not ENABLE_TRACKING:
        yield
        return
    
    try:
        all_tags = {**DEFAULT_TAGS, **(tags or {})}
        with mlflow.start_run(run_name=run_name) as run:
            for key, value in all_tags.items():
                mlflow.set_tag(key, str(value))
            logger.debug(f"Run iniciado: {run.info.run_id}")
            yield run
    except Exception as e:
        logger.error(f"Erro no run: {e}")
        yield None

# ============================================================================
# FUNÇÕES ESPECÍFICAS PARA O DATATHON
# ============================================================================

def log_notebook_execution(
    notebook_name: str,
    etapa: str,
    params: Dict[str, Any],
    metrics: Dict[str, float],
    artifacts: Optional[Dict[str, str]] = None
):
    """
    Log completo de execução de notebook.
    
    Args:
        notebook_name: "03_Baseline_e_Thompson"
        etapa: "etapa3_simulacao"
        params: {"seed": 42, "test_size": 0.3, ...}
        metrics: {"baseline_conv": 0.10, "thompson_conv": 0.13, ...}
        artifacts: {"resultados.csv": "/path/to/file"}
    """
    if not ENABLE_TRACKING:
        return None
    
    try:
        with track_run(run_name=f"{notebook_name}_{etapa}") as run:
            if run is None:
                return None
            
            # Log parâmetros
            for key, value in params.items():
                if isinstance(value, (int, float, str, bool)):
                    mlflow.log_param(key, value)
            
            # Log métricas
            for key, value in metrics.items():
                mlflow.log_metric(key, float(value))
            
            # Log artefatos
            if artifacts:
                for artifact_name, artifact_path in artifacts.items():
                    try:
                        mlflow.log_artifact(artifact_path, artifact_name=artifact_name)
                    except Exception as e:
                        logger.warning(f"Erro ao logar artefato {artifact_name}: {e}")
            
            run_id = run.info.run_id
            logger.info(f"Notebook run logged: {run_id}")
            return run_id
    except Exception as e:
        logger.error(f"Erro ao logar execução do notebook: {e}")
        return None

def log_api_inference(
    decision_id: str,
    arm_selected: str,
    confidence: float,
    client_features: Optional[Dict[str, Any]] = None,
    model_version: Optional[str] = None
):
    """
    Log de predição feita pela API.
    
    Args:
        decision_id: ID único da decisão (ex: "DECISION_12345")
        arm_selected: Braço escolhido ("cellular" ou "telephone")
        confidence: Confiança da predição (0-1)
        client_features: Features do cliente (dicionário)
        model_version: Versão do modelo usada
    """
    if not ENABLE_TRACKING:
        return None
    
    try:
        with track_run("api_inference") as run:
            if run is None:
                return None
            
            mlflow.set_tag("decision_id", decision_id)
            mlflow.set_tag("arm_selected", arm_selected)
            mlflow.set_tag("model_version", model_version or "unknown")
            
            mlflow.log_param("confidence_threshold", confidence)
            mlflow.log_metric("arm_value", 1 if arm_selected == "cellular" else 0)
            mlflow.log_metric("confidence", confidence)
            
            if client_features:
                mlflow.log_dict(client_features, "client_features.json")
            
            logger.debug(f"Inference logged: {decision_id}")
            return run.info.run_id
    except Exception as e:
        logger.error(f"Erro ao logar predição: {e}")
        return None

def log_feedback_result(
    decision_id: str,
    arm: str,
    conversion: bool,
    delay_seconds: Optional[int] = None
):
    """
    Log do resultado/feedback de uma decisão.
    
    Args:
        decision_id: ID da decisão original
        arm: Braço que foi escolhido
        conversion: Se houve conversão (True/False)
        delay_seconds: Tempo entre decisão e feedback
    """
    if not ENABLE_TRACKING:
        return None
    
    try:
        with track_run("api_feedback") as run:
            if run is None:
                return None
            
            mlflow.set_tag("decision_id", decision_id)
            mlflow.set_tag("arm", arm)
            
            mlflow.log_param("conversion_observed", int(conversion))
            mlflow.log_metric("conversion", 1.0 if conversion else 0.0)
            
            if delay_seconds is not None:
                mlflow.log_metric("feedback_delay_seconds", float(delay_seconds))
            
            logger.debug(f"Feedback logged: {decision_id} → {conversion}")
            return run.info.run_id
    except Exception as e:
        logger.error(f"Erro ao logar feedback: {e}")
        return None

def log_bandit_stats(
    arm_stats: Dict[str, Dict[str, int]]
):
    """
    Log das estatísticas atualizadas do Thompson Sampling.
    
    Args:
        arm_stats: {
            "cellular": {"trials": 100, "wins": 15},
            "telephone": {"trials": 50, "wins": 4}
        }
    """
    if not ENABLE_TRACKING:
        return None
    
    try:
        with track_run("bandit_stats") as run:
            if run is None:
                return None
            
            for arm, stats in arm_stats.items():
                trials = stats.get("trials", 0)
                wins = stats.get("wins", 0)
                rate = wins / trials if trials > 0 else 0
                
                mlflow.log_metric(f"{arm}_trials", float(trials))
                mlflow.log_metric(f"{arm}_wins", float(wins))
                mlflow.log_metric(f"{arm}_rate", float(rate))
            
            logger.debug(f"Bandit stats logged")
            return run.info.run_id
    except Exception as e:
        logger.error(f"Erro ao logar stats do bandit: {e}")
        return None
```

---

## 📝 Etapa 3: Modificar `app/main.py`

Adicione no **TOPO** do arquivo:

```python
# Adicionar após imports existentes
from app.mlflow_config import ENVIRONMENT, ENABLE_TRACKING
from app.mlflow_utils import (
    initialize_mlflow,
    log_api_inference,
    log_feedback_result,
    log_bandit_stats,
)

# Na inicialização (antes ou logo após criar a app FastAPI)
initialize_mlflow()

logger = logging.getLogger(__name__)
```

Substitua as funções `_log_recommendation` e `_log_feedback` por:

```python
def _log_recommendation(decision_id: str, arm: str, client_context: dict | None) -> None:
    """Log melhorado da recomendação."""
    if not ENABLE_TRACKING:
        return
    
    log_api_inference(
        decision_id=decision_id,
        arm_selected=arm,
        confidence=0.5,  # Placeholder, ajuste se houver confidence real
        client_features=client_context or {},
        model_version="thompson_v1"
    )

def _log_feedback(decision_id: str, arm: str, reward: int) -> None:
    """Log melhorado do feedback."""
    if not ENABLE_TRACKING:
        return
    
    log_feedback_result(
        decision_id=decision_id,
        arm=arm,
        conversion=bool(reward),
        delay_seconds=None  # Placeholder
    )
```

---

## 📓 Etapa 4: Modificar Notebooks

### Notebook: `03_Baseline_e_Thompson.ipynb`

**Célula 1 (Setup):** Adicione logo depois dos imports:

```python
import sys
sys.path.insert(0, '..')

from app.mlflow_config import ENVIRONMENT, initialize_mlflow
from app.mlflow_utils import log_notebook_execution, track_run

# Inicializar MLflow
initialize_mlflow()
```

**Célula ao final (Logging):** Após calcular métricas, adicione:

```python
# Logar execução no MLflow
params = {
    "environment": ENVIRONMENT,
    "dataset": "bank-term-deposit-subscription",
    "test_size": 0.30,
    "seed": 42,
    "baseline_policy": "regra fixa (sempre telephone)",
    "algoritmo_adaptativo": "MABWiser ThompsonSampling",
}

metrics = {
    "baseline_conversion": float(metrics['baseline_conversion']),
    "thompson_conversion": float(metrics['thompson_conversion']),
    "conversion_lift_relative_pct": float(metrics['conversion_lift_relative'] * 100),
}

artifacts = {
    "resultados": str(RESULTS_PATH),
    "metricas": str(METRICS_PATH),
}

run_id = log_notebook_execution(
    notebook_name="03_Baseline_e_Thompson",
    etapa="etapa3_simulacao",
    params=params,
    metrics=metrics,
    artifacts=artifacts
)

print(f"\n✅ Experimento logado no MLflow: {run_id}")
print(f"   Local: mlflow ui --backend-store-uri sqlite:///mlflow.db")
```

### Notebook: `04_Avaliacao_e_Golden_Set.ipynb`

Similar ao anterior, adicionar:

```python
# Setup
import sys
sys.path.insert(0, '..')
from app.mlflow_utils import log_notebook_execution, track_run

# Ao final
run_id = log_notebook_execution(
    notebook_name="04_Avaliacao_e_Golden_Set",
    etapa="etapa4_avaliacao",
    params={"n_golden_cases": len(golden_set)},
    metrics={"auc": float(auc_score), "precision": float(precision)},
    artifacts={"golden_set.csv": str(golden_set_path)}
)
```

---

## 🐳 Etapa 5: Configurar Docker Compose

Arquivo: `deploy/mlflow-config/mlflow.env`

```bash
# MLflow Configuration for Docker Compose
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_BACKEND_STORE_URI=sqlite:////mlflow/mlflow.db
MLFLOW_ARTIFACT_ROOT=/mlflow/mlruns
MLFLOW_DEFAULT_ARTIFACT_ROOT=/mlflow/mlruns

# API Environment
ENVIRONMENT=local
ENABLE_MLFLOW_TRACKING=true
```

Verificar que `docker-compose.yml` tem:

```yaml
services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5002:5000"  # Remapeado para 5002 no host
    volumes:
      - ./mlflow.db:/mlflow/mlflow.db
      - ./mlruns:/mlflow/mlruns
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - MLFLOW_BACKEND_STORE_URI=sqlite:////mlflow/mlflow.db
      - MLFLOW_ARTIFACT_ROOT=/mlflow/mlruns
    command: mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:////mlflow/mlflow.db

  fastapi:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - mlflow
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - ENVIRONMENT=local
      - ENABLE_MLFLOW_TRACKING=true
```

---

## 🚀 Etapa 6: Testar Localmente

### Passo 1: Iniciar tudo

```bash
cd datathon-8mlet-grupo-04

# Terminal 1: Docker Compose
docker compose -f deploy/docker-compose.yml up -d

# Terminal 2: Rodar notebooks
jupyter notebook notebooks/03_Baseline_e_Thompson.ipynb
```

### Passo 2: Verificar logs

```bash
# Ver logs da API
docker compose -f deploy/docker-compose.yml logs -f fastapi

# Ver logs do MLflow
docker compose -f deploy/docker-compose.yml logs -f mlflow

# Acessar MLflow UI
# http://localhost:5002/
```

### Passo 3: Testar API

```bash
# Health check
curl http://localhost:8000/health

# Fazer predição
curl -X POST http://localhost:8000/recomendar \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "C123", "age": 35}'

# Verificar logs no MLflow UI
# http://localhost:5002/ → deve mostrar novo run "api_inference"
```

---

## ☁️ Etapa 7: Deploy na AWS

### Variáveis de Ambiente (Terraform)

```hcl
# deploy/aws/terraform/vars.tf
variable "mlflow_rds_host" {
  default = "seu-rds-endpoint.rds.amazonaws.com"
}

variable "mlflow_rds_user" {
  default = "mlflow_user"
}

variable "mlflow_s3_bucket" {
  default = "datathon-mlflow-artifacts"
}

variable "mlflow_artifact_root" {
  default = "s3://datathon-mlflow-artifacts/mlflow"
}
```

### Task Definition ECS (atualizar)

```json
{
  "name": "fastapi",
  "environment": [
    {
      "name": "ENVIRONMENT",
      "value": "aws"
    },
    {
      "name": "MLFLOW_TRACKING_URI",
      "value": "http://mlflow:5000"
    },
    {
      "name": "ENABLE_MLFLOW_TRACKING",
      "value": "true"
    },
    {
      "name": "RDS_HOST",
      "value": "seu-rds-endpoint.rds.amazonaws.com"
    },
    {
      "name": "RDS_PORT",
      "value": "5432"
    },
    {
      "name": "RDS_USER",
      "valueFrom": "arn:aws:secretsmanager:us-east-2:ACCOUNT:secret:mlflow-rds-user"
    },
    {
      "name": "RDS_PASSWORD",
      "valueFrom": "arn:aws:secretsmanager:us-east-2:ACCOUNT:secret:mlflow-rds-password"
    },
    {
      "name": "S3_BUCKET",
      "value": "datathon-mlflow-artifacts"
    }
  ]
}
```

---

## ✅ Checklist de Implementação

### Fase 1: Arquivos Base
- [ ] Criar `app/mlflow_config.py`
- [ ] Criar `app/mlflow_utils.py`
- [ ] Modificar `app/main.py` (adicionar imports e inicialização)
- [ ] Criar `deploy/mlflow-config/mlflow.env`

### Fase 2: Notebooks
- [ ] Adicionar setup MLflow em `03_Baseline_e_Thompson.ipynb`
- [ ] Adicionar logging ao final de `03_Baseline_e_Thompson.ipynb`
- [ ] Adicionar setup MLflow em `04_Avaliacao_e_Golden_Set.ipynb`
- [ ] Adicionar logging ao final de `04_Avaliacao_e_Golden_Set.ipynb`

### Fase 3: Testes Locais
- [ ] Executar `docker compose up -d`
- [ ] Rodar notebooks (03 e 04)
- [ ] Verificar logs no MLflow UI (http://localhost:5002)
- [ ] Fazer requisições na API e verificar logs
- [ ] Comparar baseline vs Thompson no MLflow UI

### Fase 4: Testes em Produção (AWS)
- [ ] Atualizar variáveis de ambiente no Terraform
- [ ] Deploy na AWS com `terraform apply`
- [ ] Verificar MLflow em `http://alb-endpoint:5000`
- [ ] Fazer requisições na API na AWS
- [ ] Comparar dados locais vs AWS no MLflow

### Fase 5: Demo Day
- [ ] Criar video mostrando:
  - Notebooks rodando com MLflow tracking
  - MLflow UI comparando baseline vs Thompson
  - API rodando e logando predições
  - Dashboard ao vivo em produção

---

## 📊 Resultado Esperado

Depois de implementar, você terá:

```
MLflow UI (Local e AWS):
├── Experiment: datathon-bandit-etapa7
│   ├── Run: 03_Baseline_e_Thompson_etapa3_simulacao
│   │   ├── Params: seed, test_size, algoritmo, etc
│   │   ├── Metrics: baseline_conv=10.44%, thompson_conv=13.67%, +31% lift
│   │   └── Artifacts: resultados.csv, métricas.json
│   │
│   ├── Run: 04_Avaliacao_e_Golden_Set_etapa4_avaliacao
│   │   ├── Metrics: AUC=0.79, precision=0.68
│   │   └── Artifacts: golden_set.csv
│   │
│   └── Runs de API (em tempo real):
│       ├── api_inference: decision_id, arm_selected, confidence
│       ├── api_feedback: conversion=1 ou 0
│       └── bandit_stats: cellular_rate, telephone_rate

Dashboard:
├── Gráfico de convergência: Thompson vs Baseline
├── Comparação de métricas lado-a-lado
├── Histórico de predições em tempo real
└── Performance do bandit (arms wins/losses)
```

---

**Tempo estimado:** 2-3 horas de implementação  
**Dificuldade:** Média (cópia + adaptação de código)  
**Valor agregado:** Sistema production-ready com rastreamento completo! 🚀
