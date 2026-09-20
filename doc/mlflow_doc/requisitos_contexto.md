# 📋 Requisitos e Contexto - Jornada MLflow

**Data:** 2026-09-20  
**Projeto:** datathon-8mlet-grupo-04  
**Status:** ✅ Em Execução

---

## 🎯 Objetivo da Jornada

Implementar **rastreamento completo de Machine Learning** usando MLflow, garantindo que:
- ✅ Modelos treinados sejam **registrados e versionados**
- ✅ Experimentos sejam **rastreáveis com métricas detalhadas**
- ✅ Artefatos sejam **persistidos e recuperáveis**
- ✅ Metadata seja **rica em descrições, tags e versões**
- ✅ Sistema funcione em **local (Docker) e AWS (ECS + RDS + S3)**

---

## 📊 Requisitos Funcionais

### 1. Model Registry

#### 1.1 Modelo Principal
- **Nome:** `thompson_sampling_bandit`
- **Origem:** Notebook `03_Baseline_e_Thompson.ipynb`
- **Algoritmo:** MABWiser Thompson Sampling
- **Dataset:** Bank Term Deposit Subscription (32.191 clientes)

#### 1.2 Descrição do Modelo
```
[OBRIGATÓRIO]
- Algoritmo utilizado
- Dataset de treino (size, split)
- Canais/Arms disponíveis
- Performance vs Baseline
  * Baseline conversion: 10.44% (regra fixa)
  * Modelo conversion: 13.67% (adaptativo)
  * Ganho: +31% relativo
- Features utilizadas (contextuais)
- Status: Production-ready
```

#### 1.3 Tags do Modelo (30+ tags)
```
[OBRIGATÓRIO]
Categoria: Projeto
- project: datathon-8mlet-grupo-04
- datathon: 8mlet-grupo-04

Categoria: Técnica
- algorithm: Thompson Sampling
- library: MABWiser
- language: Python
- task_type: Multi-Armed Bandit
- application: channel_optimization

Categoria: Dataset
- dataset: bank-term-deposit-subscription
- dataset_size: 32191
- train_samples: 22533
- test_samples: 9658
- split_ratio: 0.70/0.30

Categoria: Performance
- baseline_conversion_rate: 0.1044
- model_conversion_rate: 0.1367
- improvement_absolute: 0.0323
- improvement_relative: 0.3100
- improvement_percentage: 31.0%

Categoria: Arquitetura
- arms_count: 2
- arms: cellular,telephone
- features_count: 16
- features_engineered: yes
- contextual: yes

Categoria: Deploy
- environment: local
- status: production
- ready_for_deployment: true
- version_major: 1
- version_minor: 0
- version_patch: 0
```

#### 1.4 Versões do Modelo
```
[OBRIGATÓRIO]
v1 (Atual)
├─ Stage: Production
├─ Criação: 2026-09-20
├─ Description: [DETALHADA - vide 1.5]
├─ Artifacts:
│  └─ bandit_model_temp.pkl (serializado pickle)
├─ Metrics:
│  ├─ baseline_conversion: 0.1044
│  ├─ thompson_conversion: 0.1367
│  ├─ lift_absolute: 0.0323
│  └─ lift_relative: 0.3100
└─ Status: Pronto para produção
```

#### 1.5 Descrição Detalhada da Versão
```
[OBRIGATÓRIO - Preencher todas as seções]

**Thompson Sampling Bandit - v1**  
**Created:** 2026-09-20 | **Status:** Production

### Configuração do Treinamento
- Dataset: Bank Term Deposit Subscription
- Amostras Treino: 22.533 (70%)
- Amostras Teste: 9.658 (30%)
- Random Seed: 42
- Split Strategy: Stratified

### Modelo
- Algoritmo: MABWiser Thompson Sampling
- Prior Distribution: Beta-Bernoulli
- Approach: Balanced exploitation-exploration
- Arms: 2 (cellular, telephone)

### Performance
- Baseline: 10.44% conversão (telefone fixo)
- Thompson: 13.67% conversão (adaptativo)
- Ganho Absoluto: +3.23pp
- Ganho Relativo: +31.0%
- Thompson escolheu cellular: 9.560x (99%)
- Thompson escolheu telephone: 98x (1%)

### Features (16 total)
- Contextuais: age, job, marital, education, default, 
  balance, housing, loan, month, day, campaign, pdays, 
  previous, poutcome
- Engineered: age_segment (jovem/adulto/senior)

### Artefatos
- Modelo: bandit_model_temp.pkl (MABWiser object)
- Resultados: bandit_results.csv (9.658 rodadas)
- Métricas: bandit_metrics.json (resumo)
- Figura: conversao_e_distribuicao.png (gráficos)

### Pronto para Uso
✓ Treinado
✓ Artefatos salvos
✓ Registrado no Model Registry
✓ Em Production
✓ Pronto para API
```

