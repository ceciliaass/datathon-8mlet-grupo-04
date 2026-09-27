#!/bin/bash

################################################################################
# Migrar MLflow Local (SQLite) -> AWS RDS PostgreSQL
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[⚠️]${NC} $1"; }

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_DIR="${PROJECT_ROOT}/deploy"

# RDS Credentials — nunca hardcode a senha aqui.
# Exporte RDS_PASSWORD (ex.: `export RDS_PASSWORD=$(aws secretsmanager get-secret-value ...)`)
# antes de rodar este script.
RDS_HOST="${RDS_HOST:-datathon-bandit-mlflow-db.ch6eci8sykpe.us-east-2.rds.amazonaws.com}"
RDS_PORT="${RDS_PORT:-5432}"
RDS_DB="${RDS_DB:-mlflow}"
RDS_USER="${RDS_USER:-mlflow_admin}"
RDS_PASS="${RDS_PASSWORD:?Defina a env var RDS_PASSWORD antes de rodar este script}"
BACKEND_STORE_URI="postgresql://${RDS_USER}:${RDS_PASS}@${RDS_HOST}:${RDS_PORT}/${RDS_DB}"

log_info "=== Migrando MLflow: SQLite Local -> AWS RDS ==="
log_info "RDS Endpoint: ${RDS_HOST}"

# Step 1: Fazer backup do banco local
log_info "PASSO 1: Backup do banco SQLite local..."
BACKUP_DIR="${PROJECT_ROOT}/.mlflow-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "${BACKUP_DIR}"

cd "${PROJECT_ROOT}"
docker exec datathon_mlflow sqlite3 /tmp/mlflow.db ".dump" > "${BACKUP_DIR}/mlflow_dump.sql"
log_success "Backup salvo em: ${BACKUP_DIR}/mlflow_dump.sql"

# Step 2: Exportar dados em JSON para facilitar re-import
log_info "PASSO 2: Exportando experimentos e runs..."

EXPORT_SCRIPT="
import mlflow
from mlflow.tracking import MlflowClient
import json
import os

os.makedirs('/tmp/mlflow_export', exist_ok=True)
client = MlflowClient('http://localhost:5000')

# Listar todos os experimentos
experiments = client.search_experiments()

export_data = {}
for exp in experiments:
    print(f'Exportando experimento: {exp.name} (ID: {exp.experiment_id})')

    # Buscar todos os runs deste experimento
    runs = client.search_runs(experiment_ids=[exp.experiment_id])

    export_data[exp.name] = {
        'experiment_id': exp.experiment_id,
        'runs': []
    }

    for run in runs:
        print(f'  Run: {run.info.run_id}')
        run_data = {
            'run_id': run.info.run_id,
            'status': run.info.status,
            'params': run.data.params,
            'metrics': dict(run.data.metrics),
            'tags': run.data.tags,
        }
        export_data[exp.name]['runs'].append(run_data)

# Salvar em JSON
with open('/tmp/mlflow_export/experiments.json', 'w') as f:
    json.dump(export_data, f, indent=2)

print(f'✓ Exportados {len(experiments)} experimentos')
"

docker exec datathon_mlflow python3 << 'EOF'
import mlflow
from mlflow.tracking import MlflowClient
import json
import os

os.makedirs('/tmp/mlflow_export', exist_ok=True)
client = MlflowClient('http://localhost:5000')

# Listar todos os experimentos
experiments = client.search_experiments()

export_data = {}
for exp in experiments:
    print(f'Exportando experimento: {exp.name} (ID: {exp.experiment_id})')

    # Buscar todos os runs deste experimento
    runs = client.search_runs(experiment_ids=[exp.experiment_id])

    export_data[exp.name] = {
        'experiment_id': exp.experiment_id,
        'runs': []
    }

    for run in runs:
        print(f'  Run: {run.info.run_id}')
        run_data = {
            'run_id': run.info.run_id,
            'status': run.info.status,
            'params': run.data.params,
            'metrics': dict(run.data.metrics),
            'tags': run.data.tags,
        }
        export_data[exp.name]['runs'].append(run_data)

# Salvar em JSON
with open('/tmp/mlflow_export/experiments.json', 'w') as f:
    json.dump(export_data, f, indent=2)

print(f'✓ Exportados {len(experiments)} experimentos')
EOF

