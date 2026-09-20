#!/usr/bin/env python3
"""
🚀 MLflow Demo Script - Fluxo Completo Simulado

Este script mostra EXATAMENTE o que acontece quando você:
1. Treina um modelo no notebook
2. Registra no MLflow
3. API carrega o modelo
4. Cliente faz predição
5. Feedback é registrado

Execute este script para entender o fluxo end-to-end!

Pré-requisitos:
    pip install mlflow scikit-learn

Como rodar:
    python doc/mlflow_demo_script.py
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict

# MLflow imports
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

# Sklearn imports
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder

import pickle
import tempfile

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

MLFLOW_BACKEND = "sqlite:///mlflow.db"
MLFLOW_ARTIFACTS = "./mlruns"
MLFLOW_SERVER_URI = "http://localhost:5000"

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title: str):
    """Imprimir seção com destaque"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.ENDC}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")

# ============================================================================
# FASE 1: TREINAR MODELO E LOGAR NO MLFLOW
# ============================================================================

def fase_1_treinar_modelo():
    """FASE 1: Simulate notebook running mlflow.start_run()"""
    print_section("FASE 1️⃣: TREINAR MODELO E LOGAR NO MLFLOW")
    print_info("Simulando: notebooks/03_Baseline_e_Thompson.ipynb")
    print()

    # Configurar MLflow
    mlflow.set_tracking_uri(f"sqlite:///{os.getcwd()}/mlflow.db")
    mlflow.set_artifact_root(os.path.join(os.getcwd(), "mlruns"))

    # Carregar dados
    print_info("Carregando dados (Iris dataset)...")
    iris = load_iris()
    X = iris.data
    y = iris.target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print_success(f"Dados carregados: {X_train.shape[0]} amostras treino, {X_test.shape[0]} teste")
    print()

    # BASELINE
    print_info("Treinar BASELINE (árvore simples)...")
    with mlflow.start_run(run_name="baseline_simples"):
        print_info("  mlflow.start_run(run_name='baseline_simples')")

        # Treinar
        baseline_model = RandomForestClassifier(n_estimators=10, random_state=42)
        baseline_model.fit(X_train, y_train)

        # Métricas
        baseline_pred = baseline_model.predict(X_test)
        baseline_acc = accuracy_score(y_test, baseline_pred)

        # Log no MLflow
        mlflow.log_param("model_type", "baseline")
        mlflow.log_param("n_estimators", 10)
        mlflow.log_param("random_state", 42)
        print_info("  mlflow.log_param('model_type', 'baseline')")
        print_info("  mlflow.log_param('n_estimators', 10)")

        mlflow.log_metric("accuracy", baseline_acc)
        print_info(f"  mlflow.log_metric('accuracy', {baseline_acc:.4f})")

        mlflow.sklearn.log_model(baseline_model, "model")
        print_info("  mlflow.sklearn.log_model(baseline_model, 'model')")

        baseline_run_id = mlflow.active_run().info.run_id
        print_success(f"Baseline treinado! Run ID: {baseline_run_id[:8]}...")
        print()

    # MODELO AVANÇADO (Thompson Sampling simulado)
    print_info("Treinar MODELO AVANÇADO (mais estimadores)...")
    with mlflow.start_run(run_name="thompson_sampling_v1"):
        print_info("  mlflow.start_run(run_name='thompson_sampling_v1')")

        # Treinar
        advanced_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        advanced_model.fit(X_train, y_train)

        # Métricas
        advanced_pred = advanced_model.predict(X_test)
        advanced_acc = accuracy_score(y_test, advanced_pred)

        improvement = ((advanced_acc - baseline_acc) / baseline_acc) * 100

        # Log no MLflow
        mlflow.log_param("model_type", "advanced_thompson_like")
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("max_depth", 10)
        mlflow.log_param("algorithm", "Thompson Sampling (simulated)")
        print_info("  mlflow.log_param(...)")

        mlflow.log_metric("accuracy", advanced_acc)
        mlflow.log_metric("improvement_vs_baseline_pct", improvement)
        print_info(f"  mlflow.log_metric('accuracy', {advanced_acc:.4f})")
        print_info(f"  mlflow.log_metric('improvement_vs_baseline_pct', {improvement:.2f})")

        # Tags
        mlflow.set_tag("best_model", "true")
        mlflow.set_tag("ready_for_production", "true")
        mlflow.set_tag("version", "v1.0")
        print_info("  mlflow.set_tag('best_model', 'true')")
        print_info("  mlflow.set_tag('ready_for_production', 'true')")

        # Log artifacts
        mlflow.sklearn.log_model(advanced_model, "model")
        print_info("  mlflow.sklearn.log_model(advanced_model, 'model')")

        advanced_run_id = mlflow.active_run().info.run_id
        print_success(f"Modelo avançado treinado! Run ID: {advanced_run_id[:8]}...")
        print_success(f"📈 Melhoria: +{improvement:.2f}% em relação ao baseline")
        print()

    return advanced_run_id, advanced_model, advanced_acc

