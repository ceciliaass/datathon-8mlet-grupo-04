from typing import Optional

from pydantic import BaseModel, Field


class ClienteContexto(BaseModel):
    """Campos do cliente, opcionais. Hoje servem para log/auditoria; o próximo
    passo natural (ver README) é usá-los para tornar o bandit contextual."""

    idade: Optional[int] = Field(default=None, description="Idade do cliente")
    poutcome: Optional[str] = Field(
        default=None, description="Resultado da campanha anterior (failure/success/other/unknown)"
    )
    previous: Optional[int] = Field(
        default=None, description="Número de contatos anteriores a esta campanha"
    )


class RecomendacaoResponse(BaseModel):
    decision_id: str
    arm: str


class FeedbackRequest(BaseModel):
    decision_id: str = Field(..., description="ID retornado por /recomendar")
    converteu: bool = Field(..., description="Se o cliente converteu (True) ou não (False)")


class FeedbackResponse(BaseModel):
    decision_id: str
    arm: str
    reward: int