---

### 2. Experimentos

#### 2.1 Experimento Principal
- **Nome:** `testemlflow`
- **Descrição:** Rastreamento de experimentos do Datathon Etapa 3
- **Runs Esperados:** Múltiplos (treino, validação, API)

#### 2.2 Run: Treino do Modelo (Notebook 03)

**Nome:** `etapa3_baseline_vs_thompson`

**Aba: Parameters** (16 parâmetros)
```
✅ OBRIGATÓRIO PREENCHER:
dataset: bank-term-deposit-subscription (dharmik34)
arms: ['cellular', 'telephone']
baseline_policy: regra fixa (sempre telephone)
baseline_arm: telephone
algoritmo_adaptativo: MABWiser ThompsonSampling
test_size: 0.30
seed: 42
contextual_rate_prior_weight: 20.0
best_arm_oracle_referencia: cellular
[... mais parametros específicos]
```

**Aba: Metrics** (10+ métricas)
```
✅ OBRIGATÓRIO PREENCHER:
baseline_conversion: 0.1044
thompson_conversion: 0.1367
conversion_lift_pp: 3.23
conversion_lift_relative_pct: 31.0
thompson_escolhas_cellular: 9560
thompson_escolhas_telephone: 98
[... mais métricas de performance]
```

**Aba: Artifacts** (4 arquivos)
```
✅ OBRIGATÓRIO LOGAR:
- bandit_results.csv (9.658 rodadas de simulação)
- bandit_metrics.json (resumo de performance)
- conversao_e_distribuicao.png (gráficos comparativos)
- model/bandit_model_temp.pkl (modelo serializado)
```

**Aba: Tags**
```
✅ OBRIGATÓRIO DEFINIR:
notebook: 03_Baseline_e_Thompson
etapa: etapa3_simulacao
tipo: simulacao
versao: v1.0
environment: local
```

#### 2.3 Run: API Inference (FastAPI)

**Nome:** `api_inference`  
**Aba: Parameters**
```
arm_value: [0 ou 1]
```

**Aba: Metrics**
```
confidence: [0-1]
```

**Aba: Tags**
```
decision_id: [ID único]
arm_selected: cellular ou telephone
model_version: thompson_v1
```

#### 2.4 Run: API Feedback (FastAPI)

**Nome:** `api_feedback`  
**Aba: Parameters**
```
conversion_observed: [0 ou 1]
```

**Aba: Metrics**
```
conversion: [0 ou 1]
feedback_delay_seconds: [N]
```

**Aba: Tags**
```
decision_id: [ID único]
arm: cellular ou telephone
conversion: yes ou no
```

---

## 🖥️ Requisitos de UI - MLflow Interface

### Interface do MLflow: Pré-requisitos para Funcionalidade

A **UI do MLflow em http://localhost:5002** precisa exibir TODAS as informações abaixo para validar a implementação:

#### 📊 Model Registry View

**Requisito 1: Modelo Visível**
```
✅ Model Registry
   └─ thompson_sampling_bandit
      ├─ Status: Production
      ├─ Versão: 1
      ├─ Data Criação: 2026-09-20
      └─ [Clicável para detalhes]
```

**Requisito 2: Descrição do Modelo**
```
✅ Modelo > Descrição (aberta)
   ├─ Algoritmo: Thompson Sampling
   ├─ Dataset: Bank Term Deposit Subscription (32.191 clientes)
   ├─ Performance vs Baseline:
   │  ├─ Baseline: 10.44%
   │  ├─ Modelo: 13.67%
   │  └─ Ganho: +31%
   ├─ Canais: cellular, telephone
   └─ Status: Production-ready
```

**Requisito 3: Tags do Modelo (30+)**
```
✅ Modelo > Tags (aba)
   ├─ project: datathon-8mlet-grupo-04
   ├─ algorithm: Thompson Sampling
   ├─ dataset: bank-term-deposit-subscription
   ├─ baseline_conversion_rate: 0.1044
   ├─ model_conversion_rate: 0.1367
   ├─ improvement_percentage: 31.0%
   ├─ status: production
   └─ [30+ tags no total]
```

