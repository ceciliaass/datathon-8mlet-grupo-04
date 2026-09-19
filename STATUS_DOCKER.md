# 🚀 Status - Docker Compose Local

**Data:** 2026-09-19  
**Status:** ✅ ONLINE E OPERACIONAL

---

## 📊 Serviços Rodando

| Serviço | URL | Status | Porta |
|---------|-----|--------|-------|
| **MLflow UI** | http://localhost:5002 | ✅ Healthy | 5002 |
| **FastAPI** | http://localhost:8000 | ✅ Healthy | 8000 |
| **Network** | datathon_net | ✅ Connected | - |

---

## 📈 Experiments Visíveis

### Experiment 1: `datathon-bandit-canal` (Treinamento)
- **Runs:** 3
  - etapa3_baseline_vs_thompson
  - etapa4_avaliacao_golden_set
  - (versão anterior)
- **Métricas:** baseline_conversion, thompson_conversion, lift, IC95%
- **Artifacts:** baseline_results.csv, golden_set_results.csv, gráficos PNG

### Experiment 2: `datathon-bandit-app` (Produção)
- **Runs:** 1+ (novo run criado com o teste)
- **Métricas:** selected_arm, reward
- **Artifacts:** client_context.json

---

## 🔗 Links de Acesso

### MLflow UI
- **Geral:** http://localhost:5002
- **Experiments:** http://localhost:5002/experiments
- **Experiment 1:** http://localhost:5002/experiments/1
- **Experiment 2:** http://localhost:5002/experiments/2

### FastAPI
- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 📁 Estrutura de Dados

```
projeto/
├── mlruns/
│   ├── 1/                    ← Experiment 1 (Notebooks)
│   │   ├── 70fce3e.../       ← Run: Baseline vs Thompson
│   │   ├── 685d3f34.../      ← Run: Avaliação
│   │   └── f8b222525.../     ← Run: anterior
│   └── 2/                    ← Experiment 2 (API)
│       ├── be1e2f36.../      ← Run: novo (seu teste)
│       └── ...
└── mlflow.db                 ← Backend SQLite (856 KB)
```

---

## 🧪 Teste Realizado

```bash
# Requisição
curl -X POST http://localhost:8000/recomendar \
  -H 'Content-Type: application/json' \
  -d '{"idade":35,"poutcome":"unknown","previous":1}'

# Resposta
{
  "decision_id": "be1e2f36-f276-4114-843a-34e7f44d454f",
  "arm": "cellular"
}

# Feedback
curl -X POST http://localhost:8000/feedback \
  -H 'Content-Type: application/json' \
  -d '{"decision_id":"be1e2f36-f276-4114-843a-34e7f44d454f","converteu":true}'

# Stats Atuais
# cellular: 0.1502 taxa de conversão
# telephone: 0.1319 taxa de conversão
```

---

## 🛑 Para Parar

```bash
docker compose -f deploy/docker-compose.yml down
```

---

## 📝 O que foi alterado

✅ **docker-compose.yml:** Atualizado com comentários, health checks, MLFLOW_ALLOWED_HOSTS  
✅ **validate-mlflow-local.sh:** Criado para validar setup  
✅ **MLFLOW_UNIFICATION.md:** Consolidação de experiments  
✅ **DOCKER_COMPOSE_SETUP.md:** Guia completo  
✅ **MLFLOW_DATA_FLOW.md:** Arquitetura de dados  
✅ **QUICKSTART_MLFLOW_LOCAL.md:** Quick start 5 min  

---

**Tudo está pronto para uso! 🎉**
