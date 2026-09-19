# MLflow: Jornada Completa do ML no Datathon
## Da Experimentação em Notebooks até Production (Local ou AWS)

---

## 🎯 Visão Geral: Duas Rotas Possíveis

```
FASE 1-4: IGUAL PARA TODOS (Local com Docker Compose)
┌──────────────────────────────────────────────────────────────┐
│ Notebooks (Tracking) → Scripts (Reproducible) → API (Docker) │
│ Trabalhar localmente, testar tudo, validar modelo            │
└──────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        │                                       │
   ROTA A: LOCAL                         ROTA B: AWS
  (Docker Compose)                   (ECS + RDS + S3)
        │                                       │
   ┌────▼──────────────┐              ┌────────▼──────────────┐
   │ FASE 5: LOCAL   │              │ FASE 5: AWS        │
   │ ✅ Simples        │              │ ✅ Escalável         │
   │ ✅ Gratuito       │              │ ✅ Profissional      │
   │ ✅ Rápido         │              │ ✅ Auto-escalável    │
   │ ✅ Desenvolvimento│              │ ✅ Monitored         │
   │                   │              │ ✅ Multi-replica     │
   │ docker-compose.yml│              │ Terraform + CI/CD    │
   └───────────────────┘              └──────────────────────┘
```

---

## 📊 Qual Rota Escolher?

| Critério | Local (Docker Compose) | AWS (ECS + RDS + S3) |
|----------|---|---|
| **Custo** | Grátis (laptop/servidor local) | ~$100-200/mês |
| **Setup** | 5 minutos | 30 minutos (primeira vez) |
| **Scaling** | Não automático | Auto-escalável |
| **Uptime** | Enquanto máquina está ligada | 99.9% SLA |
| **Melhor para** | Dev/Test/Demo | Produção real |
| **Monitoramento** | Logs locais | CloudWatch automático |
| **CI/CD** | Manual | GitHub Actions automático |
| **Multi-replica** | Não | Sim (3+ instâncias) |

**Recomendação:**
- **Fases 1-4:** Todos fazem localmente com Docker Compose
- **Fase 5:** Escolha sua rota
  - 📍 **Fazer demo/hackathon?** → Fica em Docker Compose
  - 🚀 **Ir para produção?** → Vai para AWS

---

# FASES 1-4: IGUAL PARA TODOS (Local com Docker)

---

# FASE 1: Enriquecer Tracking nos Notebooks

## Objetivo
Fazer o notebook 03 logar **tudo** no MLflow com SQLite local.

### 1. Aumentar Tags (Categorização)

```python
# notebook/03_Baseline_e_Thompson.ipynb

import mlflow

mlflow.set_tracking_uri('sqlite:///../../mlflow.db')
mlflow.set_experiment('datathon-bandit-canal')

with mlflow.start_run(run_name='etapa3_seed42_v2'):
    
    # ===== TAGS (para filtrar e organizar) =====
    mlflow.set_tag('stage', 'training')
    mlflow.set_tag('etapa_datathon', '3')
    mlflow.set_tag('dataset', 'bank-term-deposit')
    mlflow.set_tag('algoritmo', 'thompson_sampling')
    mlflow.set_tag('producao_ready', 'false')
    mlflow.set_tag('autor', 'grupo-04')
    mlflow.set_tag('notas', 'seed 42, prior_weight=20')
```

### 2. Enriquecer Parâmetros

```python
    # ===== PARÂMETROS =====
    mlflow.log_param('seed', 42)
    mlflow.log_param('test_size', 0.30)
    mlflow.log_param('train_rows', len(train_df))
    mlflow.log_param('test_rows', len(test_df))
    mlflow.log_param('algoritmo', 'MABWiser ThompsonSampling')
    mlflow.log_param('prior_weight_contextual', 20.0)
```

### 3. Métricas Detalhadas

```python
    # ===== MÉTRICAS BÁSICAS =====
    mlflow.log_metric('thompson_conversion_final', metrics['thompson_conversion'])
    mlflow.log_metric('baseline_conversion_final', metrics['baseline_conversion'])
    mlflow.log_metric('lift_relativo_pct', metrics['conversion_lift_relative'] * 100)
    
    # ===== MÉTRICAS COM HISTÓRICO =====
    for round_num in range(len(results)):
        mlflow.log_metric('thompson_conversion_rolling', 
                         results['thompson_cumulative_conversion'].iloc[round_num],
                         step=round_num)
        mlflow.log_metric('cumulative_regret',
                         float(results['cumulative_regret'].iloc[round_num]),
                         step=round_num)
    
    # ===== MÉTRICAS POR SEGMENTO =====
    for segment in ['jovem', 'adulto', 'senior']:
        subset = results[results['age_segment'] == segment]
        mlflow.log_metric(f'thompson_conversion_segment_{segment}', 
                         float(subset['thompson_reward'].mean()))
```

