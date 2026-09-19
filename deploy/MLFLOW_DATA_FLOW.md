# 📊 MLflow - Fluxo de Dados e Consumo

Guia visual sobre **o que o MLflow consome** em cada ambiente (local vs AWS) e qual é a arquitetura de armazenamento.

---

## 🔄 Comparação: Local vs AWS

### 📍 Ambiente LOCAL (Docker Compose)

```
┌─────────────────────────────────────────────────────────┐
│                    Seu Computador                        │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  projeto/                                        │   │
│  │  ├── mlruns/              ◄─── Backend Artifact  │   │
│  │  │   └── 1/               (Runs, Artifacts)      │   │
│  │  │       └── run-id/                             │   │
│  │  │           └── artifacts/                      │   │
│  │  ├── mlflow.db            ◄─── Backend Store     │   │
│  │  │                        (Metadata - SQLite)    │   │
│  │  ├── app/                                        │   │
│  │  ├── deploy/                                     │   │
│  │  └── notebooks/                                  │   │
│  │      ├── 03_Baseline...  ─┐                      │   │
│  │      ├── 04_Avaliacao...  ├─► Criam runs no     │   │
│  │      └── mlruns/          ─┘   MLflow (ID: 1)   │   │
│  └──────────────────────────────────────────────────┘   │
│                         ▲                                │
│          ┌──────────────┴──────────────┐               │
│          │                             │                │
│  ┌───────┴────────┐          ┌────────┴──────┐        │
│  │  MLflow Server │          │  FastAPI       │        │
│  │  (porta 5002)  │          │  (porta 8000)  │        │
│  │                │          │                │        │
│  │ Backend Store: │          │ Tracking URI:  │        │
│  │ sqlite:///..   │          │ http://mlflow  │        │
│  │                │          │ :5000          │        │
│  │ Artifact Root: │          │                │        │
│  │ /app/mlruns    │          │ (logs runs)    │        │
│  └────────────────┘          └────────────────┘        │
│         │                             │                 │
│         └─────────────┬───────────────┘                │
│                       │                                │
│                 Compartilham:                          │
│                 ../mlruns (mount)                      │
│                 ../mlflow.db (mount)                   │
└─────────────────────────────────────────────────────────┘

Docker Compose (deploy/docker-compose.yml):
  mlflow:
    - Monta ../mlruns como /app/mlruns
    - Monta ../mlflow.db como /app/mlflow.db
    - Variáveis:
      MLFLOW_DEFAULT_ARTIFACT_ROOT=/app/mlruns
      MLFLOW_BACKEND_STORE_URI=sqlite:////app/mlflow.db

  fastapi:
    - Acessa MLflow via http://mlflow:5000 (nome do serviço)
    - Mesmos mounts (compartilham dados)
    - MLFLOW_TRACKING_URI=http://mlflow:5000
```

