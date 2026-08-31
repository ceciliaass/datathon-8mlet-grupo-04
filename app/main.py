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
from fastapi import FastAPI, HTTPException

from app.bandit_store import bandit_store
from app.schemas import (
    ClienteContexto,
    FeedbackRequest,
    FeedbackResponse,
    RecomendacaoResponse,
)

app = FastAPI(
    title="Bandit Adaptativo - Canal de Contato",
    description=(
        "Serviço de decisão adaptativa (Thompson Sampling) para escolher o "
        "canal de contato (cellular/telephone) por cliente, com aprendizado "
        "online a partir do feedback observado."
    ),
    version="1.0.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/recomendar", response_model=RecomendacaoResponse)
def recomendar(contexto: ClienteContexto | None = None) -> RecomendacaoResponse:
    """Recomenda o canal de contato para um cliente e registra a decisão.

    O contexto do cliente é opcional nesta versão (o bandit ainda não é
    contextual) -- é aceito e logado para auditoria e para permitir evoluir
    para uma versão contextual (LinTS/LinUCB) sem quebrar a API.
    """
    contexto_dict = contexto.model_dump() if contexto else None
    resultado = bandit_store.recommend(client_context=contexto_dict)
    return RecomendacaoResponse(**resultado)


@app.post("/feedback", response_model=FeedbackResponse)
def feedback(payload: FeedbackRequest) -> FeedbackResponse:
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

    return FeedbackResponse(**resultado)


@app.get("/stats")
def stats() -> dict:
    """Estado atual do bandit -- observabilidade para monitorar o aprendizado."""
    return bandit_store.stats()
