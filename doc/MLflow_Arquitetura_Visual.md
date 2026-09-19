# Arquitetura MLflow: Visão Completa

## 🏗️ Arquitetura Local (Docker Compose)

```
┌─────────────────────────────────────────────────────────────────────┐
│                      LAPTOP DO CIENTISTA                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────┐         ┌──────────────────────┐          │
│  │  Jupyter Notebook    │         │  Terminal / Scripts  │          │
│  │  (Etapa 3: Train)    │         │  (src/train.py)      │          │
│  │                      │         │  (src/evaluate.py)   │          │
│  │  • Carrega dados     │         │                      │          │
│  │  • Treina bandit     │         │  MLflow run . --     │          │
│  │  • Log no MLflow     │         │    entry-point train │          │
│  │  • Salva artifacts   │         │                      │          │
│  └──────────┬───────────┘         └──────────┬───────────┘          │
│             │                                 │                      │
│             └─────────────────┬───────────────┘                      │
│                               │                                       │
│                        ┌──────▼────────┐                             │
│                        │  SQLITE DB    │                             │
│                        │  (mlflow.db)  │                             │
│                        └──────┬────────┘                             │
│                               │                                       │
│                        ┌──────▼────────┐                             │
│                        │   mlruns/     │                             │
│                        │  (artifacts)  │                             │
│                        └───────────────┘                             │
│                                                                      │
│  ┌─────────────────────────────────────────────────────┐            │
│  │         docker compose up (Docker Compose)          │            │
│  │                                                     │            │
│  │  ┌─────────────────────┐  ┌──────────────────────┐ │            │
│  │  │  MLflow Container   │  │  FastAPI Container   │ │            │
│  │  │                     │  │                      │ │            │
│  │  │ • Backend: SQLite   │  │ • Port: 8000         │ │            │
│  │  │ • UI: 5002 (mapped) │  │ • Carrega modelo     │ │            │
│  │  │ • Artifacts: mlruns │  │ • /recomendar endpoint           │            │
│  │  └──────────┬──────────┘  └──────────┬───────────┘ │            │
│  │             │                        │             │            │
│  │  ┌──────────▼────────────────────────▼──────────┐  │            │
│  │  │      Docker Network (datathon_net)          │  │            │
│  │  │   FastAPI consegue acessar MLflow            │  │            │
│  │  │   MLFLOW_TRACKING_URI=http://mlflow:5000     │  │            │
│  │  └──────────────────────────────────────────────┘  │            │
│  │                                                     │            │
│  │  Volume compartilhado: ../mlruns                    │            │
│  │  (Notebooks e API veem mesmos artifacts)            │            │
│  │                                                     │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                      │
│  ┌─────────────────────────────────────────────────────┐            │
│  │           Browser Local                             │            │
│  ├─────────────────────────────────────────────────────┤            │
│  │  • http://localhost:5002  → MLflow UI               │            │
│  │    (ver experiments, runs, métricas, artifacts)     │            │
│  │                                                     │            │
│  │  • http://localhost:8000/docs → FastAPI Swagger    │            │
│  │    (testar /recomendar, /feedback)                 │            │
│  │                                                     │            │
│  │  • http://localhost:8000/health → Health check     │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

╔═════════════════════════════════════════════════════════════════════╗
║  FLUXO LOCAL:                                                       ║
║  1. Cientista roda notebook 03 → logs no SQLite                     ║
║  2. docker compose up → MLflow UI em 5002, API em 8000              ║
║  3. Acessa http://localhost:5002 → vê experimentos                  ║
║  4. Testa http://localhost:8000/recomendar → chama API              ║
║  5. API carrega modelo do MLflow via http://mlflow:5000             ║
╚═════════════════════════════════════════════════════════════════════╝
```

---

