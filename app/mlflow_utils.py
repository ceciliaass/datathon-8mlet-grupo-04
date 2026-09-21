"""
Utilitários reusáveis para tracking MLflow em notebook e API.
Oferece contextos, decoradores e funções que funcionam em qualquer ambiente.

Uso na API:
    from app.mlflow_utils import initialize_mlflow, log_api_inference
    initialize_mlflow()
    log_api_inference(decision_id="D123", arm_selected="cellular", ...)

Uso em Notebook:
    from app.mlflow_utils import log_notebook_execution
    run_id = log_notebook_execution("03_Baseline_Thompson", "etapa3", params, metrics)
"""
import json
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any
from datetime import datetime

import mlflow

from app.mlflow_config import (
    MLFLOW_TRACKING_URI,
    EXPERIMENT_NAME,
    ENABLE_TRACKING,
    DEFAULT_TAGS,
)

logger = logging.getLogger(__name__)

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

def initialize_mlflow():
    """
    Inicializar MLflow (executar na startup da API ou início do notebook).

    Executa gracefully mesmo se MLflow estiver indisponível.
    """
    if not ENABLE_TRACKING:
        logger.info("❌ MLflow tracking desativado")
        return

    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(EXPERIMENT_NAME)
        logger.info(f"✅ MLflow inicializado em {MLFLOW_TRACKING_URI}")
    except Exception as e:
        logger.warning(f"⚠️  Erro ao inicializar MLflow (continuando sem tracking): {e}")

# ============================================================================
# CONTEXTOS (usar com `with` statements)
# ============================================================================

@contextmanager
def track_run(run_name: str, tags: Optional[Dict[str, str]] = None):
    """
    Context manager para rastrear um run do MLflow.

    Uso:
        with track_run("minha_etapa", tags={"tipo": "predição"}):
            mlflow.log_param("param1", value1)
            mlflow.log_metric("metric1", value1)

    Se MLflow estiver indisponível, ainda assim executa o bloco (graceful degradation).
    """
    if not ENABLE_TRACKING:
        yield None
        return

    try:
        all_tags = {**DEFAULT_TAGS, **(tags or {})}
        with mlflow.start_run(run_name=run_name) as run:
            for key, value in all_tags.items():
                try:
                    mlflow.set_tag(key, str(value))
                except Exception:
                    pass
            logger.debug(f"✅ Run iniciado: {run.info.run_id}")
            yield run
    except Exception as e:
        logger.warning(f"⚠️  Erro ao iniciar run: {e}")
        yield None

# ============================================================================
# FUNÇÕES ESPECÍFICAS PARA O DATATHON
# ============================================================================