# ============================================================================
# FASE 2: REGISTRAR MODELO NO MLFLOW
# ============================================================================

def fase_2_registrar_modelo(run_id: str):
    """FASE 2: Register model na MLflow Model Registry"""
    print_section("FASE 2️⃣: REGISTRAR MODELO NO MLFLOW MODEL REGISTRY")

    client = MlflowClient(tracking_uri=f"sqlite:///{os.getcwd()}/mlflow.db")

    print_info("Registrando modelo na Model Registry...")
    print_info(f"  model_uri = 'runs:/{run_id}/model'")

    try:
        # Registrar modelo
        result = mlflow.register_model(
            model_uri=f"runs:/{run_id}/model",
            name="iris_classifier"
        )
        print_success(f"Modelo registrado!")
        print_success(f"  Nome: iris_classifier")
        print_success(f"  Versão: {result.version}")
        print()

        return result.version
    except Exception as e:
        # Pode já existir
        print_warning(f"Modelo 'iris_classifier' já existe (normal)")
        versions = client.get_latest_versions("iris_classifier")
        if versions:
            print_success(f"  Versão mais recente: {versions[0].version}")
            print()
            return int(versions[0].version)
        else:
            raise

# ============================================================================
# FASE 3: PROMOVER PARA PRODUCTION
# ============================================================================

def fase_3_promover_production(model_name: str, version: int):
    """FASE 3: Move model to Production stage"""
    print_section("FASE 3️⃣: PROMOVER MODELO PARA PRODUCTION")

    client = MlflowClient(tracking_uri=f"sqlite:///{os.getcwd()}/mlflow.db")

    print_info(f"Mudando stage do modelo...")
    print_info(f"  Nome: {model_name}")
    print_info(f"  Versão: {version}")
    print_info(f"  Stage: None → Production")

    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage="Production"
    )

    print_success(f"Modelo promovido para Production!")
    print()

    # Verificar
    model_version = client.get_model_version(model_name, version)
    print_info(f"Estado atual:")
    print_info(f"  Stage: {model_version.current_stage}")
    print()

# ============================================================================
# FASE 4: API CARREGA MODELO
# ============================================================================

def fase_4_api_carrega_modelo(model_name: str):
    """FASE 4: Simulate API loading model on startup"""
    print_section("FASE 4️⃣: API CARREGA MODELO (Simulated)")

    client = MlflowClient(tracking_uri=f"sqlite:///{os.getcwd()}/mlflow.db")

    print_info("Simulando: @app.on_event('startup')")
    print()

    # Procurar modelo em Production
    print_info("Procurando modelo em stage 'Production'...")
    versions = client.get_latest_versions(
        name=model_name,
        stages=["Production"]
    )

    if not versions:
        print_error(f"Nenhum modelo em Production encontrado!")
        return None

    prod_version = versions[0]
    print_success(f"Encontrado: {model_name} v{prod_version.version}")
    print()

    # Carregar modelo
    print_info("Carregando modelo em memória...")
    print_info(f"  model_uri = 'models:/{model_name}/Production'")

    model = mlflow.sklearn.load_model(f"models:/{model_name}/Production")

    print_success(f"Modelo carregado em memória!")
    print_info(f"  Tipo: {type(model).__name__}")
    print_info(f"  Versão do modelo: {prod_version.version}")
    print()

    return model, prod_version.version

# ============================================================================
# FASE 5: FAZER PREDIÇÃO
# ============================================================================