**Requisito 4: Versão Detalhada**
```
✅ Modelo > Versões > v1
   ├─ Stage: Production
   ├─ Criado: 2026-09-20
   ├─ Description (completa):
   │  ├─ Configuração do Treinamento
   │  ├─ Modelo (algoritmo, distribuição)
   │  ├─ Métricas de Treino
   │  ├─ Features Utilizadas
   │  └─ Pronto para Uso
   └─ Artifacts:
      └─ bandit_model_temp.pkl [CLICÁVEL - download]
```

#### 🧪 Experiments View

**Requisito 5: Experimento Visível**
```
✅ Experiments
   └─ testemlflow
      ├─ Criado: 2026-09-20
      ├─ Runs: 3+ (incluindo etapa3_baseline_vs_thompson)
      └─ [Clicável para detalhes]
```

**Requisito 6: Run Principal Visível**
```
✅ testemlflow > Runs
   └─ etapa3_baseline_vs_thompson
      ├─ Status: FINISHED
      ├─ Start Time: 2026-09-20 XX:XX:XX
      ├─ Duration: ~5 min
      ├─ [Clicável para detalhes]
      └─ [Abas visíveis: Parameters, Metrics, Artifacts]
```

**Requisito 7: Parameters (Aba)**
```
✅ Run > Parameters (16 parâmetros visíveis)
   ├─ dataset: bank-term-deposit-subscription (dharmik34)
   ├─ arms: ['cellular', 'telephone']
   ├─ baseline_policy: regra fixa (sempre telephone)
   ├─ baseline_arm: telephone
   ├─ algoritmo_adaptativo: MABWiser ThompsonSampling
   ├─ test_size: 0.3
   ├─ seed: 42
   ├─ contextual_rate_prior_weight: 20.0
   ├─ best_arm_oracle_referencia: cellular
   └─ [11+ parâmetros adicionais]
```

**Requisito 8: Metrics (Aba)**
```
✅ Run > Metrics (10+ métricas visíveis e gráficos)
   ├─ baseline_conversion: 0.1044 [com gráfico de série temporal]
   ├─ thompson_conversion: 0.1367 [com gráfico de série temporal]
   ├─ conversion_lift_pp: 3.23
   ├─ conversion_lift_relative_pct: 31.0
   ├─ thompson_escolhas_cellular: 9560
   ├─ thompson_escolhas_telephone: 98
   └─ [4+ métricas adicionais com histórico de execução]
```

**Requisito 9: Artifacts (Aba)**
```
✅ Run > Artifacts (4 arquivos visíveis e baixáveis)
   ├─ 📄 bandit_results.csv (678 KB) [PREVIEW + DOWNLOAD]
   ├─ 📄 bandit_metrics.json [PREVIEW + DOWNLOAD]
   ├─ 🖼️  conversao_e_distribuicao.png [VISUALIZAÇÃO + DOWNLOAD]
   └─ 📦 model/ [PASTA]
      └─ bandit_model_temp.pkl [DOWNLOAD]
```

**Requisito 10: Tags da Run (Aba)**
```
✅ Run > Tags
   ├─ notebook: 03_Baseline_e_Thompson
   ├─ etapa: etapa3_simulacao
   ├─ tipo: simulacao
   ├─ versao: v1.0
   └─ environment: local
```

#### 📈 Comparação Visual

**Requisito 11: Comparação entre Runs**
```
✅ Experimento > Compare Runs (funcionalidade)
   ├─ Seleção de 2+ runs para comparação
   ├─ Exibição lado-a-lado de:
   │  ├─ Parameters (diferenças destacadas)
   │  ├─ Metrics (gráficos sobrepostos)
   │  └─ Artifacts (listados)
   └─ [Exportar comparação]
```

#### 🔗 Rastreabilidade

**Requisito 12: Links Cruzados**
```
✅ Model Registry > Versão > "Registered From Run"
   └─ Link para o run no experimento que o registrou
      └─ ffdde5fea68e40b8bdd43a021185d2b2

✅ Experimento > Run > "Model Registry"
   └─ Link para o modelo registrado (se aplicável)
      └─ thompson_sampling_bandit v1
```

---

## 📁 Paths do Banco de Dados MLflow

### ⚠️ IMPORTANTE - Qual Banco Usar em Cada Contexto

