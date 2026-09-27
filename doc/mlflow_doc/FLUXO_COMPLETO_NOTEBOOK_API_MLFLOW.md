# 🎯 Fluxo Completo: Notebook → API → MLflow

Este documento mostra o fluxo REAL de como o modelo Thompson Sampling treinado no notebook se integra com a API e MLflow.

## 📊 Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Notebook 03                                                        │
│  ├─ Treina Thompson Sampling (MABWiser)                            │
│  ├─ Salva: bandit_model.pkl                                        │
│  └─ Loga métricas no MLflow                                        │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  MLflow Server (SQLite)                                            │
│  ├─ Experimento: "testemlflow"                                     │
│  ├─ Runs: etapa3_simulacao                                         │
│  └─ Artifacts: resultados.csv, métricas.json                      │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  API FastAPI                                                       │
│  ├─ Carrega: bandit_model.pkl (na startup)                         │
│  ├─ POST /recomendar → bandit.predict()                            │
│  ├─ POST /feedback → bandit.partial_fit() + loga no MLflow        │
│  └─ GET /stats → bandit.stats()                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Passo 1: Iniciar MLflow Server

```bash
cd datathon-8mlet-grupo-04

# Iniciar MLflow server em background
mlflow server --backend-store-uri sqlite:///mlflow.db \
              --default-artifact-root ./mlruns \
              --host 0.0.0.0 \
              --port 5002 &

# Verificar que subiu
sleep 3
curl http://localhost:5002/health  # Deve retornar OK
```

**Resultado esperado:**
```
INFO mlflow.server: Created MLflow database tables at sqlite:///mlflow.db
INFO uvicorn: Started server process [XXXX]
INFO uvicorn: Application startup complete.
```

---

## 📓 Passo 2: Treinar Modelo (Notebook 03)

### Abrir o Jupyter Notebook

```bash
jupyter notebook notebooks/03_Baseline_e_Thompson.ipynb
```

### O que o notebook faz:

1. **Carrega dados**: `data/processed/bank-term-deposit-subscription_eda/bank_full_tratado.csv`

2. **Treina 2 políticas**:
   - **Baseline**: regra fixa (sempre "telephone")
   - **Thompson Sampling**: bandit adaptativo (MABWiser)

3. **Simula 9,333 rodadas** (30% dos dados para teste)
   - Resultado: Thompson ganha +3.23% em conversão (13.67% vs 10.44%)

4. **Salva artefatos**:
   ```
   data/processed/bank-term-deposit-subscription_eda/
   ├─ bandit_model.pkl          ← Modelo para API usar
   ├─ bandit_results.csv        ← Simulação completa
   ├─ bandit_metrics.json       ← Métricas resumidas
   └─ context_rates.csv         ← Taxas por contexto
   ```

5. **Loga no MLflow**:
   ```
   Experimento: testemlflow
   Run: etapa3_simulacao
   Params:
     - dataset: bank-term-deposit-subscription
     - test_size: 0.30
     - algoritmo_adaptativo: MABWiser ThompsonSampling
   Metrics:
     - baseline_conversion: 10.44%
     - thompson_conversion: 13.67%
     - conversion_lift_relative_pct: +31.0%
   Artifacts:
     - resultados.csv
     - metricas.json
   ```

### Executar o notebook:

1. Clicar em "Run All Cells" ou executar célula por célula
2. Ao final, verá: `✅ Experimento logado no MLflow!`
3. Procure por: `bandit_model.pkl` em `data/processed/bank-term-deposit-subscription_eda/`

---

## 🔍 Passo 3: Verificar no MLflow UI

Abrir browser:
```
http://localhost:5002/
```

### O que você verá:

**Experimento: `testemlflow`**
```
├─ Run: etapa3_simulacao
│  ├─ Parâmetros
│  │  ├─ dataset: bank-term-deposit-subscription
│  │  ├─ test_size: 0.30
│  │  ├─ algoritmo_adaptativo: MABWiser ThompsonSampling
│  │  └─ [16 mais parâmetros]
│  │
│  ├─ Métricas
│  │  ├─ baseline_conversion: 0.1044 (10.44%)
│  │  ├─ thompson_conversion: 0.1367 (13.67%)
│  │  ├─ conversion_lift_absolute: 0.0323 (+3.23%)
│  │  └─ conversion_lift_relative_pct: 31.0 (+31.0%)
│  │
│  └─ Artifacts
│     ├─ resultados.csv (9333 linhas com simulação completa)
│     └─ metricas.json (resumo de métricas)
```

---

## 🚀 Passo 4: Iniciar API FastAPI

Em outro terminal:

```bash
cd datathon-8mlet-grupo-04

# Rodar API
uvicorn app.main:app --reload --port 8000
```

**O que a API faz na startup:**
```python
@app.on_event("startup")
async def startup_event():
    initialize_mlflow()  # ← Configura tracking
    logger.info("🚀 API iniciando...")
```

**Resultado esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
🚀 API iniciando...
✅ API pronta!
```

---

## 📡 Passo 5: Testar API

### Fazer uma recomendação

```bash
curl -X POST "http://localhost:8000/recomendar" \
  -H "Content-Type: application/json" \
  -d '{
    "idade": 35,
    "poutcome": "unknown",
    "previous": 1
  }'
```

**Resposta esperada:**
```json
{
  "decision_id": "DECISION_1726779....",
  "arm": "cellular",
  "timestamp": "2026-09-20T14:30:45.123Z"
}
```

### Enviar feedback

```bash
curl -X POST "http://localhost:8000/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "decision_id": "DECISION_1726779....",
    "converteu": true
  }'