def log_notebook_execution(
    notebook_name: str,
    etapa: str,
    params: Dict[str, Any],
    metrics: Dict[str, float],
    artifacts: Optional[Dict[str, str]] = None,
    tags: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """
    Log completo de execução de notebook.

    Args:
        notebook_name: Ex: "03_Baseline_e_Thompson"
        etapa: Ex: "etapa3_simulacao"
        params: Dicionário de parâmetros (seed=42, test_size=0.3, etc)
        metrics: Dicionário de métricas (baseline_conv=0.10, etc)
        artifacts: Dict {nome: caminho} para arquivos a logar
        tags: Tags adicionais para o run

    Returns:
        run_id se sucesso, None se falha

    Uso:
        run_id = log_notebook_execution(
            notebook_name="03_Baseline_e_Thompson",
            etapa="etapa3_simulacao",
            params={"seed": 42, "test_size": 0.3},
            metrics={"baseline_conv": 0.1044, "thompson_conv": 0.1367},
            artifacts={"resultados": "data/processed/results.csv"}
        )
    """
    if not ENABLE_TRACKING:
        logger.info(f"⏭️  MLflow desativado, pulando log de {notebook_name}")
        return None

    run_name = f"{notebook_name}_{etapa}"

    try:
        all_tags = {"notebook": notebook_name, "etapa": etapa}
        if tags:
            all_tags.update(tags)

        with track_run(run_name=run_name, tags=all_tags) as run:
            if run is None:
                return None

            # Log parâmetros
            for key, value in params.items():
                try:
                    if isinstance(value, (int, float, str, bool, type(None))):
                        mlflow.log_param(key, value)
                    else:
                        # Se não for tipo primitivo, converter para string
                        mlflow.log_param(key, str(value)[:100])
                except Exception as e:
                    logger.warning(f"Erro ao logar param {key}: {e}")

            # Log métricas
            for key, value in metrics.items():
                try:
                    mlflow.log_metric(key, float(value))
                except Exception as e:
                    logger.warning(f"Erro ao logar métrica {key}: {e}")

            # Log artefatos
            if artifacts:
                for artifact_name, artifact_path in artifacts.items():
                    try:
                        mlflow.log_artifact(artifact_path)
                        logger.debug(f"✅ Artefato logado: {artifact_name}")
                    except Exception as e:
                        logger.warning(f"⚠️  Erro ao logar artefato {artifact_name}: {e}")

            run_id = run.info.run_id
            logger.info(f"✅ Notebook run logged: {run_id}")
            return run_id
    except Exception as e:
        logger.error(f"❌ Erro ao logar execução do notebook: {e}")
        return None

def log_api_inference(
    decision_id: str,
    arm_selected: str,
    confidence: float,
    client_features: Optional[Dict[str, Any]] = None,
    model_version: Optional[str] = None,
    extra_metrics: Optional[Dict[str, float]] = None
) -> Optional[str]:
    """
    Log de predição/inferência feita pela API.

    Args:
        decision_id: ID único da decisão (ex: "DECISION_12345")
        arm_selected: Braço escolhido ("cellular" ou "telephone")
        confidence: Confiança da predição (0-1)
        client_features: Features do cliente (opcional)
        model_version: Versão do modelo usada (ex: "thompson_v1")
        extra_metrics: Métricas adicionais a logar

    Returns:
        run_id se sucesso, None se falha

    Uso:
        log_api_inference(
            decision_id="DEC_abc123",
            arm_selected="cellular",
            confidence=0.75,
            client_features={"age": 35, "balance": 5000},
            model_version="thompson_v1"
        )
    """
    if not ENABLE_TRACKING:
        return None

    try:
        with track_run("api_inference") as run:
            if run is None:
                return None

            mlflow.set_tag("decision_id", str(decision_id))
            mlflow.set_tag("arm_selected", str(arm_selected))
            if model_version:
                mlflow.set_tag("model_version", str(model_version))

            mlflow.log_param("arm_value", 1 if arm_selected == "cellular" else 0)
            mlflow.log_metric("confidence", float(confidence))

            if client_features:
                try:
                    mlflow.log_dict(client_features, "client_features.json")
                except Exception as e:
                    logger.debug(f"Não foi possível logar client_features: {e}")

            if extra_metrics:
                for key, value in extra_metrics.items():
                    try:
                        mlflow.log_metric(key, float(value))
                    except Exception:
                        pass

            logger.debug(f"✅ Inferência logada: {decision_id} → {arm_selected}")
            return run.info.run_id
    except Exception as e:
        logger.warning(f"⚠️  Erro ao logar predição: {e}")
        return None

def log_feedback_result(
    decision_id: str,
    arm: str,
    conversion: bool,
    delay_seconds: Optional[int] = None,
    extra_metrics: Optional[Dict[str, float]] = None
) -> Optional[str]:
    """
    Log do resultado/feedback de uma decisão.

    Args:
        decision_id: ID da decisão original
        arm: Braço que foi escolhido
        conversion: Se houve conversão (True/False)
        delay_seconds: Tempo entre decisão e feedback (opcional)
        extra_metrics: Métricas adicionais

    Returns:
        run_id se sucesso, None se falha

    Uso:
        log_feedback_result(
            decision_id="DEC_abc123",
            arm="cellular",
            conversion=True,
            delay_seconds=3600
        )
    """
    if not ENABLE_TRACKING:
        return None

    try:
        with track_run("api_feedback") as run:
            if run is None:
                return None

            mlflow.set_tag("decision_id", str(decision_id))
            mlflow.set_tag("arm", str(arm))
            mlflow.set_tag("conversion", "yes" if conversion else "no")

            mlflow.log_param("conversion_observed", int(conversion))
            mlflow.log_metric("conversion", 1.0 if conversion else 0.0)

            if delay_seconds is not None:
                mlflow.log_metric("feedback_delay_seconds", float(delay_seconds))

            if extra_metrics:
                for key, value in extra_metrics.items():
                    try:
                        mlflow.log_metric(key, float(value))
                    except Exception:
                        pass

            logger.debug(f"✅ Feedback logado: {decision_id} → {conversion}")
            return run.info.run_id
    except Exception as e:
        logger.warning(f"⚠️  Erro ao logar feedback: {e}")
        return None

def log_bandit_stats(
    arm_stats: Dict[str, Dict[str, int]],
    timestamp: Optional[str] = None
) -> Optional[str]:
    """
    Log das estatísticas atualizadas do Thompson Sampling.

    Args:
        arm_stats: {
            "cellular": {"trials": 100, "wins": 15},
            "telephone": {"trials": 50, "wins": 4}
        }
        timestamp: Quando as stats foram coletadas (ISO format)

    Returns:
        run_id se sucesso, None se falha

    Uso:
        log_bandit_stats({
            "cellular": {"trials": 100, "wins": 15},
            "telephone": {"trials": 50, "wins": 4}
        })
    """
    if not ENABLE_TRACKING:
        return None

    try:
        with track_run("bandit_stats") as run:
            if run is None:
                return None

            if timestamp:
                mlflow.set_tag("collected_at", timestamp)

            for arm, stats in arm_stats.items():
                trials = float(stats.get("trials", 0))
                wins = float(stats.get("wins", 0))
                rate = wins / trials if trials > 0 else 0.0

                mlflow.log_metric(f"{arm}_trials", trials)
                mlflow.log_metric(f"{arm}_wins", wins)
                mlflow.log_metric(f"{arm}_rate", rate)

            logger.debug(f"✅ Bandit stats logado")
            return run.info.run_id
    except Exception as e:
        logger.warning(f"⚠️  Erro ao logar stats do bandit: {e}")
        return None

def log_model_registration(
    model_name: str,
    model_version: str,
    description: str = "",
    tags: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """
    Log de registro de modelo (for tracking model lifecycle).

    Args:
        model_name: Ex: "thompson_bandit_v1"
        model_version: Ex: "1.0"
        description: Descrição do modelo
        tags: Tags do modelo

    Returns:
        run_id se sucesso
    """
    if not ENABLE_TRACKING:
        return None

    try:
        all_tags = {"model_name": model_name, "model_version": model_version}
        if tags:
            all_tags.update(tags)

        with track_run("model_registration", tags=all_tags) as run:
            if run is None:
                return None

            mlflow.log_param("description", description[:500])
            logger.info(f"✅ Model registration logada: {model_name} v{model_version}")
            return run.info.run_id
    except Exception as e:
        logger.warning(f"⚠️  Erro ao logar model registration: {e}")
        return None


if __name__ == "__main__":
    # Teste local
    logging.basicConfig(level=logging.DEBUG)
    initialize_mlflow()

    # Simular notebook
    run_id = log_notebook_execution(
        notebook_name="test_notebook",
        etapa="test_etapa",
        params={"seed": 42, "test": "value"},
        metrics={"metric1": 0.5, "metric2": 0.8}
    )
    print(f"✅ Test run: {run_id}")