#### **LOCAL (Execução Standalone - Current Setup)**
```
Banco: /Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04/mlflow.db
Backend Store URI: sqlite:////Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04/mlflow.db
Acesso: sqlite3 mlflow.db (local)
URL: http://localhost:5002
Comando: mlflow server --host 0.0.0.0 --port 5002 --backend-store-uri sqlite:///$(pwd)/mlflow.db
```

#### **DOCKER COMPOSE (Future Implementation)**
```yaml
Services:
  mlflow:
    volumes:
      - mlflow_data:/mlflow
    
    Backend Store URI (dentro do container):
      sqlite:////mlflow/mlflow.db
    
    Artifact Root (dentro do container):
      /mlflow/artifacts
    
    Volume Docker:
      mlflow_data:/mlflow → Local: /var/lib/docker/volumes/mlflow_data/_data/
    
    URL: http://localhost:5002
    FastAPI Conecta: http://mlflow:5000 (interno à rede Docker)
```

**Banco no Docker:**
```
DENTRO DO CONTAINER:        /mlflow/mlflow.db
NO HOST (Docker volume):    /var/lib/docker/volumes/mlflow_data/_data/mlflow.db
Acesso do Host:             docker exec datathon_mlflow sqlite3 /mlflow/mlflow.db
```

#### **AWS ECS + RDS (Production)**
```
Backend Store URI:
  postgresql://user:password@rds-endpoint:5432/mlflow

RDS Details:
  - Engine: PostgreSQL 14+
  - Database: mlflow
  - Host: mlflow-rds.xxxxx.rds.amazonaws.com
  - Port: 5432
  - Username: ${RDS_USER}
  - Password: ${RDS_PASSWORD}

Artifact Store:
  s3://bucket-name/mlflow

Environment Variables:
  MLFLOW_TRACKING_URI=http://mlflow.ecs.internal:5000
  MLFLOW_BACKEND_STORE_URI=postgresql://...
  MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://bucket/mlflow
```

---

## 🏗️ Requisitos Técnicos

### 3. Infraestrutura Local (Docker Compose - Planejado)

```yaml
Services:
✅ MLflow Server (porta 5002)
   - Backend: SQLite em volume Docker
   - Path: sqlite:////mlflow/mlflow.db (dentro do container)
   - Volume: mlflow_data:/mlflow
   - Artifacts: /mlflow/artifacts (volume Docker)
   - API: http://localhost:5002

✅ FastAPI (porta 8000)
   - Conectado ao MLflow via http://mlflow:5000 (rede Docker)
   - Logging automático de inferências
   - Suporta feedback online
```

### Configuração do Docker Compose (docker-compose.yml)
```yaml
mlflow:
  image: python:3.11-slim
  container_name: datathon_mlflow
  ports:
    - "5002:5000"
  volumes:
    - mlflow_data:/mlflow
  working_dir: /mlflow
  command: |
    mlflow server \
      --host 0.0.0.0 \
      --port 5000 \
      --backend-store-uri sqlite:////mlflow/mlflow.db \
      --default-artifact-root /mlflow/artifacts

volumes:
  mlflow_data:
    driver: local
```

**Observação:** O banco atual está rodando localmente em:
```
/Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04/mlflow.db
```

Ao migrar para Docker Compose, o banco será armazenado em:
```
Volume Docker: /var/lib/docker/volumes/mlflow_data/_data/mlflow.db
Dentro do container: /mlflow/mlflow.db
```

### 4. Infraestrutura AWS (ECS + RDS + S3)

```
[Variáveis de Ambiente]
✅ ENVIRONMENT=aws
✅ RDS_HOST=[endpoint]
✅ RDS_USER=[user]
✅ RDS_PASSWORD=[password]
✅ S3_BUCKET=[bucket-name]
✅ AWS_REGION=us-east-2

[Storage]
✅ Backend Store: PostgreSQL (RDS)
✅ Artifact Store: S3
```

### 5. Detecção Automática de Ambiente

```python
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

if ENVIRONMENT == "local":
    MLFLOW_TRACKING_URI = "http://localhost:5000"
    MLFLOW_BACKEND_STORE_URI = "sqlite:///mlflow.db"
    
elif ENVIRONMENT == "aws":
    MLFLOW_TRACKING_URI = "http://mlflow:5000"
    MLFLOW_BACKEND_STORE_URI = "postgresql://..."
```

---

## 📸 Visualização Esperada na UI do MLflow

