"""
Camada de persistência e estado do bandit adaptativo.

Por que isso é necessário para "produtizar" o notebook:
- No notebook, o MAB vive só durante a execução da célula (memória volátil).
- Em produção, o processo da API pode reiniciar (deploy, crash, autoscaling) a
  qualquer momento — se o estado do bandit não for salvo em disco (ou em um
  banco), ele "esquece" tudo que aprendeu e volta à estaca zero a cada restart.
- Cada recomendação feita recebe um `decision_id` e fica registrada com o
  braço escolhido e o contexto do cliente, mas ainda SEM o resultado. O
  endpoint de feedback usa esse `decision_id` para saber qual braço
  recompensar/punir, e então atualiza o bandit. Isso funciona como trilha de
  auditoria (governança/observabilidade pedidas no enunciado): dá para
  reconstruir toda decisão tomada, quando, e o que aconteceu depois.

Dois backends, escolhidos por BANDIT_STORE_BACKEND (default "file"):
- "file" (FileBanditStore): pickle do MAB + JSONL append-only em disco — usado
  local/docker-compose, um único processo.
- "dynamodb" (DynamoDBBanditStore): contadores de sucesso/falha por braço e
  decisões em duas tabelas DynamoDB — usado no deploy AWS (deploy/aws/),
  permite múltiplas réplicas sem estado local. Ver deploy/aws/terraform/dynamodb.tf.

Thompson Sampling aqui é não-contextual (Beta-Bernoulli): o estado real é só
um contador de sucesso/falha por braço, então os dois backends reconstroem o
objeto MAB do MABWiser a partir desses contadores via `_build_mab_from_counts`
(em vez de re-rodar `fit()` sobre todo o histórico a cada chamada).
"""
from __future__ import annotations

import json
import os
import pickle
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
from mabwiser.mab import MAB, LearningPolicy

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

BANDIT_STATE_PATH = DATA_DIR / "bandit_state.pkl"
DECISIONS_LOG_PATH = DATA_DIR / "decisions_log.jsonl"

# Usado apenas se não houver estado salvo ainda: inicializa o bandit com o
# histórico já processado pelo Notebook 2 (mesmo warm start usado no Notebook 3),
# em vez de começar de uma crença totalmente uniforme sobre os braços. Os
# mesmos números são usados para o seed do DynamoDB em
# deploy/aws/terraform/dynamodb.tf — se este CSV mudar, atualize lá também.
ARM_STATS_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "bank-term-deposit-subscription_eda"
    / "arm_stats.csv"
)

