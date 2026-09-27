#!/bin/bash

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║        Gerenciar Serviços ECS - Datathon Bandit (AWS)                   ║
# ║   Liga, desliga e monitora os serviços FastAPI e MLflow                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

set -e

# Configuração
export AWS_PROFILE=datathon
export AWS_REGION=us-east-2
CLUSTER="datathon-bandit-cluster"
SERVICE_FASTAPI="datathon-bandit-fastapi"
SERVICE_MLFLOW="datathon-bandit-mlflow"
MONITOR_TIMEOUT=120  # segundos
MONITOR_INTERVAL=2   # segundos

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════════════════
# Funções
# ═══════════════════════════════════════════════════════════════════════════

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

# Verificar AWS CLI
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI não encontrada. Instale com: brew install awscli"
        exit 1
    fi

    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "Credenciais AWS não configuradas. Execute: aws configure --profile datathon"
        exit 1
    fi

    log_info "✓ AWS CLI OK"
}

# Obter status atual dos serviços
get_service_status() {
    local service=$1
    aws ecs describe-services \
        --cluster "$CLUSTER" \
        --services "$service" \
        --query 'services[0].[desiredCount,runningCount,pendingCount]' \
        --output text 2>/dev/null
}

# Exibir status dos serviços
print_status() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"

    read -r desired_fa running_fa pending_fa <<< "$(get_service_status $SERVICE_FASTAPI)"
    read -r desired_ml running_ml pending_ml <<< "$(get_service_status $SERVICE_MLFLOW)"

    local status_fa="❌"
    [[ $running_fa -eq 1 ]] && status_fa="✅"

    local status_ml="❌"
    [[ $running_ml -eq 1 ]] && status_ml="✅"

    echo -e "📡 FastAPI      $status_fa  (desired: $desired_fa, running: $running_fa, pending: $pending_fa)"
    echo -e "📊 MLflow       $status_ml  (desired: $desired_ml, running: $running_ml, pending: $pending_ml)"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"
}

# Ligar os serviços
turn_on() {
    log_info "Ligando serviços ECS..."

    aws ecs update-service \
        --cluster "$CLUSTER" \
        --service "$SERVICE_FASTAPI" \
        --desired-count 1 \
        --output json > /dev/null

    aws ecs update-service \
        --cluster "$CLUSTER" \
        --service "$SERVICE_MLFLOW" \
        --desired-count 1 \
        --output json > /dev/null

    log_success "Comando enviado para ligar os serviços"
}

# Desligar os serviços
turn_off() {
    log_info "Desligando serviços ECS..."

    aws ecs update-service \
        --cluster "$CLUSTER" \
        --service "$SERVICE_FASTAPI" \
        --desired-count 0 \
        --output json > /dev/null

    aws ecs update-service \
        --cluster "$CLUSTER" \
        --service "$SERVICE_MLFLOW" \
        --desired-count 0 \
        --output json > /dev/null

    log_success "Comando enviado para desligar os serviços"
}

# Monitorar os serviços até ficarem online
monitor() {
    local max_attempts=$((MONITOR_TIMEOUT / MONITOR_INTERVAL))
    local attempt=0

    log_info "Monitorando status dos serviços (máx ${MONITOR_TIMEOUT}s)..."
    echo ""

    while (( attempt < max_attempts )); do
        read -r desired_fa running_fa pending_fa <<< "$(get_service_status $SERVICE_FASTAPI)"
        read -r desired_ml running_ml pending_ml <<< "$(get_service_status $SERVICE_MLFLOW)"

        timestamp=$(date '+%H:%M:%S')
        echo -e "[${BLUE}${timestamp}${NC}] FastAPI: ${running_fa}/${desired_fa} running (pending: ${pending_fa}) | MLflow: ${running_ml}/${desired_ml} running (pending: ${pending_ml})"

        # Verificar se ambos estão online
        if [[ $running_fa -eq 1 ]] && [[ $running_ml -eq 1 ]]; then
            echo ""
            log_success "Todos os serviços estão online!"
            print_endpoints
            return 0
        fi

        sleep "$MONITOR_INTERVAL"
        (( attempt++ ))
    done

    echo ""
    log_warning "Timeout: serviços não ficaram online após ${MONITOR_TIMEOUT}s"
    print_status
    return 1
}