### 4. Gráficos

```python
    # ===== GRÁFICOS =====
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    results[['thompson_cumulative_conversion', 'baseline_cumulative_conversion']].plot(ax=axes[0,0])
    axes[0,0].set_title('Conversão Acumulada')
    
    results['thompson_arm'].value_counts().plot.bar(ax=axes[0,1])
    axes[0,1].set_title('Escolhas do Thompson')
    
    results['cumulative_regret'].plot(ax=axes[1,0], color='red')
    axes[1,0].set_title('Regret Acumulado')
    
    results.groupby('age_segment')['thompson_reward'].mean().plot.bar(ax=axes[1,1])
    axes[1,1].set_title('Performance por Segmento')
    
    plt.tight_layout()
    mlflow.log_figure(fig, 'dashboard_completo.png')
```

### 5. Artefatos

```python
    # ===== ARTEFATOS =====
    results.to_csv('bandit_results.csv', index=False)
    mlflow.log_artifact('bandit_results.csv')
    
    import pickle
    with open('bandit_model.pkl', 'wb') as f:
        pickle.dump(bandit, f)
    mlflow.log_artifact('bandit_model.pkl')
    
    config = {
        'dataset': 'bank-term-deposit',
        'resultados': {
            'thompson_conversion': float(metrics['thompson_conversion']),
            'baseline_conversion': float(metrics['baseline_conversion']),
            'lift_relativo': float(metrics['conversion_lift_relative'])
        }
    }
    mlflow.log_dict(config, 'config.json')
```

### Visualizar Localmente

```bash
# Terminal
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

# Browser
# http://localhost:5000
```

---

# FASE 2: Validação e Model Registry

## Notebook 04: Golden Set + Registrar Modelo

```python
# notebook/04_Avaliacao_e_Golden_Set.ipynb

import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri('sqlite:///../../mlflow.db')

# Validar Golden Set
with mlflow.start_run(run_name='etapa4_golden_set_validation'):
    mlflow.set_tag('stage', 'validation')
    
    # ... validar modelo ...
    
    validation_score = passed / len(golden_set)
    mlflow.log_metric('golden_set_pass_rate', validation_score)
    
    if validation_score > 0.8:
        # ===== REGISTRAR MODELO =====
        class BanditModelWrapper(mlflow.pyfunc.PythonModel):
            def load_context(self, context):
                self.mab = pickle.load(open(context.artifacts['bandit_model'], 'rb'))
            
            def predict(self, context, model_input):
                decisions = []
                for _, row in model_input.iterrows():
                    arm = self.mab.predict()
                    decisions.append(arm)
                return pd.DataFrame({'recommended_channel': decisions})
        
        mlflow.pyfunc.log_model(
            python_model=BanditModelWrapper(),
            artifact_path='bandit-model',
            artifacts={
                'bandit_model': '../data/processed/.../bandit_model.pkl',
                'context_rates': '../data/processed/.../context_rates.csv'
            },
            registered_model_name='datathon-bandit-thompson'
        )
        
        print('✅ Modelo registrado (Staging)')

# Promover para Production
client = MlflowClient(tracking_uri='sqlite:///../../mlflow.db')
staging_versions = client.get_latest_versions('datathon-bandit-thompson', stages=['Staging'])

if staging_versions:
    latest = staging_versions[0]
    client.transition_model_version_stage(
        name='datathon-bandit-thompson',
        version=latest.version,
        stage='Production'
    )
    print(f'✅ Modelo movido para Production (v{latest.version})')
```

---

# FASE 3: Scripts Reproduzíveis

## Converter Notebooks em Scripts

### src/train.py