### Tela 1: Model Registry
```
┌─────────────────────────────────────────────────────────────┐
│ MLflow - Model Registry                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Models                                                      │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                             │
│ ✓ thompson_sampling_bandit                                 │
│   └─ Version 1 (Production)                                │
│      Created: 2026-09-20 02:35:25 PM                       │
│      Description: [Thompson Sampling Multi-Armed Bandit...]│
│      Tags: 30+                                             │
│      Latest Version: v1                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tela 2: Modelo Detalhado - Aba Description
```
┌─────────────────────────────────────────────────────────────┐
│ thompson_sampling_bandit > Version 1 (Production)           │
├─────────────────────────────────────────────────────────────┤
│ [Description] [Tags] [Version] [Activity]                  │
│                                                             │
│ Description:                                                │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                             │
│ Thompson Sampling Multi-Armed Bandit para otimização        │
│ de canal de contato.                                        │
│                                                             │
│ **Algoritmo:** MABWiser Thompson Sampling                   │
│ **Dataset:** Bank Term Deposit Subscription                 │
│ - Total: 32.191 clientes                                    │
│ - Treino: 22.533 (70%)                                      │
│ - Teste: 9.658 (30%)                                        │
│                                                             │
│ **Desempenho:**                                             │
│ - Baseline: 10.44% conversão                                │
│ - Thompson: 13.67% conversão                                │
│ - Ganho: +31% relativo                                      │
│                                                             │
│ **Status:** PRODUCTION - Pronto para usar em produção       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tela 3: Modelo Detalhado - Aba Tags
```
┌─────────────────────────────────────────────────────────────┐
│ thompson_sampling_bandit > Version 1 > Tags                 │
├─────────────────────────────────────────────────────────────┤
│ [Description] [Tags] [Version] [Activity]                  │
│                                                             │
│ 30+ Tags:                                                   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                             │
│ 🏷️ project: datathon-8mlet-grupo-04                         │
│ 🏷️ algorithm: Thompson Sampling                            │
│ 🏷️ library: MABWiser                                       │
│ 🏷️ dataset: bank-term-deposit-subscription                │
│ 🏷️ baseline_conversion_rate: 0.1044                        │
│ 🏷️ model_conversion_rate: 0.1367                           │
│ 🏷️ improvement_percentage: 31.0%                           │
│ 🏷️ status: production                                      │
│ 🏷️ ready_for_deployment: true                              │
│ ... [21+ tags adicionais]                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tela 4: Experimento - Runs
```
┌─────────────────────────────────────────────────────────────┐
│ testemlflow > Runs                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Run Name              | Status   | Created           | Src │
│ ──────────────────────┼──────────┼───────────────────┼──── │
│ etapa3_baseline_vs... │ FINISHED │ 2026-09-20 18:44 │ ✓   │
│                                                             │
│ Click para expandir:                                        │
│ ├─ Parameters: 16                                           │
│ ├─ Metrics: 10+                                             │
│ ├─ Artifacts: 4 files                                       │
│ └─ Tags: notebook, etapa, tipo, versao, environment        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tela 5: Run Detalhado - Parameters
```
┌─────────────────────────────────────────────────────────────┐
│ testemlflow > etapa3_baseline_vs_thompson > Parameters      │
├─────────────────────────────────────────────────────────────┤
│ [Parameters] [Metrics] [Artifacts] [Tags] [System Metrics]  │
│                                                             │
│ Name                             | Value                   │
│ ─────────────────────────────────┼────────────────────────│
│ dataset                          │ bank-term-deposit...   │
│ arms                             │ ['cellular', 'tele...] │
│ baseline_policy                  │ regra fixa (sempre...  │
│ baseline_arm                     │ telephone              │
│ algoritmo_adaptativo             │ MABWiser Thompsonsa... │
│ test_size                        │ 0.3                    │
│ seed                             │ 42                     │
│ contextual_rate_prior_weight     │ 20.0                   │
│ [... 8+ parâmetros adicionais]                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tela 6: Run Detalhado - Metrics
```
┌─────────────────────────────────────────────────────────────┐
│ testemlflow > etapa3_baseline_vs_thompson > Metrics         │
├─────────────────────────────────────────────────────────────┤
│ [Parameters] [Metrics] [Artifacts] [Tags] [System Metrics]  │
│                                                             │
│ Métrica                     | Valor    | Histórico         │
│ ────────────────────────────┼──────────┼──────────────────│
│ baseline_conversion         │ 0.1044   │ [GRÁFICO LINEAR] │
│ thompson_conversion         │ 0.1367   │ [GRÁFICO LINEAR] │
│ conversion_lift_pp          │ 3.23     │ ───────────      │
│ conversion_lift_relative... │ 31.0     │ ───────────      │
│ thompson_escolhas_cellular  │ 9560     │ ───────────      │
│ thompson_escolhas_telephone │ 98       │ ───────────      │
│ [... 4+ métricas adicionais]                               │
│                                                             │
│ 📊 [Visualizar como Gráfico Comparativo]                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tela 7: Run Detalhado - Artifacts
```
┌─────────────────────────────────────────────────────────────┐
│ testemlflow > etapa3_baseline_vs_thompson > Artifacts       │
├─────────────────────────────────────────────────────────────┤
│ [Parameters] [Metrics] [Artifacts] [Tags] [System Metrics]  │
│                                                             │
│ Artifacts (4 files):                                        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                             │
│ 📄 bandit_results.csv (678 KB)                              │
│    └─ [PREVIEW] [DOWNLOAD]                                 │
│                                                             │
│ 📄 bandit_metrics.json                                      │
│    └─ [PREVIEW] [DOWNLOAD]                                 │
│                                                             │
│ 🖼️  conversao_e_distribuicao.png                           │
│    └─ [VIEW IMAGE] [DOWNLOAD]                              │
│                                                             │
│ 📦 model/                                                   │
│    └─ bandit_model_temp.pkl [DOWNLOAD]                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist de Implementação

### Fase 1: Model Registry ✅
- [x] Modelo criado e salvo (notebook 03)
- [x] Registrado no Model Registry
- [x] Description completa preenchida
- [x] 30+ tags adicionadas
- [x] Version 1 criada
- [x] Promovido para Production

**✅ Validação UI (http://localhost:5002):**
- [x] thompson_sampling_bandit visível em Model Registry
- [x] Descrição exibida (algoritmo, dataset, performance)
- [x] 30+ tags visíveis (project, algorithm, dataset, status, etc)
- [x] Version 1 em Production
- [x] Artifacts: bandit_model_temp.pkl baixável
- [x] Links cruzados funcionando

### Fase 2: Experimentos ✅
- [x] Experimento `testemlflow` criado
- [x] Run `etapa3_baseline_vs_thompson` com:
  - [x] 16 parâmetros logados
  - [x] 10+ métricas logadas
  - [x] 4 artefatos salvos
  - [x] Tags definidas

**✅ Validação UI (http://localhost:5002):**
- [x] testemlflow experimento visível
- [x] Run etapa3_baseline_vs_thompson listado
- [x] **Parameters aba:** 16 parâmetros exibidos
  - dataset, arms, baseline_policy, algoritmo_adaptativo, test_size, seed, etc
- [x] **Metrics aba:** 10+ métricas com valores
  - baseline_conversion: 0.1044
  - thompson_conversion: 0.1367
  - conversion_lift_pp: 3.23
  - conversion_lift_relative_pct: 31.0
  - thompson_escolhas_cellular: 9560
  - thompson_escolhas_telephone: 98
- [x] **Artifacts aba:** 4 arquivos com preview/download
  - bandit_results.csv (678 KB)
  - bandit_metrics.json
  - conversao_e_distribuicao.png (imagem visível)
  - model/bandit_model_temp.pkl
- [x] **Tags aba:** notebook, etapa, tipo, versao, environment
- [x] **Rastreabilidade:** Link para Model Registry visível

### Fase 3: API Integration ⏳
- [ ] Endpoint `/recomendar` logando em `api_inference`
  - [ ] Runs `api_inference` aparecendo no experimento
  - [ ] Parameters: arm_value registrado
  - [ ] Metrics: confidence registrado
  - [ ] Tags: decision_id, arm_selected, model_version
  
- [ ] Endpoint `/feedback` logando em `api_feedback`
  - [ ] Runs `api_feedback` aparecendo no experimento
  - [ ] Parameters: conversion_observed registrado
  - [ ] Metrics: conversion, feedback_delay_seconds registrados
  - [ ] Tags: decision_id, arm, conversion

- [ ] Rastreamento de decisões e resultados
  - [ ] Histórico de decisões visível em Metrics
  - [ ] Comparação de performance em tempo real

### Fase 4: AWS ⏳
- [ ] RDS PostgreSQL configurado
  - [ ] Backend store URI apontando para RDS
  - [ ] Schema MLflow criado no RDS
  
- [ ] S3 bucket criado
  - [ ] Artifact root apontando para S3
  - [ ] Artifacts sendo salvos em S3
  
- [ ] ECS task definition com variáveis de ambiente
  - [ ] ENVIRONMENT=aws configurado
  - [ ] RDS_HOST, RDS_USER, RDS_PASSWORD definidos
  - [ ] S3_BUCKET configurado
  - [ ] MLflow server rodando em ECS
  
- [ ] MLflow server rodando em ECS
  - [ ] Acessível via endpoint AWS
  - [ ] Conectado ao RDS
  - [ ] Salvando artifacts em S3
  - [ ] UI do MLflow carregando dados do RDS

---

## 📌 REFERÊNCIA RÁPIDA - Path do Banco

### **Use Este Path:**

```bash
# LOCAL (atual):
sqlite3 /Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04/mlflow.db

