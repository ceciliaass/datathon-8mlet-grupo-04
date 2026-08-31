"""
Camada de persistência e estado do bandit adaptativo.

Por que isso é necessário para "produtizar" o notebook:
- No notebook, o MAB vive só durante a execução da célula (memória volátil).
- Em produção, o processo da API pode reiniciar (deploy, crash, autoscaling) a
  qualquer momento — se o estado do bandit não for salvo em disco (ou em um
  banco), ele "esquece" tudo que aprendeu e volta à estaca zero a cada restart.
- Aqui, o MAB (MABWiser) é serializado via pickle para um arquivo após cada
  atualização, e recarregado desse arquivo na inicialização do processo.
- Cada recomendação feita recebe um `decision_id` e fica registrada em um log
  (JSONL, append-only) com o braço escolhido e o contexto do cliente, mas
  ainda SEM o resultado. O endpoint de feedback usa esse `decision_id` para
  saber qual braço recompensar/punir, e então atualiza o bandit.
- O log JSONL funciona como trilha de auditoria (governança/observabilidade
  pedidas no enunciado): dá para reconstruir toda decisão tomada, quando, e
  o que aconteceu depois.
"""
from __future__ import annotations

import json
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
# em vez de começar de uma crença totalmente uniforme sobre os braços.
ARM_STATS_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "processed"
    / "bank-term-deposit-subscription_eda"
    / "arm_stats.csv"
)

ARMS = ["cellular", "telephone"]

_lock = threading.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BanditStore:
    """Encapsula o MAB persistido e o log de decisões pendentes de feedback."""

    def __init__(self) -> None:
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
        mab = MAB(arms=ARMS, learning_policy=LearningPolicy.ThompsonSampling())

        if ARM_STATS_PATH.exists():
            arm_stats = pd.read_csv(ARM_STATS_PATH)
            decisions, rewards = [], []
            for _, row in arm_stats.iterrows():
                arm = row["contact"]
                conversions = int(row["conversions"])
                observations = int(row["observations"])
                decisions += [arm] * conversions + [arm] * (observations - conversions)
                rewards += [1] * conversions + [0] * (observations - conversions)
            mab.fit(decisions=decisions, rewards=rewards)
        else:
            # Sem histórico disponível: começa sem viés nenhum entre os braços.
            mab.fit(decisions=ARMS, rewards=[0, 0])

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
        with _lock:
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
        with _lock:
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
        with _lock:
            success = dict(self.mab._imp.arm_to_success_count)
            fail = dict(self.mab._imp.arm_to_fail_count)
            expectations = self.mab.predict_expectations()

        arms_stats = {}
        for arm in ARMS:
            s, f_ = int(success.get(arm, 0)), int(fail.get(arm, 0))
            arms_stats[arm] = {
                "observações": s + f_,
                "conversões": s,
                "taxa_de_conversao_estimada": round(float(expectations[arm]), 4),
            }
        return {"braços": arms_stats}


# Instância única do processo (equivalente a um singleton por worker da API)
bandit_store = BanditStore()