```python
# src/train.py

import argparse
import mlflow
import pickle
import pandas as pd
import numpy as np
from mabwiser.mab import MAB, LearningPolicy
from sklearn.model_selection import train_test_split

def main(test_size=0.30, seed=42, tracking_uri='sqlite:///mlflow.db'):
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment('datathon-bandit-canal')
    
    df = pd.read_csv('data/processed/bank-term-deposit-subscription_eda/bank_full_tratado.csv')
    
    with mlflow.start_run(run_name=f'train_seed_{seed}'):
        mlflow.set_tag('stage', 'training')
        mlflow.set_tag('script', 'src/train.py')
        
        mlflow.log_param('seed', seed)
        mlflow.log_param('test_size', test_size)
        
        # Treinar
        df['age_segment'] = pd.cut(df['age'], bins=[0, 30, 50, 100], 
                                   labels=['jovem', 'adulto', 'senior'])
        train_df, test_df = train_test_split(df, test_size=test_size, 
                                            random_state=seed, stratify=df['y'])
        
        mab = MAB(arms=['cellular', 'telephone'], 
                 learning_policy=LearningPolicy.ThompsonSampling())
        mab.fit(train_df['contact'].to_numpy(), train_df['y'].to_numpy())
        
        # Simular teste
        results = []
        rng = np.random.default_rng(seed)
        for _, row in test_df.iterrows():
            arm = mab.predict()
            outcome = int(rng.random() < row['y'])
            mab.partial_fit(np.array([arm]), np.array([outcome]))
            results.append({'arm': arm, 'outcome': outcome})
        
        results_df = pd.DataFrame(results)
        conv = results_df['outcome'].mean()
        
        mlflow.log_metric('thompson_conversion', conv)
        
        results_df.to_csv('bandit_results.csv', index=False)
        mlflow.log_artifact('bandit_results.csv')
        
        with open('bandit_model.pkl', 'wb') as f:
            pickle.dump(mab, f)
        mlflow.log_artifact('bandit_model.pkl')
        
        print(f'✅ Treinamento: {conv:.2%} conversão')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-size', type=float, default=0.30)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--tracking-uri', default='sqlite:///mlflow.db')
    args = parser.parse_args()
    main(args.test_size, args.seed, args.tracking_uri)
```

### MLproject (na raiz)

```yaml
# MLproject

name: datathon-bandit

python_env: python_env.yaml

entry_points:
  
  train:
    parameters:
      test_size: {type: float, default: 0.30}
      seed: {type: int, default: 42}
    command: "python src/train.py --test-size {test_size} --seed {seed}"
  
  evaluate:
    command: "python src/evaluate.py"
```

### Executar

```bash
# Local
mlflow run . --entry-point train -P seed=123

# Múltiplas seeds (comparar)
mlflow run . --entry-point train -P seed=42
mlflow run . --entry-point train -P seed=123
mlflow run . --entry-point train -P seed=456
```

---

# FASE 4: API + MLflow (Igual em Ambas Rotas)

## app/main.py (Atualizado para Carregar do Registry)

```python
# app/main.py

import os
from contextlib import asynccontextmanager
import pandas as pd
import mlflow.pyfunc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI', 'sqlite:///mlflow.db')
MODEL_NAME = 'datathon-bandit-thompson'
MODEL_STAGE = os.getenv('MODEL_STAGE', 'Production')

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: carregar modelo
    global model
    try:
        model_uri = f'models:/{MODEL_NAME}/{MODEL_STAGE}'
        model = mlflow.pyfunc.load_model(model_uri)
        print(f'✅ Modelo carregado: {model_uri}')
    except Exception as e:
        print(f'❌ Erro carregando modelo: {e}')
        raise
    
    yield  # API roda
    print('API encerrada')

app = FastAPI(lifespan=lifespan)

class RecommendRequest(BaseModel):
    age_segment: str
    poutcome: str
    previous: int

@app.get('/health')
def health():
    return {'status': 'ok', 'model_loaded': model is not None}

@app.post('/recomendar')
def recomendar(req: RecommendRequest):
    if model is None:
        raise HTTPException(status_code=503, detail='Modelo não carregado')
    
    input_df = pd.DataFrame({
        'age_segment': [req.age_segment],
        'poutcome': [req.poutcome],
        'previous': [req.previous]
    })
    
    try:
        prediction = model.predict(input_df)
        recommended_channel = prediction['recommended_channel'][0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro: {str(e)}')
    
    # Log decision
    with mlflow.start_run(run_name='prediction'):
        mlflow.set_tag('stage', 'serving')
        mlflow.log_param('predicted_channel', recommended_channel)
        run_id = mlflow.active_run().info.run_id
    
    return {'channel': recommended_channel, 'run_id': run_id}

@app.post('/feedback')
def feedback(decision_id: str, outcome: bool):
    with mlflow.start_run(run_id=decision_id):
        mlflow.log_metric('outcome', int(outcome))
    return {'status': 'recorded'}
```