```

**Resposta esperada:**
```json
{
  "decision_id": "DECISION_1726779....",
  "arm": "cellular",
  "reward": 1,
  "timestamp": "2026-09-20T14:31:12.456Z"
}
```

### Ver estatísticas

```bash
curl "http://localhost:8000/stats"
```

---

## 📊 Passo 6: Verificar Logs no MLflow

Depois de fazer algumas requisições à API, volte ao MLflow UI:

```
http://localhost:5002/
```

Você verá novos **runs** no experimento `testemlflow`:

```
├─ Run: etapa3_simulacao (original, do notebook)
├─ Run: api_inference (requisição de recomendação)
│  ├─ Tag: decision_id
│  ├─ Tag: arm_selected
│  └─ Métrica: confidence
│
└─ Run: api_feedback (resposta do cliente)
   ├─ Tag: decision_id
   ├─ Métrica: conversion
   └─ Métrica: reward_value
```

---

## 🔗 Integração: Como Tudo se Conecta

### 1. **Notebook treina o modelo**
```python
# Notebook 03
from mabwiser.mab import MAB, LearningPolicy

mab = MAB(
    arms=['cellular', 'telephone'],
    learning_policy=LearningPolicy.ThompsonSampling()
)
mab.fit(decisions=train_decisions, rewards=train_rewards)

# Salva em pickle
with open('bandit_model.pkl', 'wb') as f:
    pickle.dump(mab, f)

# Loga no MLflow
log_notebook_execution(
    notebook_name='03_Baseline_e_Thompson',
    params={...},
    metrics={...},
    artifacts={'resultados': 'bandit_results.csv', ...}
)
```

### 2. **API carrega o modelo**

No arquivo `app/bandit_store.py` (que você já tem):
```python
import pickle
from pathlib import Path

BANDIT_PATH = Path('../data/processed/bank-term-deposit-subscription_eda/bandit_model.pkl')

with BANDIT_PATH.open('rb') as f:
    bandit = pickle.load(f)

# Na startup
@app.on_event("startup")
async def startup_event():
    logger.info(f"Carregado: {BANDIT_PATH}")
    logger.info(f"Modelo: MABWiser ThompsonSampling")
```

### 3. **API faz predição**
```python
@app.post("/recomendar")
def recomendar(contexto: ClienteContexto) -> RecomendacaoResponse:
    # Bandit prediz qual braço escolher
    arm = bandit.predict()  # ← Usa Thompson Sampling
    
    # Log no MLflow
    log_api_inference(
        decision_id=decision_id,
        arm_selected=arm,
        confidence=0.5,
        model_version="thompson_bandit_v1"
    )
    
    return RecomendacaoResponse(arm=arm, ...)
```

### 4. **API aprende com feedback**
```python
@app.post("/feedback")
def feedback(payload: FeedbackRequest) -> FeedbackResponse:
    reward = 1 if payload.converteu else 0
    
    # Thompson Sampling aprende
    bandit.partial_fit(
        decisions=[arm],
        rewards=[reward]
    )
    
    # Log no MLflow
    log_feedback_result(
        decision_id=decision_id,
        arm=arm,
        conversion=bool(reward)
    )
    
    return FeedbackResponse(...)
```

### 5. **MLflow rastreia tudo**
```
testemlflow (Experimento)
├─ etapa3_simulacao (notebook treina)
│  └─ baseline_conversion: 10.44%, thompson_conversion: 13.67%
├─ api_inference (cliente faz requisição)
│  └─ decision_id=XXX, arm=cellular, confidence=0.5
└─ api_feedback (feedback chega)
   └─ decision_id=XXX, conversion=true
```

---

## ✅ Checklist Final

- [ ] MLflow server rodando em http://localhost:5002/
- [ ] Notebook 03 executado com sucesso
- [ ] `bandit_model.pkl` criado em `data/processed/...`
- [ ] Experimento `testemlflow` visível no MLflow UI
- [ ] API iniciada com `uvicorn app.main:app --reload --port 8000`
- [ ] Teste POST /recomendar funcionando
- [ ] Teste POST /feedback funcionando
- [ ] Novo runs aparecem no MLflow UI após requisições

---

## 🎓 Resumo do Fluxo

```
📓 NOTEBOOK 03                   
│  Treina Thompson Sampling
│  Salva: bandit_model.pkl
│  Loga: metrics no MLflow
│
├─→ 📊 MLFLOW (Visualiza)
│   Experimento: testemlflow
│   Métricas: baseline vs thompson
│   Artifacts: resultados.csv
│
├─→ 🚀 API FASTAPI (Produção)
│   Carrega: bandit_model.pkl
│   POST /recomendar → predict()
│   POST /feedback → partial_fit()
│
└─→ 📈 MLFLOW (Monitora)
    Runs: api_inference, api_feedback
    Métricas em tempo real
```

---

## 🐛 Troubleshooting

**Problema**: `bandit_model.pkl não encontrado`
- Solução: Executar notebook 03 completamente até a última célula

**Problema**: `ModuleNotFoundError: No module named 'mabwiser'`
- Solução: `pip install mabwiser`

**Problema**: MLflow não conecta
- Solução: Verificar se `mlflow server` está rodando em outro terminal

**Problema**: API não inicia
- Solução: Verificar se porta 8000 está livre: `lsof -i :8000`

---

## 🚀 Próximos Passos

1. **Executar o fluxo completo** (notebook → API → MLflow)
2. **Notebook 04**: Avaliação e Golden Set
3. **Docker Compose**: Testar com containers
4. **AWS**: Migrar para ECS + RDS + S3 (já documentado)
