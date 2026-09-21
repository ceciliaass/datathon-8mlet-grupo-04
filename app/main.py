"""
Etapa 5 do Datathon: serviço que recebe dados do cliente e retorna a oferta
(canal) recomendada, e que APRENDE de verdade com o resultado observado.

Diferença central para o notebook:
    notebook  -> simula uma sequência de decisões e recompensas de uma vez só,
                 tudo dentro da mesma execução da célula.
    este serviço -> cada decisão é um evento independente no tempo; a
                 recompensa (conversão) só é conhecida depois (a ligação
                 aconteceu, o cliente respondeu ou não) e chega em uma
                 chamada HTTP separada, possivelmente minutos/horas depois,
                 possivelmente vinda de outro sistema (ex.: callback do
                 discador, evento de CRM). O estado do bandit precisa
                 sobreviver entre essas duas chamadas e entre reinícios do
                 processo -- é isso que o bandit_store.py resolve.

Rodar localmente:
    uvicorn app.main:app --reload --port 8000

Fluxo de uso:
    1) POST /recomendar        -> {"decision_id": "...", "arm": "cellular"}
    2) (tempo depois, callback real do canal)
       POST /feedback          -> atualiza o bandit com o resultado
    3) GET  /stats             -> acompanha a crença atual por braço
"""
import os
import logging

import mlflow
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import RedirectResponse

from app.bandit_store import bandit_store
from app.schemas import (
    ClienteContexto,
    FeedbackRequest,
    FeedbackResponse,
    RecomendacaoResponse,
)
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
log_config()

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5002")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
try:
    # Chamada de rede na inicialização do processo: se o MLflow ainda não
    # estiver de pé (ex.: os dois serviços sobem juntos no ECS e o MLflow
    # demora mais a ficar saudável), isso não pode derrubar a API — o
    # tracking é melhor-esforço (ver _log_recommendation/_log_feedback).
    mlflow.set_experiment("model-production")
except Exception:
    pass

# Gera uma recomendação de exemplo para popular os exemplos da documentação
# (permite que o botão "Try it out" em /docs use um `decision_id` válido).
_example = bandit_store.recommend(client_context={"example": True})
EXAMPLE_DECISION_ID = _example["decision_id"]


def _log_recommendation(decision_id: str, arm: str, client_context: dict | None) -> None:
    try:
        with mlflow.start_run(run_name="recomendacao") as _run:
            mlflow.set_tag("decision_id", decision_id)
            mlflow.set_tag("arm", arm)
            mlflow.log_param("selected_arm", arm)
            mlflow.log_param("client_context_present", bool(client_context))
            if client_context:
                mlflow.log_dict(client_context, "client_context.json")
    except Exception:
        # Falha do MLflow não deve quebrar a request da API; o bandit continua
        # funcionando e o tracking pode ser refeito em outra execução do ambiente.
        pass


def _log_feedback(decision_id: str, arm: str, reward: int) -> None:
    try:
        with mlflow.start_run(run_name="feedback") as _run:
            mlflow.set_tag("decision_id", decision_id)
            mlflow.set_tag("arm", arm)
            mlflow.log_param("reward", reward)
            mlflow.log_metric("conversion_observed", float(reward))
    except Exception:
        pass


app = FastAPI(
    title="Bandit Adaptativo - Canal de Contato",
    description=(
        "Serviço de decisão adaptativa (Thompson Sampling) para escolher o "
        "canal de contato (cellular/telephone) por cliente, com aprendizado "
        "online a partir do feedback observado."
    ),
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """Executado quando a API inicia."""
    logger.info("🚀 API iniciando...")
    initialize_mlflow()
    logger.info("✅ API pronta!")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/recomendar", response_model=RecomendacaoResponse)
def recomendar(contexto: ClienteContexto | None = Body(
    None,
    example={"idade": 35, "poutcome": "unknown", "previous": 1},
),) -> RecomendacaoResponse:
    """Recomenda o canal de contato para um cliente e registra a decisão.

    O contexto do cliente é opcional nesta versão (o bandit ainda não é
    contextual) -- é aceito e logado para auditoria e para permitir evoluir
    para uma versão contextual (LinTS/LinUCB) sem quebrar a API.
    """
    contexto_dict = contexto.model_dump() if contexto else None
    resultado = bandit_store.recommend(client_context=contexto_dict)

    decision_id = resultado["decision_id"]
    arm_selected = resultado["arm"]

    # Log tradicional (manter para compatibilidade)
    _log_recommendation(
        decision_id=decision_id,
        arm=arm_selected,
        client_context=contexto_dict,
    )

    # Log enriquecido no MLflow
    log_api_inference(
        decision_id=decision_id,
        arm_selected=arm_selected,
        confidence=0.5,
        client_features=contexto_dict or {},
        model_version="thompson_v1"
    )

    logger.info(f"📊 Recomendação: {decision_id} → {arm_selected}")
    return RecomendacaoResponse(**resultado)


@app.post("/feedback", response_model=FeedbackResponse)
def feedback(payload: FeedbackRequest = Body(
    ...,
    example={"decision_id": EXAMPLE_DECISION_ID, "converteu": True},
)) -> FeedbackResponse:
    """Registra o resultado real de uma recomendação e atualiza o bandit.

    Deve ser chamado assim que o desfecho da interação for conhecido (ex.:
    a ligação terminou e sabemos se o cliente contratou o produto ou não).
    """
    try:
        resultado = bandit_store.feedback(
            decision_id=payload.decision_id,
            reward=int(payload.converteu),
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    # Log tradicional
    _log_feedback(
        decision_id=resultado["decision_id"],
        arm=resultado["arm"],
        reward=resultado["reward"],
    )

    # Log enriquecido no MLflow
    log_feedback_result(
        decision_id=resultado["decision_id"],
        arm=resultado["arm"],
        conversion=bool(resultado["reward"]),
        extra_metrics={
            "reward_value": float(resultado["reward"]),
        }
    )

    status = "✅ Conversão" if resultado["reward"] else "❌ Sem conversão"
    logger.info(f"📊 Feedback: {resultado['decision_id']} → {status}")
    return FeedbackResponse(**resultado)


@app.get("/stats")
def stats() -> dict:
    """Estado atual do bandit -- observabilidade para monitorar o aprendizado."""
    return bandit_store.stats()