# OU (relativo ao projeto):
cd /Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04
sqlite3 mlflow.db

# Backend Store URI (para mlflow server):
sqlite:////Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04/mlflow.db

# Backend Store URI (relativo):
sqlite:///$(pwd)/mlflow.db

# Para Docker (quando implementado):
docker exec datathon_mlflow sqlite3 /mlflow/mlflow.db
```

### **Para AWS (quando migrar):**
```bash
# RDS PostgreSQL
postgresql://user:password@mlflow-rds.xxxxx.rds.amazonaws.com:5432/mlflow

# S3 para Artifacts
s3://seu-bucket/mlflow
```

---

## 🎯 Validação Funcional - O QUE VERIFICAR NA UI

### ✅ Teste 1: Acessar Model Registry
```bash
URL: http://localhost:5002
Ação: Clicar em "Model Registry" no menu
Esperado: ✓ thompson_sampling_bandit aparece na lista
```

### ✅ Teste 2: Visualizar Descrição do Modelo
```bash
URL: http://localhost:5002/#/models/thompson_sampling_bandit
Aba: Description
Esperado: ✓ Texto completo com:
  - Algoritmo, Dataset, Performance, Status
  - Conversão baseline: 10.44%
  - Conversão modelo: 13.67%
  - Ganho: +31%