ARMS = ["cellular", "telephone"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_mab_from_counts(success: dict, fail: dict) -> MAB:
    """Reconstrói o MAB do MABWiser a partir de contadores agregados por
    braço, sem precisar re-rodar `fit()` sobre todo o histórico de decisões.
    """
    mab = MAB(arms=ARMS, learning_policy=LearningPolicy.ThompsonSampling())
    mab.fit(decisions=ARMS, rewards=[0, 0])  # inicializa as estruturas internas
    mab._imp.arm_to_success_count = {a: int(success.get(a, 0)) for a in ARMS}
    mab._imp.arm_to_fail_count = {a: int(fail.get(a, 0)) for a in ARMS}
    return mab


def _warm_start_counts() -> tuple[dict, dict]:
    """Contadores iniciais (sucesso/falha por braço) a partir do
    `arm_stats.csv` gerado no Notebook 2, ou zerados se o arquivo não existir.
    """
    if not ARM_STATS_PATH.exists():
        return {a: 0 for a in ARMS}, {a: 0 for a in ARMS}

    arm_stats = pd.read_csv(ARM_STATS_PATH)
    success, fail = {}, {}
    for _, row in arm_stats.iterrows():
        arm = row["contact"]
        conversions = int(row["conversions"])
        observations = int(row["observations"])
        success[arm] = conversions
        fail[arm] = observations - conversions
    return success, fail


# ---------------------------------------------------------------------------
# Backend local: pickle do MAB + JSONL append-only em disco.
# ---------------------------------------------------------------------------
class FileBanditStore:
    """Encapsula o MAB persistido em arquivo e o log de decisões pendentes de
    feedback. Usado localmente (um único processo, ex.: docker-compose)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.mab: MAB = self._load_or_create()

    # ------------------------------------------------------------------
    # Ciclo de vida / persistência
    # ------------------------------------------------------------------
    def _load_or_create(self) -> MAB:
        if BANDIT_STATE_PATH.exists():
            with BANDIT_STATE_PATH.open("rb") as f:
                return pickle.load(f)
        return self._create_warm_started_mab()

    def _create_warm_started_mab(self) -> MAB:
        success, fail = _warm_start_counts()
        mab = _build_mab_from_counts(success, fail)
        self._persist(mab)
        return mab

    def _persist(self, mab: Optional[MAB] = None) -> None:
        mab = mab if mab is not None else self.mab
        tmp_path = BANDIT_STATE_PATH.with_suffix(".pkl.tmp")
        with tmp_path.open("wb") as f:
            pickle.dump(mab, f)
        tmp_path.replace(BANDIT_STATE_PATH)  # escrita atômica

    # ------------------------------------------------------------------
    # Decisão (recomendação)
    # ------------------------------------------------------------------
    def recommend(self, client_context: Optional[dict] = None) -> dict:
        with self._lock:
            arm = self.mab.predict()
            decision_id = str(uuid.uuid4())
            entry = {
                "decision_id": decision_id,
                "arm": arm,
                "client_context": client_context or {},
                "decided_at": _now_iso(),
                "reward": None,
                "feedback_at": None,
            }
            with DECISIONS_LOG_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return {"decision_id": decision_id, "arm": arm}

    # ------------------------------------------------------------------
    # Feedback (atualização online)
    # ------------------------------------------------------------------
    def feedback(self, decision_id: str, reward: int) -> dict:
        with self._lock:
            entry, entry_line_index = self._find_decision(decision_id)
            if entry is None:
                raise KeyError(f"decision_id não encontrado: {decision_id}")
            if entry["reward"] is not None:
                raise ValueError(f"decision_id já recebeu feedback: {decision_id}")

            arm = entry["arm"]
            self.mab.partial_fit(decisions=[arm], rewards=[reward])
            self._persist()

            entry["reward"] = reward
            entry["feedback_at"] = _now_iso()
            self._rewrite_decision_line(entry_line_index, entry)

        return {"decision_id": decision_id, "arm": arm, "reward": reward}

    def _find_decision(self, decision_id: str):
        if not DECISIONS_LOG_PATH.exists():
            return None, None
        with DECISIONS_LOG_PATH.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            entry = json.loads(line)
            if entry["decision_id"] == decision_id:
                return entry, i
        return None, None

    def _rewrite_decision_line(self, line_index: int, entry: dict) -> None:
        with DECISIONS_LOG_PATH.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        lines[line_index] = json.dumps(entry, ensure_ascii=False) + "\n"
        with DECISIONS_LOG_PATH.open("w", encoding="utf-8") as f:
            f.writelines(lines)

    # ------------------------------------------------------------------
    # Observabilidade
    # ------------------------------------------------------------------
    def stats(self) -> dict:
        with self._lock:
            success = dict(self.mab._imp.arm_to_success_count)
            fail = dict(self.mab._imp.arm_to_fail_count)
            expectations = self.mab.predict_expectations()

        return _format_stats(success, fail, expectations)


def _format_stats(success: dict, fail: dict, expectations: dict) -> dict:
    arms_stats = {}
    for arm in ARMS:
        s, f_ = int(success.get(arm, 0)), int(fail.get(arm, 0))
        arms_stats[arm] = {
            "observações": s + f_,
            "conversões": s,
            "taxa_de_conversao_estimada": round(float(expectations[arm]), 4),
        }
    return {"braços": arms_stats}


# ---------------------------------------------------------------------------
# Backend AWS: contadores + decisões em duas tabelas DynamoDB.
# ---------------------------------------------------------------------------
class DynamoDBBanditStore:
    """Mesma interface pública de `FileBanditStore`, mas com o estado do
    bandit e o log de decisões em DynamoDB (deploy/aws/terraform/dynamodb.tf).

    Escolhida por ser o padrão de acesso natural para "grava decisão pendente
    -> busca por decision_id -> atualiza com o resultado": get/update por
    chave primária, que o DynamoDB atende nativamente (PutItem/GetItem/
    UpdateItem), diferente de um object store como o S3.
    """

    def __init__(self) -> None:
        import boto3  # import local: só é necessário quando este backend é usado

        region = os.environ["AWS_REGION"]
        self._table_arms = boto3.resource("dynamodb", region_name=region).Table(
            os.environ["DYNAMODB_TABLE_ARMS"]
        )
        self._table_decisions = boto3.resource("dynamodb", region_name=region).Table(
            os.environ["DYNAMODB_TABLE_DECISIONS"]
        )
        self._ensure_seeded()

    def _ensure_seeded(self) -> None:
        """Garante que as duas linhas de `bandit_arms` existem (o Terraform já
        faz esse seed, isso aqui é só uma rede de segurança, ex.: uso do
        backend DynamoDB fora do stack Terraform). `ConditionExpression`
        evita sobrescrever contadores que a aplicação já atualizou — se a
        linha já existir, o put falha e o erro esperado é ignorado."""
        from botocore.exceptions import ClientError

        success, fail = _warm_start_counts()
        for arm in ARMS:
            try:
                self._table_arms.put_item(
                    Item={
                        "arm": arm,
                        "success_count": success.get(arm, 0),
                        "fail_count": fail.get(arm, 0),
                    },
                    ConditionExpression="attribute_not_exists(arm)",
                )
            except ClientError as exc:
                if exc.response["Error"]["Code"] != "ConditionalCheckFailedException":
                    raise

    def _read_counts(self) -> tuple[dict, dict]:
        success, fail = {}, {}
        for arm in ARMS:
            item = self._table_arms.get_item(Key={"arm": arm}).get("Item", {})
            success[arm] = int(item.get("success_count", 0))
            fail[arm] = int(item.get("fail_count", 0))
        return success, fail

    def recommend(self, client_context: Optional[dict] = None) -> dict:
        success, fail = self._read_counts()
        mab = _build_mab_from_counts(success, fail)
        arm = mab.predict()
        decision_id = str(uuid.uuid4())

        item = {
            "decision_id": decision_id,
            "arm": arm,
            "client_context_json": json.dumps(client_context or {}, ensure_ascii=False),
            "decided_at": _now_iso(),
        }
        self._table_decisions.put_item(Item=item)

        return {"decision_id": decision_id, "arm": arm}

    def feedback(self, decision_id: str, reward: int) -> dict:
        from botocore.exceptions import ClientError

        item = self._table_decisions.get_item(Key={"decision_id": decision_id}).get("Item")
        if item is None:
            raise KeyError(f"decision_id não encontrado: {decision_id}")
        if "reward" in item:
            raise ValueError(f"decision_id já recebeu feedback: {decision_id}")

        arm = item["arm"]
        count_field = "success_count" if reward else "fail_count"

        try:
            # UpdateItem atômico: protege contra corrida entre requests
            # concorrentes sem precisar de um lock em memória (que só
            # funcionaria dentro de um único processo/réplica).
            self._table_decisions.update_item(
                Key={"decision_id": decision_id},
                UpdateExpression="SET reward = :r, feedback_at = :t",
                ConditionExpression="attribute_not_exists(reward)",
                ExpressionAttributeValues={":r": reward, ":t": _now_iso()},
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise ValueError(f"decision_id já recebeu feedback: {decision_id}") from exc
            raise

        self._table_arms.update_item(
            Key={"arm": arm},
            UpdateExpression=f"ADD {count_field} :one",
            ExpressionAttributeValues={":one": 1},
        )

        return {"decision_id": decision_id, "arm": arm, "reward": reward}

    def stats(self) -> dict:
        success, fail = self._read_counts()
        mab = _build_mab_from_counts(success, fail)
        expectations = mab.predict_expectations()
        return _format_stats(success, fail, expectations)


# ---------------------------------------------------------------------------
# Factory: escolhe o backend por env var. Sem fallback silencioso para
# "file" se o Dynamo falhar — um erro de configuração/IAM deve propagar no
# startup do container, não mascarar como "funcionando" até o próximo restart.
# ---------------------------------------------------------------------------
def _create_bandit_store():
    backend = os.getenv("BANDIT_STORE_BACKEND", "file")
    if backend == "dynamodb":
        return DynamoDBBanditStore()
    return FileBanditStore()


# Instância única do processo (equivalente a um singleton por worker da API)
bandit_store = _create_bandit_store()