### Docker Compose (para ambas rotas)

```yaml
# deploy/docker-compose.yml

version: '3.8'

services:
  mlflow:
    build:
      context: ..
      dockerfile: deploy/Dockerfile.mlflow
    container_name: datathon_mlflow
    volumes:
      - mlflow-db-volume:/app/data
      - ../mlruns:/app/mlruns
      - ..:/app:cached
    ports:
      - "5002:5000"
    environment:
      - MLFLOW_BACKEND_STORE_URI=sqlite:////app/data/mlflow.db
      - MLFLOW_DEFAULT_ARTIFACT_ROOT=/app/mlruns
    networks:
      - datathon_net
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://127.0.0.1:5000/ || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: unless-stopped

  fastapi:
    build:
      context: ..
      dockerfile: deploy/Dockerfile.fastapi
    container_name: datathon_fastapi
    depends_on:
      mlflow:
        condition: service_healthy
    volumes:
      - ../mlruns:/app/mlruns
      - ..:/app:cached
    ports:
      - "8000:8000"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - MODEL_STAGE=Production
    networks:
      - datathon_net
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

networks:
  datathon_net:

volumes:
  mlflow-db-volume:
```

### Testar Localmente

```bash
# Subir
docker compose -f deploy/docker-compose.yml up -d

# Testar API
curl -X POST http://localhost:8000/recomendar \
  -H "Content-Type: application/json" \
  -d '{"age_segment": "jovem", "poutcome": "success", "previous": 1}'

# Visualizar MLflow
# http://localhost:5002

# Logs
docker compose -f deploy/docker-compose.yml logs -f fastapi
docker compose -f deploy/docker-compose.yml logs -f mlflow

# Parar
docker compose -f deploy/docker-compose.yml down
```

---

# FASE 5: Escolha Sua Rota

---

# 🏠 ROTA A: Continuar em Docker Compose Local

## Objetivo
Manter infraestrutura simples, local, sem custo.

### Vantagens
- ✅ Nenhum custo de cloud
- ✅ Setup instantâneo
- ✅ Não precisa conta AWS
- ✅ Perfeito para demo/hackathon
- ✅ Tudo em um arquivo docker-compose.yml

### Implementação (Já Pronta!)

```bash
# Tudo que você precisa fazer:

# 1. Treinar com scripts
mlflow run . --entry-point train -P seed=42

# 2. Validar e promover no MLflow UI
# http://localhost:5002 → Marcar como Production

# 3. Subir API + MLflow
docker compose -f deploy/docker-compose.yml up -d

# 4. Testar
curl http://localhost:8000/docs
curl http://localhost:5002  # MLflow UI

# 5. Para subir em servidor linux:
# Copie tudo para servidor
# Rode docker compose up -d
# Acesse via IP do servidor
```

### Estrutura Local Final

```
datathon-8mlet-grupo-04/
├── mlflow.db                    ← Backend MLflow (SQLite)
├── mlruns/                       ← Artifacts
│   ├── 0/                        ← Experimento 0
│   │   └── {run_id}/
│   │       └── artifacts/
│   │           ├── bandit_model.pkl
│   │           ├── bandit_results.csv
│   │           └── config.json
│   └── 1/                        ← Experimento 1
│       └── {run_id}/
│
├── docker-compose.yml
├── src/
│   ├── train.py
│   └── evaluate.py
│
└── app/
    └── main.py
```

### Checklist Rota A (Fase 5)

- [ ] Treinar com `mlflow run . --entry-point train`
- [ ] Validar Golden Set no notebook 04
- [ ] Registrar modelo no MLflow Registry (Staging)
- [ ] Testar carregamento do modelo
- [ ] Promover para Production
- [ ] Subir docker compose
- [ ] Testar API endpoints
- [ ] Visualizar MLflow UI
- [ ] Documentar instrções de uso

---

# ☁️ ROTA B: Escalar para AWS (ECS + RDS + S3)

## Objetivo
Infraestrutura profissional, escalável, monitorada.

### Vantagens
- ✅ Auto-escalável (horizontal)
- ✅ Monitora automático (CloudWatch)
- ✅ Backup automático (RDS)
- ✅ CI/CD integrado (GitHub Actions)
- ✅ Multi-replica (3+ instâncias)
- ✅ Pronto para produção real