## ☁️ Arquitetura AWS (Terraform)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AWS (us-east-2)                                │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                        VPC Privada                                 │ │
│  │                                                                    │ │
│  │  ┌──────────────────────────────────────────────────────────────┐ │ │
│  │  │                  ECS Fargate Cluster                         │ │ │
│  │  │                                                              │ │ │
│  │  │  ┌─────────────────────┐  ┌──────────────────────────────┐ │ │ │
│  │  │  │  FastAPI Service    │  │   MLflow Server Service       │ │ │ │
│  │  │  │                     │  │                              │ │ │ │
│  │  │  │ • Port: 8000        │  │ • Port: 5000                 │ │ │ │
│  │  │  │ • Task: api-fastapi │  │ • Task: mlflow-server        │ │ │ │
│  │  │  │ • Replicas: 2-3     │  │ • Replicas: 1                │ │ │ │
│  │  │  │ • Carrega modelo    │  │ • Backend PostgreSQL         │ │ │ │
│  │  │  │   do Registry       │  │ • Artifacts em S3            │ │ │ │
│  │  │  │                     │  │                              │ │ │ │
│  │  │  └────────────┬────────┘  └────────────┬─────────────────┘ │ │ │
│  │  │               │                        │                    │ │ │
│  │  │      MLFLOW_TRACKING_URI=             MLFLOW_BACKEND_STORE │ │ │
│  │  │      http://mlflow.datathon...:5000   _URI=postgresql://.. │ │ │
│  │  │                                                              │ │ │
│  │  └──────────────────┬───────────────────┬───────────────────────┘ │ │
│  │                     │                   │                         │ │
│  │  ┌──────────────────▼───────────────────▼──────────────────────┐ │ │
│  │  │         Application Load Balancer (ALB)                     │ │ │
│  │  │                                                              │ │ │
│  │  │  • http://datathon-alb-xxx.us-east-2.elb.amazonaws.com    │ │ │
│  │  │    :80 → FastAPI (8000)                                    │ │ │
│  │  │    :5000 → MLflow (5000)                                   │ │ │
│  │  │                                                              │ │ │
│  │  │  • Health checks automáticos                                │ │ │
│  │  │  • Auto-scaling baseado em CPU/memória                      │ │ │
│  │  └──────────────────┬──────────────────────────────────────────┘ │ │
│  │                     │                                            │ │
│  └─────────────────────┼────────────────────────────────────────────┘ │
│                        │                                               │
│  ┌─────────────────────▼───────────────────────────────────────────┐ │
│  │              Armazenamento de Dados (Não em ECS)                │ │
│  │                                                                   │ │
│  │  ┌──────────────────────┐  ┌──────────────────────────────────┐ │ │
│  │  │  RDS PostgreSQL      │  │   DynamoDB                       │ │ │
│  │  │  (Aurora Multi-AZ)   │  │   (Bandit State)                 │ │ │
│  │  │                      │  │                                  │ │ │
│  │  │ • Backend MLflow     │  │ • Tabela: bandit-arms           │ │ │
│  │  │ • Metadata runs      │  │ • Tabela: bandit-decisions      │ │ │
│  │  │ • Params, metrics    │  │ • Key: decision_id              │ │ │
│  │  │ • User/models        │  │ • Valor: recomendação + outcome │ │ │
│  │  │                      │  │ • Suporta horizontal scaling     │ │ │
│  │  │ • Credenciais em     │  │                                  │ │ │
│  │  │   Secrets Manager    │  │                                  │ │ │
│  │  └──────────────────────┘  └──────────────────────────────────┘ │ │
│  │                                                                   │ │
│  │  ┌────────────────────────────────────────────────────────────┐ │ │
│  │  │  S3 (Artefatos MLflow)                                     │ │ │
│  │  │                                                            │ │ │
│  │  │  • s3://mlflow-artifacts-{account-id}/mlruns              │ │ │
│  │  │  │                                                        │ │ │
│  │  │  ├─ {experiment-id}/                                      │ │ │
│  │  │  │  └─ {run-id}/                                          │ │ │
│  │  │  │     ├─ artifacts/bandit_model.pkl                      │ │ │
│  │  │  │     ├─ artifacts/bandit_results.csv                    │ │ │
│  │  │  │     ├─ artifacts/config.json                           │ │ │
│  │  │  │     └─ artifacts/RELATORIO.md                          │ │ │
│  │  │  │                                                        │ │ │
│  │  │  └─ (organizado por data/experimento)                     │ │ │
│  │  │                                                            │ │ │
│  │  │  • Acesso via IAM roles (ECS task role)                   │ │ │
│  │  │  • Versionamento de modelos rastreado em RDS             │ │ │
│  │  └────────────────────────────────────────────────────────────┘ │ │
│  │                                                                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │           Logging e Monitoramento                                │ │
│  │                                                                   │ │
│  │  ┌─────────────────────────┐  ┌──────────────────────────────┐ │ │
│  │  │  CloudWatch Logs        │  │  CloudWatch Metrics          │ │ │
│  │  │                         │  │                              │ │ │
│  │  │ • /ecs/fastapi          │  │ • ECS CPU/Memory usage       │ │ │
│  │  │ • /ecs/mlflow           │  │ • RDS connections           │ │ │
│  │  │ • /mlflow               │  │ • DynamoDB requests         │ │ │
│  │  │ • /api                  │  │ • S3 operations             │ │ │
│  │  │                         │  │                              │ │ │
│  │  │ Auditoria completa:     │  │ Alertas automáticos:         │ │ │
│  │  │ • Quem fez o quê        │  │ • CPU > 80% → Scale up      │ │ │
│  │  │ • Quando (timestamps)   │  │ • Erro rate > 5% → Notify   │ │ │
│  │  │ • Detalhes de cada call │  │ • Latência > 1s → Investigate           │ │
│  │  │                         │  │                              │ │ │
│  │  └─────────────────────────┘  └──────────────────────────────┘ │ │
│  │                                                                   │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                  ECR (Imagens Docker)                            │ │
│  │                                                                   │ │
│  │  • {account-id}.dkr.ecr.us-east-2.amazonaws.com/                │ │
│  │    ├─ datathon-fastapi:latest (API)                             │ │
│  │    └─ datathon-mlflow:latest (MLflow Server)                    │ │
│  │                                                                   │ │
│  │  • Builded localmente, pushed via CI/CD                          │ │
│  │  • ECS pull mais recente no startup                             │ │
│  │                                                                   │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════╗
║  FLUXO AWS:                                                               ║
║  1. Cientista faz git push → GitHub                                       ║
║  2. CI/CD Pipeline (opcional GitHub Actions):                             ║
║     ├─ Build imagens Docker (fastapi, mlflow)                            ║
║     ├─ Push para ECR                                                      ║
║     ├─ Roda ECS Task: src/train.py                                        ║
║     ├─ Log para RDS (backend) + S3 (artifacts)                            ║
║     └─ Atualiza MLflow UI                                                 ║
║  3. ECS atualiza serviços (rolling update)                                ║
║  4. ALB roteia para novo FastAPI                                          ║
║  5. API começa a servir com novo modelo                                   ║
║  6. Feedback registrado em DynamoDB + MLflow                              ║
║  7. CloudWatch monitora tudo                                              ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## 🔄 Fluxo Completo: Do Notebook ao Production

