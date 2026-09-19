# MLflow: Roteiro para Este Fim de Semana
## Implementação Rápida (Local ou AWS)

---

## 🎯 Visão Geral: Duas Rotas, Uma Noite

```
FASES 1-4: IGUAL PARA TODOS (Local com Docker)
└─ Notebooks → Scripts → API → Testado

FASE 5: ESCOLHA SUA ROTA
├─ ROTA A: Docker Compose (continua local)
└─ ROTA B: AWS (escala para nuvem)
```

---

## ⏱️ Tempo Estimado

| Fase | Rota A | Rota B | O que fazer |
|------|--------|--------|---|
| **1** | 2h | 2h | Enriquecer Tracking |
| **2** | 1h | 1h | Model Registry |
| **3** | 1.5h | 1.5h | Scripts Reproduzíveis |
| **4** | 1h | 1h | API Local |
| **5** | 0.5h | 3h | Deployer |
| **TOTAL** | **6 horas** | **9 horas** |

**Ou mais rápido se pular alguns passos!**

---

# FASES 1-4: Igual para Ambas as Rotas

---

# FASE 1: Enriquecer Tracking (2h)

## Objetivo
Adicionar tags, métricas, gráficos e artefatos no notebook 03.

## Código Completo

```python
# notebook/03_Baseline_e_Thompson.ipynb

import mlflow
import matplotlib.pyplot as plt
import pickle
import json

mlflow.set_tracking_uri('sqlite:///../../mlflow.db')
mlflow.set_experiment('datathon-bandit-canal')

with mlflow.start_run(run_name='baseline_vs_thompson_complete'):
    
    # ===== TAGS =====
    mlflow.set_tag('stage', 'training')
    mlflow.set_tag('dataset', 'bank-term-deposit')
    mlflow.set_tag('algoritmo', 'thompson_sampling')
    mlflow.set_tag('producao_ready', 'false')
    
    # ===== PARÂMETROS =====
    mlflow.log_param('seed', 42)
    mlflow.log_param('test_size', 0.30)
    mlflow.log_param('train_rows', len(train_df))
    mlflow.log_param('test_rows', len(test_df))
    
    # ===== MÉTRICAS PRINCIPAIS =====
    mlflow.log_metric('thompson_conversion', metrics['thompson_conversion'])
    mlflow.log_metric('baseline_conversion', metrics['baseline_conversion'])
    mlflow.log_metric('lift_relative_pct', metrics['conversion_lift_relative'] * 100)
    
    # ===== MÉTRICAS COM HISTÓRICO =====
    for round_num in range(len(results)):
        mlflow.log_metric('thompson_rolling', 
                         results['thompson_cumulative_conversion'].iloc[round_num], 
                         step=round_num)
    
    # ===== GRÁFICOS =====
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    results[['thompson_cumulative_conversion', 'baseline_cumulative_conversion']].plot(ax=axes[0,0])
    axes[0,0].set_title('Conversão Acumulada')
    results['thompson_arm'].value_counts().plot.bar(ax=axes[0,1])
    axes[0,1].set_title('Escolhas Thompson')
    results.groupby('age_segment')['thompson_reward'].mean().plot.bar(ax=axes[1,0])
    axes[1,0].set_title('Performance por Segmento')
    plt.tight_layout()
    mlflow.log_figure(fig, 'dashboard.png')
    
    # ===== ARTEFATOS =====
    results.to_csv('bandit_results.csv', index=False)
    mlflow.log_artifact('bandit_results.csv')
    
    with open('bandit_model.pkl', 'wb') as f:
        pickle.dump(bandit, f)
    mlflow.log_artifact('bandit_model.pkl')
    
    mlflow.log_dict({
        'thompson_conversion': float(metrics['thompson_conversion']),
        'baseline_conversion': float(metrics['baseline_conversion']),
        'lift': float(metrics['conversion_lift_relative'])
    }, 'metrics.json')

print('✅ Fase 1 completa!')
```