# Copiar arquivo exportado
docker cp datathon_mlflow:/tmp/mlflow_export/experiments.json "${BACKUP_DIR}/"
log_success "Experimentos exportados"

# Step 3: Parar e remover MLflow local
log_info "PASSO 3: Parando MLflow local..."
docker stop datathon_mlflow || true
sleep 2
log_success "MLflow parado"

# Step 4: Criar docker-compose com RDS
log_info "PASSO 4: Atualizando docker-compose para usar RDS..."

# Nota: heredoc com delimitador entre aspas ('DOCKER_COMPOSE') para NAO expandir
# variaveis aqui — a senha nunca e escrita em disco. Quem resolve ${RDS_USER}
# etc. e o proprio `docker compose` (client-side), lendo do ambiente do processo
# no momento do `up`, usando as env vars ja exportadas acima neste script.
export RDS_HOST RDS_PORT RDS_DB RDS_USER
export RDS_PASSWORD="${RDS_PASS}"

cat > "${DEPLOY_DIR}/docker-compose-rds.yml" << 'DOCKER_COMPOSE'
services:
  mlflow:
    image: python:3.11-slim
    container_name: datathon_mlflow_rds
    ports:
      - "5002:5000"
    networks:
      - datathon_net
    working_dir: /tmp
    environment:
      - MLFLOW_BACKEND_STORE_URI=postgresql://${RDS_USER}:${RDS_PASSWORD}@${RDS_HOST}:${RDS_PORT}/${RDS_DB}
      - MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://datathon-bandit-data-799823514976/mlflow-artifacts
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    entrypoint: >
      sh -c "
      pip install mlflow==3.15.1 boto3 psycopg2-binary --quiet &&
      mlflow server
        --host 0.0.0.0
        --port 5000
        --backend-store-uri $$MLFLOW_BACKEND_STORE_URI
        --default-artifact-root $$MLFLOW_DEFAULT_ARTIFACT_ROOT
      "

  fastapi:
    image: deploy-fastapi
    container_name: datathon_fastapi
    ports:
      - "8000:8000"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - ENVIRONMENT=local
    depends_on:
      - mlflow
    networks:
      - datathon_net

networks:
  datathon_net:
    driver: bridge
DOCKER_COMPOSE

log_success "docker-compose atualizado para usar RDS"

# Step 5: Iniciar MLflow com RDS
log_info "PASSO 5: Iniciando MLflow com RDS..."
docker compose -f "${DEPLOY_DIR}/docker-compose-rds.yml" up -d mlflow

sleep 15
log_success "MLflow com RDS iniciado"

# Step 6: Re-importar dados
log_info "PASSO 6: Re-importando experimentos no RDS..."

docker cp "${BACKUP_DIR}/experiments.json" datathon_mlflow_rds:/tmp/

docker exec datathon_mlflow_rds python3 << 'EOF'
import mlflow
import json

mlflow.set_tracking_uri('http://localhost:5000')

with open('/tmp/experiments.json', 'r') as f:
    experiments = json.load(f)

for exp_name, exp_data in experiments.items():
    print(f'Re-criando experimento: {exp_name}')
    try:
        exp_id = mlflow.create_experiment(exp_name)
        print(f'  ✓ Experimento criado com ID: {exp_id}')
    except:
        # Experimento pode já existir
        exp_id = mlflow.get_experiment_by_name(exp_name).experiment_id
        print(f'  ✓ Experimento já existe com ID: {exp_id}')

print('✓ Experimentos re-importados com sucesso')
EOF

log_success "Experimentos re-importados"

# Step 7: Re-iniciar FastAPI
log_info "PASSO 7: Re-iniciando FastAPI..."
docker compose -f "${DEPLOY_DIR}/docker-compose-rds.yml" up -d fastapi
sleep 10
log_success "FastAPI reiniciado"

log_info "=== Migração concluída com sucesso! ==="
log_success "Backup: ${BACKUP_DIR}"
log_success "MLflow RDS: http://localhost:5002"
log_success "FastAPI: http://localhost:8000"

log_warning "Próximos passos:"
echo "  1. Verificar experimentos: http://localhost:5002"
echo "  2. Testar API: curl http://localhost:8000/health"
echo "  3. Na AWS, MLflow usará os mesmos dados: ${RDS_HOST}"