```
┌───────────────────────────────────────────────────────────────────────────┐
│  FASE 1: ENRIQUECIMENTO TRACKING (Notebook 03)                          │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Cientista                        MLflow Local                            │
│  ┌──────────────────────┐        ┌──────────────────┐                    │
│  │ Notebook 03          │        │  sqlite:///      │                    │
│  │                      │───────▶│  mlflow.db       │                    │
│  │ mlflow.log_param()   │        │                  │                    │
│  │ mlflow.log_metric()  │        │  Experiments:    │                    │
│  │ mlflow.log_artifact()│        │  datathon-       │                    │
│  │ mlflow.log_figure()  │        │  bandit-canal    │                    │
│  │                      │        │                  │                    │
│  └──────────────────────┘        └────────┬─────────┘                    │
│                                           │                              │
│                                      MLflow UI                           │
│                                    (localhost:5002)                      │
│                                    ├─ Tags: stage=training               │
│                                    ├─ Params: seed=42                    │
│                                    ├─ Metrics: thompson_conversion       │
│                                    └─ Artifacts: gráficos, CSV           │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  FASE 2: VALIDAÇÃO E REGISTRO (Notebook 04 + Model Registry)            │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Notebook 04              Golden Set Validation      Model Registry       │
│  ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────────┐ │
│  │ Carrega run_id   │    │ 5 casos de teste│    │ MLflow Registry     │ │
│  │ da run anterior  │───▶│ • age_segment   │───▶│ (SQLite)            │ │
│  │                  │    │ • poutcome      │    │                     │ │
│  │ Valida em Golden │    │ • previous      │    │ datathon-bandit-    │ │
│  │ Set (8+ casos)   │    │                 │    │ thompson            │ │
│  │                  │    │ Validation rate │    │ ├─ Version 1        │ │
│  │ Se > 80% OK:     │    │ > 80% ✅        │    │ │  Stage: Staging   │ │
│  │ ├─ Cria wrapper  │    └─────────────────┘    │ └─ Production ready │ │
│  │ ├─ Registra como │                           │                     │ │
│  │ │ MLflow Model   │                           │ (após aprovação)    │ │
│  │ └─ Move para     │                           │ ├─ Version 1        │ │
│  │   Production     │                           │ │  Stage: Production│ │
│  │                  │                           │ └─ Em uso agora!    │ │
│  └──────────────────┘                           └─────────────────────┘ │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  FASE 3: REPRODUZIBILIDADE (MLflow Projects)                            │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  src/train.py                 src/evaluate.py           MLproject         │
│  ┌──────────────────┐        ┌──────────────────┐    ┌──────────────────┐ │
│  │ Script Python    │        │ Script Python    │    │ entry_points:    │ │
│  │ (notebook 03)    │───┐    │ (notebook 04)    │──┐ │ ├─ prepare_data  │ │
│  │                  │   │    │                  │  │ │ ├─ train         │ │
│  │ Reproduzível:    │   │    │ Golden Set check │  │ │ ├─ evaluate      │ │
│  │ • Args via CLI   │   │    │ Model Registry   │  │ │ └─ serve         │ │
│  │ • Log no MLflow  │   │    │                  │  │ └──────────────────┘ │
│  │ • Mesmos dados   │   │    └──────────────────┘  │                      │
│  │                  │   │                          │  mlflow run . \      │
│  └──────────────────┘   │                          │    --entry-point train
│                         └──────────┬───────────────┘                      │
│                                    │                                      │
│                        Roda com diferentes seeds:                         │
│                        mlflow run . -P seed=42                            │
│                        mlflow run . -P seed=123                           │
│                        mlflow run . -P seed=456                           │
│                                    │                                      │
│                        Cada run logado no MLflow                          │
│                        (pode comparar lado a lado!)                       │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  FASE 4: INTEGRAÇÃO NA API (Local + Docker Compose)                     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  app/main.py             MLflow Server         Model Registry             │
│  ┌─────────────────┐    ┌────────────────┐    ┌──────────────────────┐   │
│  │ FastAPI         │    │ SQLite         │    │ datathon-bandit-     │   │
│  │                 │    │                │    │ thompson             │   │
│  │ Startup:        │    │ Experimento 1: │    │ ├─ Versão 1 (Staging)    │   │
│  │ ├─ Load model   │    │ Treinamentos   │    │ │  (teste)               │   │
│  │ │ do Registry   │───▶│                │    │ │                        │   │
│  │ ├─ models:/..   │    │ Experimento 2: │    │ └─ Versão 1 (Production) │   │
│  │ │ /Production   │    │ Serving        │    │    ✅ Em uso agora!      │   │
│  │ │               │    │                │    │                         │   │
│  │ POST /recomendar│   │ Rastreia tudo: │    └──────────────────────┘   │
│  │ ├─ Input:       │   │ • Predições    │                               │
│  │ │ age_segment   │   │ • Feedbacks    │                               │
│  │ │ poutcome      │   │ • Métricas     │                               │
│  │ │ previous      │   │                │                               │
│  │ │               │   └────────────────┘                               │
│  │ ├─ Load modelo  │                                                    │
│  │ ├─ Predição     │  docker compose up:                                │
│  │ ├─ Log outcome  │  ├─ MLflow em 5002 (localhost:5002)                │
│  │ └─ Return canal │  ├─ FastAPI em 8000 (localhost:8000)               │
│  │                 │  └─ Compartilham Docker network                    │
│  │ POST /feedback  │                                                    │
│  │ └─ Registra     │  Testes:                                           │
│  │   outcome       │  curl http://localhost:8000/docs                   │
│  │   no MLflow     │  curl http://localhost:5002                        │
│  │                 │                                                     │
│  └─────────────────┘                                                    │
│                                                                            │
│  MLFLOW_TRACKING_URI=http://mlflow:5000 (dentro da Docker network)       │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│  FASE 5: DEPLOY NA AWS (Terraform + ECS + RDS + S3)                    │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  GitHub Push          CI/CD Pipeline        AWS (us-east-2)              │
│  ┌────────────┐       ┌────────────────┐   ┌──────────────────────────┐  │
│  │ git push   │       │ GitHub Actions │   │ ECS Fargate (Imagens)    │  │
│  │ main branch│──────▶│                │──▶│                          │  │
│  │            │       │ • Build imagem │   │ FastAPI Container        │  │
│  │ Trigger:   │       │ • Push ECR     │   │ ├─ Port 8000             │  │
│  │ • On push  │       │ • Run training │   │ ├─ load model from       │  │
│  │ • Schedule │       │ • Deploy ECS   │   │ │  models:/Production    │  │
│  │ • Manual   │       │                │   │ └─ MLFLOW_TRACKING_URI=  │  │
│  │            │       └────────────────┘   │    http://mlflow:5000    │  │
│  └────────────┘                           │                          │  │
│                                           │ MLflow Container         │  │
│                                           │ ├─ Port 5000             │  │
│                                           │ ├─ Backend: RDS Postgres │  │
│                                           │ └─ Artifacts: S3         │  │
│                                           │                          │  │
│                                           │ ALB                      │  │
│                                           │ ├─ http://alb:80 → API   │  │
│                                           │ └─ http://alb:5000 → ML  │  │
│                                           │                          │  │
│    ┌──────────────────────────────────┬──▶│ RDS PostgreSQL           │  │
│    │                                  │   │ ├─ Backend MLflow        │  │
│    │                                  │   │ ├─ Runs, params, metrics │  │
│    │                                  │   │ └─ Model Registry        │  │
│    │                                  │   │                          │  │
│    │                                  │   │ S3                       │  │
│    │                                  │   │ └─ mlruns/artifacts      │  │
│    │                                  │   │                          │  │
│    │                                  │   │ DynamoDB                 │  │
│    │                                  │   │ └─ bandit state          │  │
│    │                                  │   │                          │  │
│    │                                  │   │ CloudWatch               │  │
│    │                                  │   │ ├─ Logs (ECS, MLflow)    │  │
│    │                                  │   │ ├─ Metrics (CPU, mem)    │  │
│    │                                  │   │ └─ Alertas automáticos   │  │
│    │                                  │   └──────────────────────────┘  │
│    │                                  │                                   │
│    │      ECR (Imagens Docker)        │                                   │
│    │      ├─ datathon-fastapi:latest  │                                   │
│    │      └─ datathon-mlflow:latest   │                                   │
│    └──────────────────────────────────┘                                   │
│                                                                            │
│  API em Produção:                                                         │
│  • Carrega automaticamente modelo Production do MLflow                    │
│  • Registra predictions e feedbacks em RDS + S3                          │
│  • Monitora latência/erros em CloudWatch                                  │
│  • Auto-scaling baseado em CPU                                            │
│  • Rollback automático se health check falhar                             │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Estado do Modelo no MLflow Registry

```
PIPELINE LOCAL (Fase 1-4):
├─ Staging (teste/validação)
│  └─ Model Version 1
│     ├─ Status: pronto para production
│     ├─ Performance: 13.67% conversão
│     ├─ Run ID: abc123def456
│     └─ Created: 2026-09-25
│
└─ Production (em uso)
   └─ Model Version 1
      ├─ Status: em uso na API
      ├─ API carrega: models:/datathon-bandit-thompson/Production
      ├─ Uptime: 99.9%
      └─ Feedback coletado: 1,247 conversões


