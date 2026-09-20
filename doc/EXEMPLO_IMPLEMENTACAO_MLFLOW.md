# 🎯 Exemplo Prático de Implementação MLflow

Este documento mostra **código real e pronto para usar** que integra MLflow no projeto datathon.

## 1️⃣ Importação no App/API

### Arquivo: `app/main.py` - Adicionar no topo

```python
import logging

# ↓ Adicionar estas linhas após imports existentes
from app.mlflow_config import ENVIRONMENT, ENABLE_TRACKING, log_config
from app.mlflow_utils import (
    initialize_mlflow,
    log_api_inference,
    log_feedback_result,
    log_bandit_stats,
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ↓ Adicionar esta linha ANTES da criação da app FastAPI
log_config()

# ... resto do código existente ...

app = FastAPI(...)

# ↓ Adicionar após criar a app
@app.on_event("startup")
async def startup_event():
    """Executado quando a API inicia."""
    logger.info("🚀 API iniciando...")
    initialize_mlflow()  # ← Inicializar MLflow
    logger.info("✅ API pronta!")
```

---

## 2️⃣ Modificar Endpoints de Recomendação

### Antes (código atual):

```python
@app.post("/recomendar")
def recomendar(cliente_contexto: ClienteContexto) -> RecomendacaoResponse:
    recomendacao = bandit_store.recommend(client_context=cliente_contexto.dict())
    
    _log_recommendation(
        decision_id=recomendacao["decision_id"],
        arm=recomendacao["arm"],
        client_context=cliente_contexto.dict()
    )
    
    return RecomendacaoResponse(**recomendacao)
```

### Depois (com MLflow completo):

```python
@app.post("/recomendar")
def recomendar(cliente_contexto: ClienteContexto) -> RecomendacaoResponse:
    """
    Recomenda um canal de contato baseado em Thompson Sampling.
    """
    recomendacao = bandit_store.recommend(client_context=cliente_contexto.dict())
    decision_id = recomendacao["decision_id"]
    arm_selected = recomendacao["arm"]
    
    # Log no MLflow
    log_api_inference(
        decision_id=decision_id,
        arm_selected=arm_selected,
        confidence=0.5,
        client_features=cliente_contexto.dict(),
        model_version="thompson_v1"
    )
    
    logger.info(f"📊 Recomendação: {decision_id} → {arm_selected}")
    return RecomendacaoResponse(**recomendacao)
```

---

## 3️⃣ Modificar Endpoint de Feedback

### Depois:

```python
@app.post("/feedback")
def feedback(feedback: FeedbackRequest) -> FeedbackResponse:
    """Registra resultado de uma decisão anterior."""
    resultado = bandit_store.update_reward(
        decision_id=feedback.decision_id,
        reward=feedback.reward
    )
    
    # Log no MLflow
    log_feedback_result(
        decision_id=feedback.decision_id,
        arm=resultado["arm"],
        conversion=bool(feedback.reward)
    )
    
    logger.info(f"📊 Feedback: {feedback.decision_id} → {'Conversão' if feedback.reward else 'Sem conversão'}")
    return FeedbackResponse(**resultado)
```

---

## 4️⃣ Notebook 03: Setup e Logging

### Célula inicial:

```python
import sys
sys.path.insert(0, '..')

from app.mlflow_config import ENVIRONMENT, initialize_mlflow
from app.mlflow_utils import log_notebook_execution

initialize_mlflow()
print(f"Environment: {ENVIRONMENT} ✅")
```

### Célula final:

```python
run_id = log_notebook_execution(
    notebook_name="03_Baseline_e_Thompson",
    etapa="etapa3_simulacao",
    params={
        "seed": 42,
        "test_size": 0.30,
        "baseline_arm": FIXED_RULE_ARM,
        "algoritmo": "MABWiser ThompsonSampling",
    },
    metrics={
        "baseline_conversion": float(metrics['baseline_conversion']),
        "thompson_conversion": float(metrics['thompson_conversion']),
        "conversion_lift_relative_pct": float(metrics['conversion_lift_relative'] * 100),
    },
    artifacts={
        "resultados": str(RESULTS_PATH),
        "metricas": str(METRICS_PATH),
    }
)
print(f"✅ Logado: {run_id}")
```

---

## 5️⃣ Docker Compose - Environment File

### Arquivo: `deploy/mlflow-config/mlflow.env`

```bash
ENVIRONMENT=local
ENABLE_MLFLOW_TRACKING=true
MLFLOW_TRACKING_URI=http://mlflow:5000
```

---

## ✅ Checklist Rápido

- [ ] Criar `app/mlflow_config.py`
- [ ] Criar `app/mlflow_utils.py`
- [ ] Modificar `app/main.py` (adicionar imports e inicialização)
- [ ] Modificar `/recomendar` para logar inferências
- [ ] Modificar `/feedback` para logar resultados
- [ ] Adicionar setup MLflow em notebook 03
- [ ] Adicionar logging ao final de notebook 03
- [ ] Testar localmente: `docker compose up && jupyter notebook`
- [ ] Verificar MLflow UI em http://localhost:5002
- [ ] Fazer commits!

**Tempo:** 1-2 horas  
**Resultado:** Sistema production-ready com rastreamento completo! 🚀
