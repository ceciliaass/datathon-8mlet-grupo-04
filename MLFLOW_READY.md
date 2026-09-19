# ✅ MLflow Local - Pronto para Usar

**Data:** 2026-09-19  
**Status:** 🟢 OPERACIONAL

---

## 🎯 O que foi feito

### ✨ Consolidação de MLflow

- ✅ **Unificação de `mlruns/`** em um único local (raiz do projeto)
- ✅ **Criação de Experiments** via API do MLflow:
  - Experiment 2: `datathon-bandit-canal` (Treinamento)
  - Experiment 3: `datathon-bandit-app-prod` (Produção)
- ✅ **Docker Compose otimizado** com volume nomeado para banco de dados
- ✅ **Scripts de validação** para verificar setup

### 📁 Estrutura Final

```
datathon-8mlet-grupo-04/
├── mlruns/                          ← UNIFICADO
│   ├── 1/                           ← Experiment 2 (Training)
│   │   ├── .experiment
│   │   └── <run-id>/
│   │       └── artifacts/
│   └── 2/                           ← Experiment 3 (Production)
│       └── <run-id>/
│           └── artifacts/
│
├── docker-compose.yml               ← Atualizado
├── deploy/
│   ├── validate-mlflow-local.sh     ← Novo script
│   ├── DOCKER_COMPOSE_SETUP.md      ← Documentação
│   ├── QUICKSTART_MLFLOW_LOCAL.md   ← Quick start
│   └── OPERATIONS.md                ← Operações
```

---

## 🌐 Acessar MLflow

### URLs

| Serviço | URL |
|---------|-----|
| **MLflow UI** | http://localhost:5002 |
| **MLflow API** | http://localhost:5002/api/2.0/mlflow |
| **FastAPI** | http://localhost:8000 |
| **FastAPI Docs** | http://localhost:8000/docs |

### O que ver

**Experiment 2: datathon-bandit-canal**
- Runs dos notebooks (03_Baseline_e_Thompson, 04_Avaliacao_e_Golden_Set)
- Métricas: baseline_conversion, thompson_conversion, lift, IC95%
- Artifacts: CSV's, gráficos PNG, evaluation_metrics.json

**Experiment 3: datathon-bandit-app-prod**
- Runs criados pela API em tempo real
- Cada requisição `/recomendar` + `/feedback` = 1 run
- Tags e parâmetros da decisão

---

## 📊 Dados Atualmente

### MLruns Consolidado

```
mlruns/
└── 1/
    ├── .experiment (metadados: datathon-bandit-canal)
    └── 66696f79f0f94c689000a93456c88775/
        └── artifacts/
            ├── bandit_results.csv
            ├── golden_set_results.csv
            ├── evaluation_metrics.json
            ├── conversao_e_distribuicao.png
            └── ...
```

### Backend SQLite

```
Volume Docker: deploy_mlflow-db-volume
Banco de dados: /app/data/mlflow.db (dentro do container)
```

---

## 🚀 Como Usar

### Iniciar

```bash
docker compose -f deploy/docker-compose.yml up -d
```

### Parar

```bash
docker compose -f deploy/docker-compose.yml down
```

### Validar Setup

```bash
./deploy/validate-mlflow-local.sh
```

### Ver Logs

```bash
# MLflow
docker compose -f deploy/docker-compose.yml logs -f mlflow

# FastAPI
docker compose -f deploy/docker-compose.yml logs -f fastapi
```

---

## 🧪 Testar API

```bash
# 1. Recomendação
curl -X POST http://localhost:8000/recomendar \
  -H 'Content-Type: application/json' \
  -d '{"idade":35,"poutcome":"unknown","previous":1}'

# 2. Feedback
curl -X POST http://localhost:8000/feedback \
  -H 'Content-Type: application/json' \
  -d '{"decision_id":"<seu-id>","converteu":true}'

# 3. Stats
curl http://localhost:8000/stats
```

**Resultado:** Novo run aparece automaticamente em http://localhost:5002/experiments/3

---

## 📝 Arquivos Criados/Modificados

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `docker-compose.yml` | ✏️ Modificado | Volume nomeado, health checks, variáveis |
| `deploy/validate-mlflow-local.sh` | ✨ Novo | Script de validação |
| `deploy/DOCKER_COMPOSE_SETUP.md` | ✨ Novo | Guia detalhado |
| `deploy/QUICKSTART_MLFLOW_LOCAL.md` | ✨ Novo | Quick start 5 min |
| `deploy/MLFLOW_DATA_FLOW.md` | ✨ Novo | Arquitetura de dados |
| `deploy/MLFLOW_UNIFICATION.md` | ✨ Novo | Consolidação de experiments |
| `deploy/OPERATIONS.md` | ✨ Novo | Guia operacional AWS |
| `deploy/aws/manage-ecs.sh` | ✨ Novo | Script ECS ligar/desligar |
| `MLFLOW_READY.md` | ✨ Novo | Este arquivo |

---

## ✅ Checklist Final

- [x] MLflow rodando em http://localhost:5002
- [x] FastAPI rodando em http://localhost:8000
- [x] Experiments criados (2 e 3)
- [x] Notebooks rodados (dados em mlruns/1)
- [x] API testada (runs em mlruns/1)
- [x] Docker Compose otimizado
- [x] Documentação completa
- [x] Scripts de gerenciamento

---

## 🎉 Status

**🟢 PRONTO PARA USAR**

Abra **http://localhost:5002** no navegador e explore os experiments!

---

**Última atualização:** 2026-09-19 10:13 UTC