### Pré-requisitos

```bash
# 1. AWS Account com credenciais configuradas
aws configure

# 2. Terraform instalado
terraform --version  # v1.0+

# 3. GitHub Actions configurado
# Adicione secrets no repositório:
# - AWS_ACCOUNT_ID
# - AWS_REGION (us-east-2)
# - AWS_ROLE_TO_ASSUME
```

### Fase 5: Implementação AWS (Passo a Passo)

#### Passo 1: Infraestrutura Base (RDS + S3)

```hcl
# deploy/aws/terraform/mlflow.tf

# RDS PostgreSQL para MLflow
resource "aws_rds_cluster" "mlflow" {
  cluster_identifier      = "mlflow-postgres"
  engine                  = "aurora-postgresql"
  engine_version          = "14.6"
  database_name           = "mlflow"
  master_username         = "mlflow"
  master_password         = random_password.rds_password.result
  
  db_subnet_group_name    = aws_db_subnet_group.main.name
  skip_final_snapshot     = false
  final_snapshot_identifier = "mlflow-snapshot-${timestamp()}"
  
  backup_retention_period = 7  # 7 dias
  preferred_backup_window = "02:00-03:00"
}

# S3 para artifacts
resource "aws_s3_bucket" "mlflow_artifacts" {
  bucket = "datathon-mlflow-artifacts-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "mlflow_artifacts" {
  bucket = aws_s3_bucket.mlflow_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

#### Passo 2: ECS Task MLflow

```hcl
# deploy/aws/terraform/ecs_mlflow.tf

resource "aws_ecs_task_definition" "mlflow" {
  family                   = "datathon-mlflow"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name      = "mlflow"
    image     = "${aws_ecr_repository.mlflow.repository_url}:latest"
    
    portMappings = [{
      containerPort = 5000
      hostPort      = 5000
    }]

    environment = [
      {
        name  = "MLFLOW_BACKEND_STORE_URI"
        value = "postgresql://mlflow:${random_password.rds_password.result}@${aws_rds_cluster.mlflow.endpoint}:5432/mlflow"
      },
      {
        name  = "MLFLOW_DEFAULT_ARTIFACT_ROOT"
        value = "s3://${aws_s3_bucket.mlflow_artifacts.id}/mlruns"
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.mlflow.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

resource "aws_ecs_service" "mlflow" {
  name            = "datathon-bandit-mlflow"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.mlflow.arn
  desired_count   = var.mlflow_desired_count  # Default: 0 (pausado)
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.mlflow.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.mlflow.arn
    container_name   = "mlflow"
    container_port   = 5000
  }
}
```

#### Passo 3: Modificar FastAPI para AWS

```hcl
# deploy/aws/terraform/ecs_fastapi.tf (Modificado)

resource "aws_ecs_task_definition" "fastapi" {
  # ... (igual ao local, mas com variáveis para AWS)

  container_definitions = jsonencode([{
    name  = "fastapi"
    image = "${aws_ecr_repository.fastapi.repository_url}:latest"

    environment = [
      {
        name  = "MLFLOW_TRACKING_URI"
        value = "http://mlflow.datathon-bandit.internal:5000"
      },
      {
        name  = "MODEL_STAGE"
        value = "Production"
      },
      {
        name  = "AWS_REGION"
        value = var.aws_region
      }
    ]

    # ... resto igual ...
  }])
}
```

#### Passo 4: Deploy com Terraform

```bash
# Inicializar
cd deploy/aws/terraform
terraform init

# Plan (ver o que vai criar)
terraform plan -out=tfplan

# Apply (criar infraestrutura)
terraform apply tfplan

# Outputs (mostrar URLs)
terraform output
# Outputs como:
# - mlflow_url = http://alb-xxx.us-east-2.elb.amazonaws.com:5000
# - api_url = http://alb-xxx.us-east-2.elb.amazonaws.com
```

#### Passo 5: CI/CD com GitHub Actions

```yaml
# .github/workflows/mlflow-train-aws.yml

name: MLflow Training (AWS)

on:
  schedule:
    - cron: '0 2 * * 0'  # Segunda às 2 AM
  workflow_dispatch:

jobs:
  train:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions
          aws-region: us-east-2

      - name: Run Training on ECS
        run: |
          aws ecs run-task \
            --cluster datathon-bandit-cluster \
            --task-definition datathon-training \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}" \
            --overrides '{
              "containerOverrides": [{
                "name": "training",
                "command": ["python", "src/train.py", "--seed", "'$(date +%s)'"]
              }]
            }'

      - name: Update ECS Service
        run: |
          aws ecs update-service \
            --cluster datathon-bandit-cluster \
            --service datathon-bandit-fastapi \
            --force-new-deployment
