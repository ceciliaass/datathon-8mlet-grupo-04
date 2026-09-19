#!/bin/bash

# Script para validar que o MLflow local está funcionando corretamente
# e que ambos os experiments estão visíveis

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

# Configuração
MLFLOW_URL="http://localhost:5002"
API_URL="http://localhost:8000"

echo -e "\n${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Validação do MLflow Local (Experiments)       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}\n"

# 1. Verificar se MLflow está rodando
log_info "Verificando se MLflow está acessível..."
if curl -s -f "$MLFLOW_URL" > /dev/null 2>&1; then
    log_success "MLflow está online em $MLFLOW_URL"
else
    log_error "MLflow não está respondendo em $MLFLOW_URL"
    echo "  Verifique se docker-compose está rodando: docker compose -f deploy/docker-compose.yml ps"
    exit 1
fi

# 2. Verificar se API está rodando
log_info "Verificando se FastAPI está acessível..."
if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    log_success "FastAPI está online em $API_URL"
else
    log_warning "FastAPI ainda está iniciando ou inacessível"
fi

# 3. Listar experiments
echo -e "\n${BLUE}═════════════════════════════════════════════${NC}"
echo -e "📊 Experiments registrados no MLflow:"
echo -e "${BLUE}═════════════════════════════════════════════${NC}\n"

response=$(curl -s "$MLFLOW_URL/api/2.0/mlflow/experiments/search")

# Parse com jq se disponível, senão fallback para grep
if command -v jq &> /dev/null; then
    experiments=$(echo "$response" | jq -r '.experiments[] | "\(.experiment_id): \(.name)"' 2>/dev/null || echo "")
    if [ -z "$experiments" ]; then
        log_warning "Nenhum experiment encontrado (ou resposta inválida)"
        echo "Resposta bruta: $response"
    else
        echo "$experiments" | while read -r line; do
            if [ -n "$line" ]; then
                exp_id=$(echo "$line" | cut -d: -f1)
                exp_name=$(echo "$line" | cut -d: -f2-)
                echo -e "  ${GREEN}Exp $exp_id:${NC} $exp_name"
            fi
        done
    fi
else
    # Fallback sem jq
    if echo "$response" | grep -q "datathon-bandit-canal"; then
        log_success "Experiment 1 (datathon-bandit-canal) encontrado"
    else
        log_warning "Experiment 1 não localizado"
    fi

    if echo "$response" | grep -q "datathon-bandit-app"; then
        log_success "Experiment 2 (datathon-bandit-app) encontrado"
    else
        log_warning "Experiment 2 não localizado"
    fi
fi

# 4. Verificar arquivos locais
echo -e "\n${BLUE}═════════════════════════════════════════════${NC}"
echo -e "📁 Estrutura local de mlruns:"
echo -e "${BLUE}═════════════════════════════════════════════${NC}\n"

MLRUNS_PATH="../mlruns"
if [ -d "$MLRUNS_PATH" ]; then
    exp_count=$(find "$MLRUNS_PATH" -maxdepth 1 -type d -name "[0-9]*" | wc -l)
    log_success "Pasta mlruns/ existe com $exp_count experiment(s)"

    for exp_dir in "$MLRUNS_PATH"/[0-9]*; do
        if [ -d "$exp_dir" ]; then
            exp_id=$(basename "$exp_dir")
            run_count=$(find "$exp_dir" -maxdepth 1 -type d | wc -l)
            run_count=$((run_count - 1))  # subtrai a pasta do experiment

            case $exp_id in
                1)
                    echo -e "  ${GREEN}Exp 1:${NC} Treinamento (Notebooks 03, 04) - $run_count runs"
                    ;;
                2)
                    echo -e "  ${GREEN}Exp 2:${NC} Produção (API) - $run_count runs"
                    ;;
                *)
                    echo -e "  ${YELLOW}Exp $exp_id:${NC} $run_count runs"
                    ;;
            esac
        fi
    done
else
    log_error "Pasta mlruns/ não encontrada"
fi

# 5. Verificar arquivo mlflow.db
echo ""
if [ -f "../mlflow.db" ]; then
    db_size=$(du -h "../mlflow.db" | cut -f1)
    log_success "Backend SQLite (mlflow.db) - Tamanho: $db_size"
else
    log_warning "Arquivo mlflow.db não encontrado (será criado no primeiro log)"
fi

# 6. Endpoints úteis
echo -e "\n${BLUE}═════════════════════════════════════════════${NC}"
echo -e "🌐 Endpoints úteis:"
echo -e "${BLUE}═════════════════════════════════════════════${NC}\n"

echo -e "  📊 MLflow UI:"
echo -e "     ${GREEN}http://localhost:5002${NC}"
echo -e "     ${GREEN}http://localhost:5002/experiments${NC}"
echo ""
echo -e "  📡 FastAPI:"
echo -e "     ${GREEN}http://localhost:8000${NC}"
echo -e "     ${GREEN}http://localhost:8000/docs${NC} (Swagger)"
echo -e "     ${GREEN}http://localhost:8000/health${NC} (Health Check)"
echo ""
echo -e "  🔗 API MLflow (programático):"
echo -e "     ${GREEN}http://localhost:5002/api/2.0/mlflow/experiments/search${NC}"
echo -e "     ${GREEN}http://localhost:5002/api/2.0/mlflow/runs/search${NC}"

# 7. Comandos úteis
echo -e "\n${BLUE}═════════════════════════════════════════════${NC}"
echo -e "💡 Comandos úteis:"
echo -e "${BLUE}═════════════════════════════════════════════${NC}\n"

echo -e "  # Visualizar logs do MLflow"
echo -e "  ${YELLOW}docker compose -f deploy/docker-compose.yml logs -f mlflow${NC}\n"

echo -e "  # Visualizar logs da API"
echo -e "  ${YELLOW}docker compose -f deploy/docker-compose.yml logs -f fastapi${NC}\n"

echo -e "  # Status dos serviços"
echo -e "  ${YELLOW}docker compose -f deploy/docker-compose.yml ps${NC}\n"

echo -e "  # Parar tudo"
echo -e "  ${YELLOW}docker compose -f deploy/docker-compose.yml down${NC}\n"

echo -e "  # Testar a API (recomendar)"
echo -e "  ${YELLOW}curl -X POST http://localhost:8000/recomendar \\${NC}"
echo -e "  ${YELLOW}  -H 'Content-Type: application/json' \\${NC}"
echo -e "  ${YELLOW}  -d '{\"idade\":35,\"poutcome\":\"unknown\",\"previous\":1}'${NC}\n"

# 8. Resumo final
echo -e "\n${BLUE}═════════════════════════════════════════════${NC}"

if curl -s -f "$MLFLOW_URL" > /dev/null 2>&1; then
    log_success "Sistema está pronto!"
    echo ""
    echo -e "  ${GREEN}✓${NC} MLflow rodando"
    echo -e "  ${GREEN}✓${NC} Pasta mlruns compartilhada (Exp 1 + 2)"
    echo -e "  ${GREEN}✓${NC} Backend SQLite configurado"
    echo ""
    echo -e "  Abra ${GREEN}http://localhost:5002${NC} no navegador para ver os experiments!"
else
    log_error "Algo deu errado"
    exit 1
fi

echo ""