def fase_5_fazer_predicao(model, model_version: int, X_test):
    """FASE 5: API receives request and makes prediction"""
    print_section("FASE 5️⃣: API RECEBE REQUISIÇÃO E FAZ PREDIÇÃO")

    # Pegar primeira amostra
    sample_idx = 0
    sample = X_test[sample_idx:sample_idx+1]

    print_info("Requisição recebida: POST /recomendar")
    print_info(f"  Sample: {sample[0][:2]}... (primeiros 2 features)")
    print()

    # Fazer predição
    print_info("Processamento:")
    print_info("  1. Validar input")
    print_info("  2. Extrair features")

    prediction = model.predict(sample)[0]
    proba = model.predict_proba(sample)[0]
    confidence = max(proba)

    print_info("  3. Prever")
    print_success(f"  Predição: classe {prediction}")
    print_success(f"  Confiança: {confidence:.2%}")
    print()

    # Log no MLflow
    print_info("Log no MLflow:")
    with mlflow.start_run(run_name="production_inference"):
        mlflow.log_param("model_version", model_version)
        mlflow.log_metric("predicted_class", prediction)
        mlflow.log_metric("confidence", confidence)
        print_info("  mlflow.log_param('model_version', {})".format(model_version))
        print_info(f"  mlflow.log_metric('predicted_class', {prediction})")
        print_info(f"  mlflow.log_metric('confidence', {confidence:.4f})")
        inference_run_id = mlflow.active_run().info.run_id

    print_success(f"Métrica registrada no MLflow! Run ID: {inference_run_id[:8]}...")
    print()

    return prediction, inference_run_id

# ============================================================================
# FASE 6: FEEDBACK
# ============================================================================

def fase_6_feedback(prediction: int):
    """FASE 6: Client sends feedback"""
    print_section("FASE 6️⃣: CLIENTE ENVIA FEEDBACK")

    # Simular feedback (acertou ou errou)
    actual_result = 1  # Suponha que acertou

    print_info("Requisição recebida: POST /feedback")
    print_info(f"  Predição: classe {prediction}")
    print_info(f"  Resultado real: classe {actual_result}")

    if prediction == actual_result:
        print_success("  Status: ✅ ACERTO")
        conversion = 1
    else:
        print_warning("  Status: ❌ ERRO")
        conversion = 0

    print()

    # Log no MLflow
    print_info("Log no MLflow:")
    with mlflow.start_run(run_name="production_feedback"):
        mlflow.log_metric("conversion", conversion)
        mlflow.log_metric("correct_prediction", 1 if conversion else 0)
        print_info(f"  mlflow.log_metric('conversion', {conversion})")
        print_info(f"  mlflow.log_metric('correct_prediction', {conversion})")
        feedback_run_id = mlflow.active_run().info.run_id

    print_success(f"Feedback registrado no MLflow! Run ID: {feedback_run_id[:8]}...")
    print()

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Executar demo completo"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         🎯 MLflow Demo - Fluxo Completo End-to-End                ║")
    print("║                                                                    ║")
    print("║  1. Treinar modelo no notebook                                    ║")
    print("║  2. Registrar no MLflow Model Registry                            ║")
    print("║  3. Promover para Production                                      ║")
    print("║  4. API carrega modelo                                            ║")
    print("║  5. Cliente faz predição                                          ║")
    print("║  6. Feedback é registrado                                         ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

    try:
        # Fase 1
        run_id, model, accuracy = fase_1_treinar_modelo()

        # Fase 2
        version = fase_2_registrar_modelo(run_id)

        # Fase 3
        fase_3_promover_production("iris_classifier", version)

        # Fase 4
        loaded_model, model_version = fase_4_api_carrega_modelo("iris_classifier")
        if loaded_model is None:
            return

        # Preparar dados para fase 5
        iris = load_iris()
        X = iris.data
        y = iris.target
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Fase 5
        prediction, inference_run_id = fase_5_fazer_predicao(loaded_model, model_version, X_test)

        # Fase 6
        fase_6_feedback(prediction)

        # Resumo final
        print_section("✅ DEMO COMPLETO!")
        print_success("Fluxo end-to-end executado com sucesso!")
        print()
        print(f"{Colors.BOLD}Próximos passos:{Colors.ENDC}")
        print(f"  1. Abrir MLflow UI: http://localhost:5000/")
        print(f"  2. Ver os runs criados em tempo real")
        print(f"  3. Comparar baseline vs modelo avançado")
        print(f"  4. Ver logs de inferência e feedback")
        print()
        print(f"{Colors.BOLD}Arquivos criados:{Colors.ENDC}")
        print(f"  📁 ./mlruns/           - Artifacts do MLflow")
        print(f"  💾 ./mlflow.db         - Backend SQLite")
        print()

    except Exception as e:
        print_error(f"Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