PIPELINE AWS (Fase 5):
├─ Staging (validação em ECS)
│  └─ Model Version 2
│     ├─ Status: aguardando aprovação
│     ├─ Performance: 13.85% conversão (+0.18pp)
│     ├─ Training date: 2026-09-30
│     └─ Data version: 2026-Q4
│
├─ Production (em uso na AWS)
│  ├─ Model Version 1
│  │  └─ Status: legacy
│  │
│  └─ Model Version 2
│     ├─ Status: em uso na API ECS
│     ├─ Replicas: 3
│     ├─ Latência avg: 45ms
│     ├─ Requests/min: 1,200
│     └─ Uptime: 99.99%
│
└─ Archived (histórico)
   ├─ Model Version 0 (primeira versão)
   └─ Model Version 1 (substituída)


RETREINO AUTOMÁTICO:
• GitHub Actions roda toda segunda às 2 AM
• src/train.py com dados novos
• Log automático no RDS + S3
• Comparação com Production
• Se lift > 1%, move Staging → Production
• Senão, fica em Staging para análise
```

---

## 🎯 Resumo da Jornada

```
LOCAL                          AWS                        RESULTADO
┌──────────────┐       ┌─────────────────────┐      ┌────────────────┐
│ Notebook 03  │       │ ECS Fargate          │      │ Production     │
│              │───┬──▶│ ├─ FastAPI          │      │ Ready System   │
│ Treina       │   │   │ └─ MLflow Server    │      │ ✅ Rastreado   │
│ Thompson     │   │   │                     │      │ ✅ Versionado  │
│              │   │   │ RDS PostgreSQL      │      │ ✅ Monitorado  │
│ Log MLflow   │   │   │ ├─ Metadata         │      │ ✅ Reproduzível│
│              │   │   │ └─ Model Registry   │      │ ✅ Auto-deploy │
│              │   │   │                     │      │ ✅ Scalável    │
│ Valida       │   │   │ S3                  │      │                │
│ Notebook 04  │───┘   │ └─ Artifacts        │      │ Total MLOps    │
│              │       │                     │      │ Maturity: HIGH │
│ Deploya      │       │ DynamoDB            │      │                │
│ API Docker   │       │ └─ Bandit State     │      └────────────────┘
│              │       │                     │
│ Visualiza    │       │ CloudWatch          │
│ UI MLflow    │       │ ├─ Logs             │
│              │       │ ├─ Metrics          │
└──────────────┘       │ └─ Alertas          │
                       └─────────────────────┘
```

