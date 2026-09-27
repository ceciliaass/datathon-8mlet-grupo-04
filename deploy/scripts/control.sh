#!/bin/bash

#######################################
# Control Script Unificado
# Controlar Local (Docker) ou AWS (ECS)
#######################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

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

info() {
    echo -e "${BLUE}[i]${NC} $1"
}

header() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC} $1"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Mostrar menu
show_main_menu() {
    header "CONTROLE DATATHON-BANDIT"

    echo "Escolha o ambiente:"
    echo ""
    echo "  1) LOCAL (Docker Compose)"
    echo "  2) AWS (ECS)"
    echo "  3) Sair"
    echo ""
}

# Menu Local
show_local_menu() {
    header "LOCAL - Docker Compose"

    echo "Escolha uma ação:"
    echo ""
    echo "  1)  Subir containers"
    echo "  2)  Desligar containers"
    echo "  3)  Pausar containers"
    echo "  4)  Retomar containers"
    echo "  5)  Ver status"
    echo "  6)  Ver logs"
    echo "  7)  Restart"
    echo "  8)  Reconstruir"
    echo "  9)  Voltar"
    echo ""
}

# Menu AWS
show_aws_menu() {
    header "AWS - ECS"

    echo "Escolha uma ação:"
    echo ""
    echo "  1) Pausar todos os serviços"
    echo "  2) Retomar todos os serviços"
    echo "  3) Ver status"
    echo "  4) Ver logs (FastAPI)"
    echo "  5) Ver logs (MLflow)"
    echo "  6) Voltar"
    echo ""
}

# Executar comando local
local_command() {
    local cmd=$1
    show_status "Executando: docker-control.sh $cmd"
    bash "$SCRIPT_DIR/docker-control.sh" "$cmd"
}

# Executar comando AWS
aws_command() {
    local cmd=$1
    show_status "Executando: ecs-control.sh $cmd"
    bash "$SCRIPT_DIR/ecs-control.sh" "$cmd"
}

# Local - Menu Interativo
local_menu() {
    while true; do
        show_local_menu
        read -p "Escolha uma opção [1-9]: " choice

        case $choice in
            1) local_command "up" ;;
            2) local_command "down" ;;
            3) local_command "pause" ;;
            4) local_command "unpause" ;;
            5) local_command "status" ;;
            6)
                read -p "Qual serviço? (vazio = todos): " service
                local_command "logs $service"
                ;;
            7) local_command "restart" ;;
            8) local_command "rebuild" ;;
            9) return ;;
            *) error "Opção inválida" ;;
        esac

        echo ""
        read -p "Pressione ENTER para continuar..."
    done
}

# AWS - Menu Interativo
aws_menu() {
    while true; do
        show_aws_menu
        read -p "Escolha uma opção [1-6]: " choice

        case $choice in
            1)
                read -p "Tem certeza? (s/N): " confirm
                if [ "$confirm" = "s" ]; then
                    aws_command "pause"
                fi
                ;;
            2)
                read -p "Tem certeza? (s/N): " confirm
                if [ "$confirm" = "s" ]; then
                    aws_command "resume"
                fi
                ;;
            3) aws_command "status" ;;
            4)
                info "Abrindo CloudWatch logs para FastAPI..."
                aws logs tail /ecs/fastapi --follow --region us-east-2
                ;;
            5)
                info "Abrindo CloudWatch logs para MLflow..."
                aws logs tail /ecs/mlflow --follow --region us-east-2
                ;;
            6) return ;;
            *) error "Opção inválida" ;;
        esac

        echo ""
        read -p "Pressione ENTER para continuar..."
    done
}

# Modo comando direto
command_mode() {
    local env=$1
    local action=$2

    case "$env" in
        local|docker)
            local_command "$action"
            ;;
        aws|ecs)
            aws_command "$action"
            ;;
        *)
            error "Ambiente inválido: $env (use: local ou aws)"
            ;;
    esac
}

# Main
main() {
    if [ $# -ge 2 ]; then
        # Modo comando direto: control.sh [local|aws] [action]
        command_mode "$1" "$2"
    else
        # Menu interativo
        while true; do
            show_main_menu
            read -p "Escolha uma opção [1-3]: " choice

            case $choice in
                1) local_menu ;;
                2) aws_menu ;;
                3)
                    echo "Saindo..."
                    exit 0
                    ;;
                *) error "Opção inválida" ;;
            esac
        done
    fi
}

main "$@"