```

### Checklist Rota B (Fase 5)

- [ ] Configurar credenciais AWS
- [ ] Instalar Terraform
- [ ] Criar RDS PostgreSQL
- [ ] Criar S3 bucket
- [ ] Deploy ECS Task MLflow
- [ ] Deploy ECS Task FastAPI
- [ ] Configurar Application Load Balancer
- [ ] Testar endpoints da API
- [ ] Visualizar MLflow UI
- [ ] Setup GitHub Actions
- [ ] Testar retreino automático
- [ ] Configurar CloudWatch logs

---

## 📊 Comparação das Duas Rotas (Fase 5 Final)

```
ROTA A: LOCAL (Docker Compose)
┌────────────────────────────────┐
│ docker-compose.yml             │
│ ├─ MLflow (SQLite local)       │
│ └─ FastAPI                     │
│                                │
│ Uptime: Enquanto máquina liga  │
│ Custo: R$ 0                    │
│ Scaling: Manual                │
│ Monitoramento: Nenhum          │
│ Auto-deploy: Não               │
└────────────────────────────────┘


ROTA B: AWS (ECS + RDS + S3)
┌────────────────────────────────┐
│ ECS Fargate                    │
│ ├─ MLflow Container            │
│ └─ FastAPI Container (3x)      │
│                                │
│ RDS PostgreSQL (Backup 7 dias) │
│ S3 (Artifacts)                 │
│ CloudWatch (Logs + Métricas)   │
│ ALB (Load Balancer)            │
│                                │
│ Uptime: 99.9%                 │
│ Custo: ~R$ 300-500/mês        │
│ Scaling: Automático            │
│ Monitoramento: Completo        │
│ Auto-deploy: CI/CD integrado   │
└────────────────────────────────┘
```

---

## 🎯 Checklist Completo (Todas as 5 Fases)

### ✅ Fase 1: Enriquecimento
- [ ] Adicionar Tags no notebook 03
- [ ] Aumentar Métricas (histórico + segmentos)
- [ ] Logar Gráficos (4+ visualizações)
- [ ] Logar Artefatos (CSV, PKL, JSON, Relatório)
- [ ] Testar: `mlflow ui --backend-store-uri sqlite:///mlflow.db`

### ✅ Fase 2: Model Registry
- [ ] Notebook 04 com Golden Set
- [ ] Criar wrapper `mlflow.pyfunc.PythonModel`
- [ ] Registrar modelo: `datathon-bandit-thompson`
- [ ] Promover para Production

### ✅ Fase 3: Scripts
- [ ] Converter notebook 03 → `src/train.py`
- [ ] Converter notebook 04 → `src/evaluate.py`
- [ ] Criar `MLproject` na raiz
- [ ] Testar: `mlflow run . --entry-point train`

### ✅ Fase 4: API Local
- [ ] Modificar `app/main.py` (carregar do Registry)
- [ ] Atualizar `Dockerfile.fastapi`
- [ ] Testar: `docker compose up`
- [ ] Validar endpoints

### ✅ Fase 5: Escolha sua Rota

**Se ROTA A (Local):**
- [ ] Documentar instruções docker compose
- [ ] Testar em servidor local/linux
- [ ] Demo pronta para apresentação

**Se ROTA B (AWS):**
- [ ] RDS PostgreSQL setup
- [ ] S3 buckets criados
- [ ] ECS Tasks definidas
- [ ] GitHub Actions configurado
- [ ] Testar end-to-end

---

## 🚀 Resumo

```
Fases 1-4: Desenvolvimento Local (igual para todos)
├─ Notebooks enriquecidos
├─ Scripts reproduzíveis
├─ API com MLflow Registry
└─ Tudo testado em Docker Compose

Fase 5: Escolha sua destinação
├─ ROTA A: Fica em Docker Compose (simples, grátis)
└─ ROTA B: Escala para AWS (profissional, automático)
```

Ambas as rotas funcionam perfeitamente. Escolha baseado no seu caso de uso! 🎯