**O que é armazenado:**
- ✅ **mlruns/1/** — Runs dos notebooks (EDA, Baseline, Avaliação)
- ✅ **mlruns/2/** — Runs da API (recomendações e feedback em tempo real)
- ✅ **mlflow.db** — Banco de dados SQLite com metadados (experiments, runs, parâmetros, métricas)

---

### ☁️ Ambiente AWS (Terraform)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AWS (us-east-2)                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Application Load Balancer (ALB)                             │  │
│  │  - Porta 80:   /recomendar, /feedback, /stats, /health      │  │
│  │  - Porta 5000: MLflow UI                                     │  │
│  └──────────────┬───────────────────────────────────────────────┘  │
│                 │                                                    │
│     ┌───────────┴───────────┐                                      │
│     │                       │                                       │
│  ┌──▼─────────────┐   ┌─────▼──────────────┐                      │
│  │ ECS Fargate    │   │  ECS Fargate       │                      │
│  │ (FastAPI)      │   │  (MLflow Server)   │                      │
│  │                │   │                    │                      │
│  │ Tasks: 1       │   │ Tasks: 1           │                      │
│  │ CPU: 0.25 vCPU │   │ CPU: 0.25 vCPU    │                      │
│  │ Mem: 512 MB    │   │ Mem: 512 MB        │                      │
│  │                │   │                    │                      │
│  │ Env:           │   │ Env:               │                      │
│  │ - MLFLOW_      │   │ - MLFLOW_          │                      │
│  │   TRACKING_URI │   │   BACKEND_STORE_  │                      │
│  │   =http://ALB  │   │   URI=postgres://  │                      │
│  │   :5000        │   │   (Secrets Mgr)    │                      │
│  │                │   │ - MLFLOW_DEFAULT_  │                      │
│  │ Logs:          │   │   ARTIFACT_ROOT=   │                      │
│  │ CloudWatch     │   │   s3://bucket/...  │                      │
│  │ /ecs/fastapi   │   │                    │                      │
│  │                │   │ Logs:              │                      │
│  │ Data:          │   │ CloudWatch         │                      │
│  │ DynamoDB       │   │ /ecs/mlflow        │                      │
│  └────────────┬───┘   └────┬───────────────┘                      │
│               │            │                                       │
│               │            │                                       │
│  ┌────────────▼────────────▼──────────────┐                       │
│  │        Secrets Manager                 │                       │
│  │  datathon-bandit-rds-credentials      │                       │
│  │  {                                     │                       │
│  │    "backend_store_uri":                │                       │
│  │    "postgresql://user:pass@rds:5432"   │                       │
│  │  }                                     │                       │
│  └────────────┬─────────────────────────┘  │                       │
│               │                             │                       │
│  ┌────────────▼────────────────────────────┐│                       │
│  │        RDS PostgreSQL                   ││                       │
│  │  (db.t4g.micro, 20GB gp3)              ││                       │
│  │                                         ││                       │
│  │  Database: mlflow                       ││                       │
│  │  ├── metric_events (métricas)          ││                       │
│  │  ├── params (parâmetros)               ││                       │
│  │  ├── tags (tags)                       ││                       │
│  │  ├── runs (metadados das runs)         ││                       │
│  │  ├── experiments (experimentos)        ││                       │
│  │  └── ... (outras tabelas)              ││                       │
│  │                                         ││                       │
│  │  ◄─── Backend Store (Metadata)         ││                       │
│  └────────────┬─────────────────────────┘│                       │
│               │                           │                       │
│  ┌────────────▼──────────────────────────┐│                       │
│  │  S3 Bucket (Artifacts)                 ││                       │
│  │  datathon-bandit-data-<account>/      ││                       │
│  │  ├── mlflow-artifacts/                 ││                       │
│  │  │   ├── 1/run-id/artifacts/          ││                       │
│  │  │   │   └── ... (notebooks artifacts) ││                       │
│  │  │   ├── 2/run-id/artifacts/          ││                       │
│  │  │   │   └── client_context.json      ││                       │
│  │  │   └── ...                           ││                       │
│  │  └── (outros dados)                    ││                       │
│  │                                         ││                       │
│  │  ◄─── Default Artifact Root            ││                       │
│  └────────────┬──────────────────────────┘│                       │
│               │                           │                       │
│  ┌────────────▼──────────────────────────┐│                       │
│  │  DynamoDB Tables                       ││                       │
│  │  ├── datathon-bandit-bandit-arms      ││                       │
│  │  │   └── Histórico de estatísticas    ││                       │
│  │  └── datathon-bandit-bandit-decisions ││                       │
│  │      └── Log de decisões (FastAPI)    ││                       │
│  │                                        ││                       │
│  │  ◄─── Usado apenas pela API           ││                       │
│  └────────────────────────────────────────┘│                       │
│                                            │                       │
│  ┌──────────────────────────────────────────┤                       │
│  │  CloudWatch Logs                         │                       │
│  │  ├── /ecs/datathon-bandit-fastapi       │                       │
│  │  └── /ecs/datathon-bandit-mlflow        │                       │
│  │                                          │                       │
│  │  ◄─── Logs de ambos serviços            │                       │
│  └──────────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

**O que é armazenado:**
- ✅ **RDS PostgreSQL** — Metadata do MLflow (runs, experiments, parâmetros, métricas)
- ✅ **S3** — Artifacts (arquivos, CSVs, gráficos, JSONs)
- ✅ **CloudWatch** — Logs dos serviços
- ✅ **DynamoDB** — Dados específicos da API (decisões, arms)
- ✅ **Secrets Manager** — Credenciais de banco de dados

---

## 📋 O que cada componente consome/produz

### 🔵 MLflow Server (em ambos os ambientes)

**Consome (Lê):**
- Backend Store (metadata) — `mlflow.db` (local) ou RDS (AWS)
- Artefatos antigos — S3 (AWS) ou `mlruns/` (local)

**Produz (Escreve):**
- Experiments criados
- Runs registradas
- Parâmetros, métricas, tags
- Artifacts (arquivos)

**Acesso via:**
- UI na porta 5000
- API REST do MLflow

### 🔴 FastAPI (Aplicação)

**Consome (Lê):**
- MLflow para registrar runs (tracking URI)
- DynamoDB para carregar estado do bandit
- S3 para carregar `arm_stats.csv` (warm start)

**Produz (Escreve):**
- Runs no MLflow (recomendações + feedback)
- Decisões no DynamoDB
- Logs no CloudWatch

**Endpoints:**
- `/recomendar` → Cria run no MLflow
- `/feedback` → Log da recompensa (conversão)
- `/stats` → Retorna estatísticas

### 📚 Notebooks (Treinamento)

**Consome (Lê):**
- `bank-term-deposit-subscription_processed/` (CSV processado)

**Produz (Escreve):**
- Runs de treinamento no MLflow (Experiment ID: 1)
- `arm_stats.csv` (warm start do bandit)
- Artifacts (gráficos, relatórios)

---

## 🔍 Estrutura de Dados no S3 (AWS)

```
s3://datathon-bandit-data-<account-id>/
├── mlflow-artifacts/                    ◄─── MLFLOW_DEFAULT_ARTIFACT_ROOT
│   ├── 1/                               ◄─── Experiment ID (notebooks)
│   │   ├── <run-uuid-1>/
│   │   │   └── artifacts/
│   │   │       ├── bandit_results.csv
│   │   │       ├── conversao_e_distribuicao.png
│   │   │       └── ...
│   │   ├── <run-uuid-2>/
│   │   └── ...
│   │
│   ├── 2/                               ◄─── Experiment ID (app/API)
│   │   ├── <run-uuid-1>/                ◄─── Cada recomendação
│   │   │   └── artifacts/
│   │   │       └── client_context.json
│   │   ├── <run-uuid-2>/                ◄─── Cada feedback
│   │   └── ...
│   │
│   └── ...
│
└── (outros dados do projeto - se houver)
```

**O MLflow lê/escreve automaticamente** nessa estrutura.

---

## 🔐 Estrutura de Dados no DynamoDB (AWS - Apenas API)

### Tabela 1: `datathon-bandit-bandit-arms`

```json
{
  "arm": {"S": "cellular"},          // Chave de partição
  "timestamp": {"N": "1234567890"},  // Atributo
  "impressions": {"N": "150"},
  "conversions": {"N": "45"},
  "conversion_rate": {"N": "0.30"}
}
```

### Tabela 2: `datathon-bandit-bandit-decisions`

```json
{
  "decision_id": {"S": "uuid-xxx"},   // Chave de partição
  "timestamp": {"N": "1234567890"},
  "arm_selected": {"S": "cellular"},
  "reward_observed": {"NULL": true},  // Preenchido por /feedback
  "client_context": {"S": "..."}
}
```

**MLflow não acessa DynamoDB** — é específico da API para persistência do bandit.

---

## 🔄 Fluxo de dados completo

### Local (Desenvolvimento)

```
1. Notebooks (03, 04) rodam
   └─► Criam runs no MLflow (Experiment 1)
   └─► Salvam artifacts em mlruns/1/
   └─► Salvam metadata em mlflow.db
   └─► Produzem arm_stats.csv

2. Docker Compose inicia
   └─► MLflow carrega mlflow.db + mlruns/
   └─► FastAPI carrega arm_stats.csv
   └─► FastAPI se conecta ao MLflow

3. API recebe /recomendar
   └─► Consulta DynamoDB (ou arquivo local)
   └─► Log de run no MLflow (Experiment 2)
   └─► Retorna recomendação

4. API recebe /feedback
   └─► Atualiza DynamoDB
   └─► Log de feedback no MLflow
   └─► Bandit aprende
```

### AWS (Produção)

```
1. FastAPI na ECS recebe /recomendar
   └─► Consulta DynamoDB
   └─► Log de run no MLflow (via http://alb:5000)
   └─► MLflow escreve em RDS (metadata) + S3 (artifacts)
   └─► CloudWatch captura logs

2. FastAPI recebe /feedback
   └─► Atualiza DynamoDB
   └─► Log de feedback no MLflow
   └─► Bandit aprende

3. MLflow UI (http://alb:5000)
   └─► Lê de RDS (metadata)
   └─► Lê de S3 (artifacts)
   └─► Exibe no navegador
```

---

## 📊 Resumo: O que MLflow consome

| Item | Local | AWS |
|------|-------|-----|
| **Backend Store** | `mlflow.db` (SQLite local) | RDS PostgreSQL |
| **Artifact Root** | `mlruns/` (diretório local) | S3 bucket |
| **Metadata** | Experiments, Runs, Params, Metrics | Idem |
| **Artifacts** | CSVs, PNGs, JSONs, client_context | Idem |
| **Acessado por** | Notebooks + FastAPI (local) | FastAPI (AWS) + UI (browser) |
| **Experiment 1** | Notebooks de treinamento | (histórico, não ativo) |
| **Experiment 2** | Recomendações da API | Recomendações da API |

---

## ⚠️ Importante: Sincronização

**Problema em desenvolvimento:**

Se você rodar os notebooks **depois** de ligar o Docker Compose, haverá **duas instâncias do MLflow**:
- ❌ `notebooks/mlruns/1/` (notebooks usam SQLite em notebooks/)
- ✅ `mlruns/2/` (API usa docker compose)

**Solução:**
1. Remova `notebooks/mlruns/`
2. Configure notebooks para usar o **mesmo MLflow** da API (ou rode *antes* do Docker Compose)

**Para garantir sincronização:**
```bash
# Opção 1: Notebooks ANTES do Docker Compose
jupyter notebook notebooks/03_Baseline...
# ... rodam ...
docker compose -f deploy/docker-compose.yml up

# Opção 2: Usar o mesmo MLflow
# Editar notebooks para apontar para http://localhost:5002 (porta mapeada)
# ou aguardar até que docker compose esteja de pé
```

---

## 🔗 Referências

- MLflow Backend Store: https://mlflow.org/docs/latest/tracking/#backend-stores
- MLflow Artifact Store: https://mlflow.org/docs/latest/tracking/#artifact-stores
- SQLite vs PostgreSQL em MLflow: https://mlflow.org/docs/latest/tracking/#sqlalchemy-database-uri