# Exibir endpoints
print_endpoints() {
    local alb_dns=$(aws elbv2 describe-load-balancers \
        --query "LoadBalancers[?contains(LoadBalancerName, 'datathon-bandit-alb')].DNSName" \
        --output text 2>/dev/null)

    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "🎉 ${GREEN}Serviços Ativos!${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"

    if [[ -n "$alb_dns" ]]; then
        echo -e "📡 API FastAPI:"
        echo -e "   ${GREEN}http://${alb_dns}${NC}"
        echo -e "   ${GREEN}http://${alb_dns}/docs${NC} (Swagger)"
        echo -e "   ${GREEN}http://${alb_dns}/health${NC} (Health check)"
        echo ""
        echo -e "📊 MLflow UI:"
        echo -e "   ${GREEN}http://${alb_dns}:5000${NC}"
    else
        echo -e "⚠️  Não foi possível obter o DNS do ALB"
    fi

    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"
}

# Comando: ligar e monitorar
start() {
    check_aws_cli
    print_status
    turn_on
    sleep 2
    monitor
}

# Comando: desligar e monitorar
stop() {
    check_aws_cli
    print_status
    turn_off
    monitor_offline
}

# Monitorar até ficarem offline
monitor_offline() {
    local max_attempts=$((MONITOR_TIMEOUT / MONITOR_INTERVAL))
    local attempt=0

    log_info "Monitorando desligamento dos serviços (máx ${MONITOR_TIMEOUT}s)..."
    echo ""

    while (( attempt < max_attempts )); do
        read -r desired_fa running_fa pending_fa <<< "$(get_service_status $SERVICE_FASTAPI)"
        read -r desired_ml running_ml pending_ml <<< "$(get_service_status $SERVICE_MLFLOW)"

        timestamp=$(date '+%H:%M:%S')
        echo -e "[${BLUE}${timestamp}${NC}] FastAPI: ${running_fa}/${desired_fa} running | MLflow: ${running_ml}/${desired_ml} running"

        # Verificar se ambos estão offline
        if [[ $running_fa -eq 0 ]] && [[ $running_ml -eq 0 ]]; then
            echo ""
            log_success "Todos os serviços foram desligados!"
            return 0
        fi

        sleep "$MONITOR_INTERVAL"
        (( attempt++ ))
    done

    echo ""
    log_warning "Timeout: serviços não ficaram offline após ${MONITOR_TIMEOUT}s"
    print_status
    return 1
}

# Status dos serviços
status() {
    check_aws_cli
    print_status
}

# Help
show_help() {
    cat << EOF
${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}
${BLUE}║     Gerenciar Serviços ECS - Datathon Bandit                ║${NC}
${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}

${GREEN}Uso:${NC}
  $0 <comando>

${GREEN}Comandos:${NC}
  start       Liga os serviços (FastAPI + MLflow) e monitora
  stop        Desliga os serviços e monitora
  status      Exibe o status atual dos serviços
  monitor     Monitora os serviços (apenas monitoramento)

${GREEN}Exemplos:${NC}
  $0 start              # Liga e monitora até ficarem online
  $0 stop               # Desliga e monitora até ficarem offline
  $0 status             # Mostra status atual
  $0 monitor            # Apenas monitora (sem ligar/desligar)

${YELLOW}Notas:${NC}
  - Requer AWS CLI configurado com profile 'datathon'
  - Região padrão: us-east-2
  - Leva ~1-2 minutos para os serviços ficarem online

EOF
}

# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

if [[ $# -eq 0 ]]; then
    show_help
    exit 1
fi

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    monitor)
        check_aws_cli
        monitor
        ;;
    *)
        log_error "Comando desconhecido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
