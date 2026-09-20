#!/bin/bash

#######################################
# Docker Compose Control Script
# Pausar/Ligar serviços localmente
#######################################

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$PROJECT_DIR/deploy/docker-compose.yml"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Verificar Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker não está instalado"
    fi

    if ! docker ps &> /dev/null; then
        error "Docker não está rodando ou você não tem permissão"
    fi

    success "Docker está disponível"
}

# Verificar Docker Compose
check_compose() {
    if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
        error "Docker Compose não está disponível"
    fi

    if [ ! -f "$COMPOSE_FILE" ]; then
        error "Arquivo docker-compose.yml não encontrado: $COMPOSE_FILE"
    fi

    success "Docker Compose está configurado"
}

# Subir containers
up() {
    show_status "Subindo containers do Docker Compose..."

    docker compose -f "$COMPOSE_FILE" up -d

    sleep 5

    show_status "Aguardando serviços ficarem saudáveis (~30s)..."
    sleep 30

    success "Containers iniciados"

    # Mostrar status
    status
}

# Desligar containers
down() {
    show_status "Desligando containers..."

    docker compose -f "$COMPOSE_FILE" down

    success "Containers desligados"
}

# Pausar containers (manter estado)
pause() {
    show_status "Pausando containers (mantendo estado)..."

    docker compose -f "$COMPOSE_FILE" pause

    success "Containers pausados"
}

# Retomar containers
unpause() {
    show_status "Retomando containers..."

    docker compose -f "$COMPOSE_FILE" unpause

    sleep 5

    success "Containers retomados"

    # Mostrar status
    status
}

# Verificar status
status() {
    show_status "Status dos containers:"
    echo ""
    docker compose -f "$COMPOSE_FILE" ps
    echo ""

    # URLs de acesso
    info "URLs de acesso:"
    echo "  • MLflow UI:  http://localhost:5002"
    echo "  • FastAPI:    http://localhost:8000"
    echo "  • API Docs:   http://localhost:8000/docs"
    echo ""
}

# Ver logs
logs() {
    local service=${1:-""}

    if [ -z "$service" ]; then
        show_status "Mostrando logs de TODOS os containers..."
        docker compose -f "$COMPOSE_FILE" logs -f --tail=100
    else
        show_status "Mostrando logs do serviço: $service"
        docker compose -f "$COMPOSE_FILE" logs -f --tail=100 "$service"
    fi
}

# Limpar volumes (CUIDADO!)
clean() {
    read -p "⚠️  Isso vai REMOVER volumes e dados. Continuar? (s/N): " confirm

    if [ "$confirm" != "s" ]; then
        echo "Cancelado"
        return
    fi

    show_status "Removendo containers e volumes..."
    docker compose -f "$COMPOSE_FILE" down -v

    success "Limpeza concluída"
}

# Restart
restart() {
    show_status "Reiniciando containers..."

    down
    sleep 2
    up

    success "Containers reiniciados"
}

# Rebuild
rebuild() {
    show_status "Reconstruindo imagens..."

    docker compose -f "$COMPOSE_FILE" down
    docker compose -f "$COMPOSE_FILE" build --no-cache
    docker compose -f "$COMPOSE_FILE" up -d

    sleep 30

    success "Imagens reconstruídas e containers reiniciados"
}

# Menu interativo
show_menu() {
    echo ""
    echo "╔══════════════════════════════════════════╗"
    echo "║  Docker Compose Control - datathon      ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    echo "1)  Subir containers (docker compose up)"
    echo "2)  Desligar containers (docker compose down)"
    echo "3)  Pausar containers (manter estado)"
    echo "4)  Retomar containers"
    echo "5)  Ver status"
    echo "6)  Ver logs (todos)"
    echo "7)  Ver logs (MLflow)"
    echo "8)  Ver logs (FastAPI)"
    echo "9)  Restart containers"
    echo "10) Reconstruir imagens"
    echo "11) Limpar tudo (CUIDADO!)"
    echo "12) Sair"
    echo ""
}

# Main
main() {
    check_docker
    check_compose

    if [ $# -eq 0 ]; then
        # Menu interativo
        while true; do
            show_menu
            read -p "Escolha uma opção [1-12]: " choice

            case $choice in
                1) up ;;
                2) down ;;
                3) pause ;;
                4) unpause ;;
                5) status ;;
                6) logs ;;
                7) logs mlflow ;;
                8) logs fastapi ;;
                9) restart ;;
                10) rebuild ;;
                11) clean ;;
                12) echo "Saindo..."; exit 0 ;;
                *) error "Opção inválida" ;;
            esac

            echo ""
            read -p "Pressione ENTER para continuar..."
        done
    else
        # Comando direto
        case "$1" in
            up|start)
                up
                ;;
            down|stop)
                down
                ;;
            pause)
                pause
                ;;
            unpause|resume)
                unpause
                ;;
            status)
                status
                ;;
            logs)
                logs "${2:-}"
                ;;
            restart)
                restart
                ;;
            rebuild)
                rebuild
                ;;
            clean)
                clean
                ;;
            *)
                error "Uso: $0 [up|down|pause|unpause|status|logs|restart|rebuild|clean]"
                ;;
        esac
    fi
}

main "$@"