```

### ✅ Teste 3: Visualizar Tags do Modelo
```bash
URL: http://localhost:5002/#/models/thompson_sampling_bandit
Aba: Tags
Esperado: ✓ 30+ tags visíveis:
  - project, datathon, algorithm, library
  - dataset, dataset_size, train_samples, test_samples
  - baseline_conversion_rate, model_conversion_rate
  - improvement_percentage, status, environment
  - [... 17+ tags adicionais]
```

### ✅ Teste 4: Visualizar Version Details
```bash
URL: http://localhost:5002/#/models/thompson_sampling_bandit/versions/1
Esperado: ✓ Informações detalhadas:
  - Stage: Production
  - Created: 2026-09-20
  - Description: [Texto longo com seções]
  - Artifacts: bandit_model_temp.pkl [DOWNLOAD]
```

### ✅ Teste 5: Acessar Experimento
```bash
URL: http://localhost:5002/#/experiments/1
Esperado: ✓ Experimento "testemlflow" visível
  - Runs: 3+ listados
  - etapa3_baseline_vs_thompson como principal
```

### ✅ Teste 6: Visualizar Run - Parameters
```bash
URL: http://localhost:5002/#/experiments/[ID]/runs/[RUN_ID]
Aba: Parameters
Esperado: ✓ 16 parâmetros visíveis:
  - dataset: bank-term-deposit-subscription (dharmik34)
  - arms: ['cellular', 'telephone']
  - baseline_policy: regra fixa (sempre telephone)
  - baseline_arm: telephone
  - algoritmo_adaptativo: MABWiser ThompsonSampling
  - test_size: 0.3
  - seed: 42
  - contextual_rate_prior_weight: 20.0
  - best_arm_oracle_referencia: cellular
  - [... 7+ parâmetros]
```

### ✅ Teste 7: Visualizar Run - Metrics
```bash
URL: http://localhost:5002/#/experiments/[ID]/runs/[RUN_ID]
Aba: Metrics
Esperado: ✓ 10+ métricas com valores:
  - baseline_conversion: 0.1044
  - thompson_conversion: 0.1367
  - conversion_lift_pp: 3.23
  - conversion_lift_relative_pct: 31.0
  - thompson_escolhas_cellular: 9560
  - thompson_escolhas_telephone: 98
  - [... 4+ métricas]
  - Gráficos de séries temporais visíveis
