#!/bin/bash

################################################################################
# 🔄 Script de Sincronização e Reset - Datathon Bandit
################################################################################

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${DEPLOY_DIR}")"
AWS_DIR="${DEPLOY_DIR}/aws"
TERRAFORM_DIR="${AWS_DIR}/terraform"
BACKUP_DIR="${PROJECT_ROOT}/.backup-$(date +%Y%m%d-%H%M%S)"

AWS_REGION="${AWS_REGION:-us-east-2}"
AWS_PROFILE="${AWS_PROFILE:-datathon}"
ECS_CLUSTER="datathon-bandit-cluster"
FASTAPI_SERVICE="datathon-bandit-fastapi"
MLFLOW_SERVICE="datathon-bandit-mlflow"

################################################################################
# Funções Auxiliares
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠️]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

################################################################################
# PHASE 1: Backup Local
################################################################################

phase_1_backup() {
    log_info "=== FASE 1: BACKUP DOS DADOS LOCAIS ==="

    mkdir -p "${BACKUP_DIR}"
    log_info "Criando backup em: ${BACKUP_DIR}"

    # Backup do banco de dados MLflow
    if [ -f "${PROJECT_ROOT}/mlflow.db" ]; then
        log_info "Fazendo backup do MLflow database..."
        cp "${PROJECT_ROOT}/mlflow.db" "${BACKUP_DIR}/mlflow.db"
        log_success "MLflow database backed up"
    fi

    # Backup dos artefatos
    if [ -d "${DEPLOY_DIR}/mlflow_artifacts" ]; then
        log_info "Fazendo backup dos artefatos MLflow..."
        cp -r "${DEPLOY_DIR}/mlflow_artifacts" "${BACKUP_DIR}/"
        log_success "Artefatos MLflow backed up"
    fi

    # Backup do código da aplicação
    if [ -d "${PROJECT_ROOT}/app" ]; then
        log_info "Fazendo backup do código da aplicação..."
        cp -r "${PROJECT_ROOT}/app" "${BACKUP_DIR}/"
        log_success "Código da aplicação backed up"
    fi

    log_success "FASE 1 completa: Backup criado em ${BACKUP_DIR}"
    echo ""
}

################################################################################
# PHASE 2: Parar Serviços Locais
################################################################################

phase_2_stop_local() {
    log_info "=== FASE 2: PARANDO SERVIÇOS LOCAIS ==="

    if docker ps -q --filter "name=datathon_fastapi" | grep -q .; then
        log_info "Parando FastAPI container..."
        docker stop datathon_fastapi || true
        log_success "FastAPI parado"
    else
        log_warning "FastAPI container não está rodando"
    fi

    if docker ps -q --filter "name=datathon_mlflow" | grep -q .; then
        log_info "Parando MLflow container..."
        docker stop datathon_mlflow || true
        log_success "MLflow parado"
    else
        log_warning "MLflow container não está rodando"
    fi

    sleep 2

    log_info "Removendo containers..."
    cd "${PROJECT_ROOT}"
    docker compose -f "${DEPLOY_DIR}/docker-compose.yml" down --remove-orphans || true

    log_success "FASE 2 completa: Serviços locais parados"
    echo ""
}

################################################################################
# PHASE 3: Resetar AWS
################################################################################

phase_3_reset_aws() {
    log_info "=== FASE 3: RESETANDO AWS ==="

    if ! aws sts get-caller-identity --profile "${AWS_PROFILE}" &>/dev/null; then
        log_warning "Não foi possível autenticar na AWS. Continuando com docker-compose local apenas."
        return 0
    fi

    log_info "Autenticação AWS verificada ✓"

    log_info "Parando serviços ECS..."

    aws ecs update-service \
        --cluster "${ECS_CLUSTER}" \
        --service "${FASTAPI_SERVICE}" \
        --desired-count 0 \
        --region "${AWS_REGION}" \
        --profile "${AWS_PROFILE}" \
        2>/dev/null || log_warning "FastAPI ECS service não encontrado"

    aws ecs update-service \
        --cluster "${ECS_CLUSTER}" \
        --service "${MLFLOW_SERVICE}" \
        --desired-count 0 \
        --region "${AWS_REGION}" \
        --profile "${AWS_PROFILE}" \
        2>/dev/null || log_warning "MLflow ECS service não encontrado"

    log_info "Aguardando parada dos serviços ECS..."
    sleep 30

    log_success "Serviços ECS parados"

    # Destruir infraestrutura terraform
    log_info "Destruindo infraestrutura Terraform..."

    cd "${TERRAFORM_DIR}"

    if [ -f "terraform.tfstate" ]; then
        log_warning "AVISO: Isto irá DESTRUIR toda a infraestrutura AWS!"
        log_warning "Pressione ENTER para continuar ou CTRL+C para cancelar..."
        read -r

        terraform destroy \
            -var-file="terraform.tfvars" \
            -auto-approve \
            2>&1 | tee "${BACKUP_DIR}/terraform-destroy.log"

        log_success "Infraestrutura Terraform destruída"
    else
        log_warning "Nenhum terraform.tfstate encontrado, pulando destruição"
    fi

    echo ""
}

################################################################################
# PHASE 4: Reconstruir AWS
################################################################################