## Verificar

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
# Acesse http://localhost:5000
# Veja: Tags, Params, Metrics, Artifacts
```

---

# FASE 2: Model Registry (1h)

## Notebook 04: Validar e Registrar

```python
# notebook/04_Avaliacao_e_Golden_Set.ipynb

import mlflow
import mlflow.pyfunc
from mlflow.tracking import MlflowClient
import pickle
import pandas as pd

mlflow.set_tracking_uri('sqlite:///../../mlflow.db')

# Golden Set validation
with mlflow.start_run(run_name='golden_set_validation'):
    # ... validar notebook 04 ...
    validation_score = 0.95  # Se > 0.8
    mlflow.log_metric('validation_score', validation_score)
    
    if validation_score > 0.8:
        # Registrar modelo
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
            artifacts={'bandit_model': 'bandit_model.pkl'},
            registered_model_name='datathon-bandit-thompson'
        )
        
        print('✅ Modelo registrado em Staging')
        
        # Promover para Production
        client = MlflowClient(tracking_uri='sqlite:///../../mlflow.db')
        versions = client.get_latest_versions('datathon-bandit-thompson', stages=['Staging'])
        
        if versions:
            client.transition_model_version_stage(
                name='datathon-bandit-thompson',
                version=versions[0].version,
                stage='Production'
            )
            print(f'✅ Modelo promovido para Production (v{versions[0].version})')

print('✅ Fase 2 completa!')
```

---

# FASE 3: Scripts Reproduzíveis (1.5h)

## Criar src/train.py

```python
# src/train.py

import argparse
import mlflow
import pickle
import pandas as pd
import numpy as np
from mabwiser.mab import MAB, LearningPolicy
from sklearn.model_selection import train_test_split

def main(seed=42, test_size=0.30):
    mlflow.set_tracking_uri('sqlite:///mlflow.db')
    mlflow.set_experiment('datathon-bandit-canal')
    
    df = pd.read_csv('data/processed/bank-term-deposit-subscription_eda/bank_full_tratado.csv')
    
    with mlflow.start_run(run_name=f'train_seed_{seed}'):
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
        
        # Simular
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
        
        print(f'✅ Treino: {conv:.2%} conversão')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--test-size', type=float, default=0.30)
    args = parser.parse_args()
    main(args.seed, args.test_size)
```

## Criar MLproject (na raiz)

```yaml
# MLproject

name: datathon-bandit

python_env: python_env.yaml

entry_points:
  train:
    parameters:
      seed: {type: int, default: 42}
      test_size: {type: float, default: 0.30}
    command: "python src/train.py --seed {seed} --test-size {test_size}"
```

## Testar

```bash
mlflow run . --entry-point train -P seed=42
mlflow run . --entry-point train -P seed=123
```

---

# FASE 4: API Local (1h)

## Modificar app/main.py

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
MODEL_STAGE = 'Production'

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    try:
        model = mlflow.pyfunc.load_model(f'models:/{MODEL_NAME}/{MODEL_STAGE}')
        print(f'✅ Modelo carregado: {MODEL_NAME}/{MODEL_STAGE}')
    except Exception as e:
        print(f'❌ Erro: {e}')
        raise
    yield
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
        return {'channel': prediction['recommended_channel'][0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/feedback')
def feedback(decision_id: str, outcome: bool):
    with mlflow.start_run(run_id=decision_id):
        mlflow.log_metric('outcome', int(outcome))
    return {'status': 'recorded'}
```

## Testar Tudo

```bash
# Subir
docker compose -f deploy/docker-compose.yml up -d

# Testar API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/recomendar \
  -H "Content-Type: application/json" \
  -d '{"age_segment": "jovem", "poutcome": "success", "previous": 1}'

# MLflow UI
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

# 🏠 ROTA A: Continuar em Docker Compose (0.5h)

## Tudo Pronto!

```bash
# Já está rodando localmente
docker compose -f deploy/docker-compose.yml up -d

