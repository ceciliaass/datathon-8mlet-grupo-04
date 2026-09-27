#!/bin/bash

#######################################
# ECS Control Script
# Pausar/Retomar serviços na AWS
#######################################

set -e

CLUSTER="datathon-bandit-cluster"
REGION="us-east-2"

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funções
show_status() {
    echo -e "${YELLOW}[STATUS]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
    exit 1
}

# Verificar credenciais AWS
check_aws() {
    if ! command -v aws &> /dev/null; then
        error "AWS CLI não está instalado"
    fi

    if ! aws sts get-caller-identity &> /dev/null; then
        error "Credenciais AWS não configuradas. Execute: aws configure"
    fi

    success "AWS CLI autenticado"
}

# Listar serviços
list_services() {
    show_status "Serviços no cluster $CLUSTER:"
    aws ecs list-services \
        --cluster "$CLUSTER" \
        --region "$REGION" \
        --query 'serviceArns[*]' \
        --output table
}

# Pausar serviço
pause_service() {
    local service=$1
    local desired_count=${2:-0}

    show_status "Pausando $service (desired_count=$desired_count)..."

    aws ecs update-service \
        --cluster "$CLUSTER" \
        --service "$service" \
        --desired-count "$desired_count" \
        --region "$REGION" \
        > /dev/null

    success "Serviço $service pausado"
}

# Retomar serviço
resume_service() {
    local service=$1
    local desired_count=${2:-1}

    show_status "Retomando $service (desired_count=$desired_count)..."

    aws ecs update-service \
        --cluster "$CLUSTER" \
        --service "$service" \
        --desired-count "$desired_count" \
        --region "$REGION" \
        > /dev/null

    success "Serviço $service retomado"
}

# Pausar todos os serviços
pause_all() {
    show_status "Pausando TODOS os serviços..."

    pause_service "datathon-bandit-fastapi" 0
    pause_service "datathon-bandit-mlflow" 0

    success "Todos os serviços pausados (desired_count=0)"
}

# Retomar todos os serviços
resume_all() {
    show_status "Retomando TODOS os serviços..."

    resume_service "datathon-bandit-fastapi" 1
    resume_service "datathon-bandit-mlflow" 1

    show_status "Aguardando serviços iniciarem (~2 min)..."
    sleep 120

    success "Todos os serviços retomados"
}

# Verificar status
check_status() {
    show_status "Status dos serviços:"

    aws ecs describe-services \
        --cluster "$CLUSTER" \
        --services \
            datathon-bandit-fastapi \
            datathon-bandit-mlflow \
        --region "$REGION" \
        --query 'services[*].[serviceName,desiredCount,runningCount]' \
        --output table
}

# Menu
show_menu() {
    echo ""
    echo "╔═══════════════════════════════════════╗"
    echo "║     ECS Control - datathon-bandit     ║"
    echo "╚═══════════════════════════════════════╝"
    echo ""
    echo "1) Pausar TODOS os serviços (desired_count=0)"
    echo "2) Retomar TODOS os serviços (desired_count=1)"
    echo "3) Verificar status"
    echo "4) Listar serviços"
    echo "5) Sair"
    echo ""
}

# Main
main() {
    check_aws

    if [ $# -eq 0 ]; then
        # Menu interativo
        while true; do
            show_menu
            read -p "Escolha uma opção [1-5]: " choice

            case $choice in
                1) pause_all ;;
                2) resume_all ;;
                3) check_status ;;
                4) list_services ;;
                5) echo "Saindo..."; exit 0 ;;
                *) error "Opção inválida" ;;
            esac
        done
    else
        # Comando direto
        case "$1" in
            pause)
                pause_all
                ;;
            resume)
                resume_all
                ;;
            status)
                check_status
                ;;
            list)
                list_services
                ;;
            *)
                error "Uso: $0 [pause|resume|status|list]"
                ;;
        esac
    fi
}

main "$@"