```

### ✅ Teste 8: Visualizar Run - Artifacts
```bash
URL: http://localhost:5002/#/experiments/[ID]/runs/[RUN_ID]
Aba: Artifacts
Esperado: ✓ 4 arquivos listados:
  - 📄 bandit_results.csv (678 KB) [DOWNLOAD]
  - 📄 bandit_metrics.json [PREVIEW + DOWNLOAD]
  - 🖼️  conversao_e_distribuicao.png [VIEW + DOWNLOAD]
  - 📦 model/bandit_model_temp.pkl [DOWNLOAD]
```

### ✅ Teste 9: Visualizar Run - Tags
```bash
URL: http://localhost:5002/#/experiments/[ID]/runs/[RUN_ID]
Aba: Tags (se disponível)
Esperado: ✓ 5 tags visíveis:
  - notebook: 03_Baseline_e_Thompson
  - etapa: etapa3_simulacao
  - tipo: simulacao
  - versao: v1.0
  - environment: local
```

### ✅ Teste 10: Rastreabilidade - Model Registry para Run
```bash
URL: http://localhost:5002/#/models/thompson_sampling_bandit/versions/1
Procurar: "Registered From Run" ou link similar
Esperado: ✓ Link clicável para run original (ffdde5fea68e40b8bdd43a021185d2b2)
```

### ✅ Teste 11: Comparar Runs
```bash
URL: http://localhost:5002/#/experiments/1
Ação: Selecionar 2+ runs e clicar "Compare"
Esperado: ✓ Comparação lado-a-lado de:
  - Parameters (diferenças destacadas)
  - Metrics (gráficos sobrepostos)
  - Artifacts (listados)
```

---

## 📋 Resumo de Validação

| Item | Local | Status | Verificado |
|------|-------|--------|-----------|
| Model Registry | http://localhost:5002/#/models | ✅ | 2026-09-20 |
| thompson_sampling_bandit | Model Registry | ✅ | 2026-09-20 |
| Description | Model details | ✅ | 2026-09-20 |
| 30+ Tags | Model > Tags | ✅ | 2026-09-20 |
| Version 1 Production | Model > Versions | ✅ | 2026-09-20 |
| testemlflow experiment | http://localhost:5002/#/experiments | ✅ | 2026-09-20 |
| etapa3_baseline_vs_thompson run | Experiment > Runs | ✅ | 2026-09-20 |
| 16 Parameters | Run > Parameters | ✅ | 2026-09-20 |
| 10+ Metrics | Run > Metrics | ✅ | 2026-09-20 |
| 4 Artifacts | Run > Artifacts | ✅ | 2026-09-20 |
| Run Tags | Run > Tags | ✅ | 2026-09-20 |

---

## 📍 Arquivos Relevantes

```
datathon-8mlet-grupo-04/
├── notebooks/
│   └── 03_Baseline_e_Thompson.ipynb ← Cria modelo + registra
├── app/
│   ├── mlflow_config.py ← Config centralizada
│   ├── mlflow_utils.py ← Funções de logging
│   └── main.py ← API com logging
├── mlflow.db ← Banco SQLite (local)
├── mlruns/ ← Artefatos locais
└── doc/mlflow_doc/
    ├── requisitos_contexto.md ← Este arquivo
    ├── EXEMPLO_IMPLEMENTACAO_MLFLOW.md
    ├── FLUXO_COMPLETO_NOTEBOOK_API_MLFLOW.md
    └── README_MLFLOW.md
```

---

## 🔗 Links Úteis

- **MLflow UI:** http://localhost:5002
- **API FastAPI:** http://localhost:8000/docs
- **Experimento testemlflow:** http://localhost:5002/#/experiments/1
- **Modelo thompson_sampling_bandit:** http://localhost:5002/#/models/thompson_sampling_bandit

---

## 📝 Notas Importantes

1. **Schema SQLite:** Atualizado para versão 2.10.2 do MLflow
2. **Porta MLflow:** Mapeada para 5002 (forwarding de 5000)
3. **Volume Docker:** `mlflow_data` para persistência
4. **Artefatos:** Salvos em `mlruns/` local e S3 em produção
5. **Graceful Degradation:** Sistema funciona se MLflow indisponível

---

**Versão:** 1.0  
**Última Atualização:** 2026-09-20  
**Responsável:** Vagner Antônio da Silva