# Acessar
# API: http://localhost:8000/docs
# MLflow: http://localhost:5002

# Para usar em servidor:
scp -r datathon-8mlet-grupo-04 usuario@servidor:/path/
ssh usuario@servidor
cd /path/datathon-8mlet-grupo-04
docker compose -f deploy/docker-compose.yml up -d
```

**Pronto para demo!** 🎉

---

# ☁️ ROTA B: Escalar para AWS (3h)

## Pré-requisitos (10 min)

```bash
# Instalar/configurar
aws configure  # Configure credenciais AWS
terraform --version  # v1.0+
```

## Passo 1: Preparar Imagens Docker (30 min)

```bash
# Build local
docker build -f deploy/Dockerfile.fastapi -t fastapi:latest .
docker build -f deploy/Dockerfile.mlflow -t mlflow:latest .

# Push para ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin {account}.dkr.ecr.us-east-2.amazonaws.com

docker tag fastapi:latest {account}.dkr.ecr.us-east-2.amazonaws.com/fastapi:latest
docker push {account}.dkr.ecr.us-east-2.amazonaws.com/fastapi:latest

docker tag mlflow:latest {account}.dkr.ecr.us-east-2.amazonaws.com/mlflow:latest
docker push {account}.dkr.ecr.us-east-2.amazonaws.com/mlflow:latest
```

## Passo 2: Deploy com Terraform (1.5h)

```bash
cd deploy/aws/terraform

# Initialize
terraform init

# Ver o que vai criar
terraform plan -out=tfplan

# Criar infraestrutura
terraform apply tfplan

# Outputs
terraform output
# Copie as URLs
```

## Passo 3: GitHub Actions CI/CD (1h)

```bash
# Adicione secrets no GitHub (Settings → Secrets):
# - AWS_ACCOUNT_ID
# - AWS_REGION (us-east-2)
# - AWS_ROLE_TO_ASSUME

# Crie arquivo:
# .github/workflows/deploy.yml

# A cada push: build, test, deploy automático
git add .
git commit -m "Deploy AWS com GitHub Actions"
git push
```

## Acessar

```bash
# Outputs do terraform mostram:
# api_url = http://alb-xxx.us-east-2.elb.amazonaws.com
# mlflow_url = http://alb-xxx.us-east-2.elb.amazonaws.com:5000

# Testar
curl http://alb-xxx.us-east-2.elb.amazonaws.com/health
curl http://alb-xxx.us-east-2.elb.amazonaws.com:5000
```

**Em produção!** 🚀

---

## 📊 Checklist Rápido

### Fase 1: Tracking
- [ ] Adicionar tags/params/metrics no notebook 03
- [ ] Logar gráficos e artefatos
- [ ] Verificar no MLflow UI

### Fase 2: Model Registry
- [ ] Golden Set validation no notebook 04
- [ ] Registrar modelo como MLflow Model
- [ ] Promover para Production

### Fase 3: Scripts
- [ ] Criar src/train.py
- [ ] Criar MLproject
- [ ] Testar: mlflow run . --entry-point train

### Fase 4: API
- [ ] Modificar app/main.py (carregar do MLflow)
- [ ] docker compose up
- [ ] Testar endpoints

### Fase 5A: Local (se escolher Rota A)
- [ ] Documentar docker compose
- [ ] Pronto para usar

### Fase 5B: AWS (se escolher Rota B)
- [ ] Push imagens para ECR
- [ ] terraform apply
- [ ] GitHub Actions configurado
- [ ] Testar URLs da ALB

---

## 🎯 Resumo

```
Fases 1-4: 6 horas (Docker Compose local - igual para todos)
Fase 5A: 0.5h (Continuar local)
Fase 5B: 3h (Escalar para AWS)

Total: 6-9 horas (este fim de semana!)
```

**Comece agora!** 📚