phase_4_rebuild_aws() {
    log_info "=== FASE 4: RECONSTRUINDO AWS ==="

    if ! aws sts get-caller-identity --profile "${AWS_PROFILE}" &>/dev/null 2>&1; then
        log_warning "AWS não disponível, pulando fase de rebuild"
        return 0
    fi

    cd "${TERRAFORM_DIR}"

    log_info "Inicializando Terraform..."
    terraform init

    log_info "Aplicando configuração Terraform..."
    terraform apply \
        -var-file="terraform.tfvars" \
        -auto-approve \
        2>&1 | tee "${BACKUP_DIR}/terraform-apply.log"

    log_info "Exportando outputs Terraform..."
    terraform output -json > "${BACKUP_DIR}/terraform-outputs.json" 2>/dev/null || true

    log_success "FASE 4 completa: Infraestrutura AWS reconstruída"
    echo ""
}

################################################################################
# PHASE 5: Reconstruir Docker Images
################################################################################

phase_5_rebuild_images() {
    log_info "=== FASE 5: RECONSTRUINDO DOCKER IMAGES ==="

    cd "${PROJECT_ROOT}"

    log_info "Construindo imagem FastAPI..."
    docker build -f "${DEPLOY_DIR}/Dockerfile.fastapi" -t datathon-fastapi:latest . 2>&1 | tail -20
    log_success "FastAPI image construído"

    log_info "Verificando Dockerfile.mlflow..."
    if [ -f "${DEPLOY_DIR}/Dockerfile.mlflow" ]; then
        log_info "Construindo imagem MLflow..."
        docker build -f "${DEPLOY_DIR}/Dockerfile.mlflow" -t datathon-mlflow:latest . 2>&1 | tail -20
        log_success "MLflow image construído"
    else
        log_warning "Dockerfile.mlflow não encontrado, usando imagem padrão"
    fi

    log_success "FASE 5 completa: Docker images reconstruídos"
    echo ""
}

################################################################################
# PHASE 6: Ligar Docker Compose Local
################################################################################

phase_6_start_local() {
    log_info "=== FASE 6: LIGANDO DOCKER COMPOSE LOCAL ==="

    cd "${PROJECT_ROOT}"

    log_info "Iniciando serviços com docker-compose..."

    # Restaurar volumes se necessário
    if [ -d "${BACKUP_DIR}/mlflow_artifacts" ]; then
        log_info "Restaurando artefatos MLflow..."
        rm -rf "${DEPLOY_DIR}/mlflow_artifacts"
        cp -r "${BACKUP_DIR}/mlflow_artifacts" "${DEPLOY_DIR}/"
    fi

    # Iniciar docker-compose
    docker compose -f "${DEPLOY_DIR}/docker-compose.yml" up -d

    log_info "Aguardando inicialização dos serviços (30 segundos)..."
    sleep 30

    # Verificar saúde
    log_info "Verificando saúde dos serviços..."

    if curl -s http://localhost:8000/health 2>/dev/null | grep -q "ok"; then
        log_success "FastAPI está saudável ✓"
    else
        log_warning "FastAPI ainda está inicializando..."
    fi

    if curl -s http://localhost:5002 2>/dev/null | grep -q "MLflow" || curl -s http://localhost:5002 2>/dev/null | grep -q "ml"; then
        log_success "MLflow está saudável ✓"
    else
        log_warning "MLflow ainda está inicializando..."
    fi

    log_success "FASE 6 completa: Docker Compose local iniciado"
    echo ""
}

################################################################################
# PHASE 7: Sincronizar com AWS
################################################################################

phase_7_sync_to_aws() {
    log_info "=== FASE 7: SINCRONIZANDO COM AWS ==="

    if ! aws sts get-caller-identity --profile "${AWS_PROFILE}" &>/dev/null 2>&1; then
        log_warning "AWS não disponível, pulando sincronização"
        return 0
    fi

    cd "${AWS_DIR}"

    if [ -f "push_images.sh" ]; then
        log_info "Fazendo push das imagens Docker para ECR..."
        AWS_REGION="${AWS_REGION}" ./push_images.sh || log_warning "Push para ECR falhou"
        log_success "FASE 7 completa: Imagens sincronizadas com AWS"
    else
        log_warning "push_images.sh não encontrado, pulando push ECR"
    fi

    echo ""
}

################################################################################
# MAIN
################################################################################

main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║  🔄 SINCRONIZAÇÃO E RESET - DATATHON BANDIT            ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    log_info "Projeto: ${PROJECT_ROOT}"
    log_info "Região AWS: ${AWS_REGION}"
    log_info "Cluster ECS: ${ECS_CLUSTER}"
    echo ""

    # Executar fases
    phase_1_backup
    phase_2_stop_local
    phase_3_reset_aws
    phase_4_rebuild_aws
    phase_5_rebuild_images
    phase_6_start_local
    phase_7_sync_to_aws

    # Resumo final
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║  ✅ SINCRONIZAÇÃO COMPLETA!                            ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    log_success "Backup: ${BACKUP_DIR}"
    log_success "API Local: http://localhost:8000"
    log_success "API Docs: http://localhost:8000/docs"
    log_success "MLflow Local: http://localhost:5002"

    echo ""
    log_info "Próximos passos:"
    echo "  1. Verificar logs: docker logs -f datathon_fastapi"
    echo "  2. Verificar saúde: curl http://localhost:8000/health"
    echo "  3. Acessar documentação: http://localhost:8000/docs"
    echo "  4. Para ligar AWS: cd deploy/aws && ./manage-ecs.sh start"
}

# Executar main
main
