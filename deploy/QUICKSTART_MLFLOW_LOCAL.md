# 🚀 Quick Start - MLflow Local com Docker Compose

**Objetivo:** Rodar o projeto localmente e ver os experiments (Exp 1: treinamento, Exp 2: produção) no MLflow UI.

---

## ⏱️ Tempo total: ~10 min

---

## 1️⃣ Preparar dados (3-5 min)

```bash
cd datathon-8mlet-grupo-04

# Ativar ambiente
python3 -m venv venv
source venv/bin/activate

# Instalar
pip install -r requirements.txt

# Rodar notebooks (criam Experiment 1)
jupyter notebook notebooks/03_Baseline_e_Thompson.ipynb
# ... esperar completar, fechar notebook ...

jupyter notebook notebooks/04_Avaliacao_e_Golden_Set.ipynb
# ... esperar completar, fechar notebook ...
```

✅ **Resultado:** `mlruns/1/` com 2 runs de treinamento

---

## 2️⃣ Iniciar Docker Compose (2-3 min)

```bash
# Build + start
docker compose -f deploy/docker-compose.yml build
docker compose -f deploy/docker-compose.yml up -d

# Aguardar 15-20 segundos...

# Verificar status
docker compose -f deploy/docker-compose.yml ps
```

✅ **Esperado:** Ambos `datathon_mlflow` e `datathon_fastapi` com status `Up (healthy)`

---

## 3️⃣ Validar setup (1 min)

```bash
./deploy/validate-mlflow-local.sh
```

✅ **Esperado:** 
```
✅ MLflow está online em http://localhost:5002
✅ FastAPI está online em http://localhost:8000
📊 Experiments registrados:
  Exp 1: datathon-bandit-canal (2 runs)
  Exp 2: datathon-bandit-app (0 runs)
```

---

## 4️⃣ Acessar MLflow UI

🌐 **Abrir navegador:**
```
http://localhost:5002
```

**O que você verá:**
- **Experiment 1:** `datathon-bandit-canal` (Treinamento)
  - Run 1: Baseline vs Thompson Sampling
  - Run 2: Avaliação e Golden Set
  - Métricas: conversion_lift (+31%), IC95%, regret_acumulado

- **Experiment 2:** `datathon-bandit-app` (Produção)
  - Vazio por enquanto (você cria runs fazendo requisições)

---

## 5️⃣ Testar a API (criar Experiment 2 runs)

```bash
# Terminal 1: Ver logs em tempo real
docker compose -f deploy/docker-compose.yml logs -f fastapi

# Terminal 2: Fazer requisições
# 1. Recomendação
curl -X POST http://localhost:8000/recomendar \
  -H 'Content-Type: application/json' \
  -d '{"idade":35,"poutcome":"unknown","previous":1}'

# Copiar decision_id retornado
# Exemplo: {"decision_id":"uuid-123", "arm":"cellular", ...}

# 2. Feedback
curl -X POST http://localhost:8000/feedback \
  -H 'Content-Type: application/json' \
  -d '{"decision_id":"uuid-123","converteu":true}'

# 3. Stats
curl http://localhost:8000/stats
```

✅ **Resultado:** Novo run aparece em `http://localhost:5002/experiments/2`

---

## 🛑 Parar tudo

```bash
docker compose -f deploy/docker-compose.yml down
```

---

## 📚 Documentação Completa

- **Docker Compose detalhado:** [`deploy/DOCKER_COMPOSE_SETUP.md`](DOCKER_COMPOSE_SETUP.md)
- **MLflow Data Flow:** [`deploy/MLFLOW_DATA_FLOW.md`](MLFLOW_DATA_FLOW.md)
- **Unificação de Experiments:** [`deploy/MLFLOW_UNIFICATION.md`](MLFLOW_UNIFICATION.md)

---

## 🎯 Checklist

- [ ] Notebooks rodaram (Exp 1 em `mlruns/1/`)
- [ ] Docker Compose subiu (`docker compose ps`)
- [ ] MLflow UI acessível (`http://localhost:5002`)
- [ ] Experiments 1 e 2 visíveis
- [ ] API respondendo (`curl http://localhost:8000/health`)
- [ ] Requisições criando novo runs em Exp 2

---

## 💡 Dicas

### Ver logs em tempo real
```bash
docker compose -f deploy/docker-compose.yml logs -f mlflow
docker compose -f deploy/docker-compose.yml logs -f fastapi
```

### Acessar a API (Swagger)
```
http://localhost:8000/docs
```

### Resetar tudo (limpar containers + volumes)
```bash
docker compose -f deploy/docker-compose.yml down -v
```

### Recriar sem cache
```bash
docker compose -f deploy/docker-compose.yml build --no-cache
docker compose -f deploy/docker-compose.yml up -d
```

---

## ⚠️ Problemas comuns

| Problema | Solução |
|----------|---------|
| "Connection refused" | `docker compose ps` — container não subiu? |
| "No experiments found" | Notebooks não rodaram? Executar 03 e 04 |
| Volumes não mapeados | `docker compose exec mlflow ls -la /app/mlruns/` |
| FastAPI não acessa MLflow | Aguardar 15-20s (MLflow ainda iniciando) |

---

**Status:** ✅ Pronto para usar!  
**Próximo:** Abrir http://localhost:5002 e explorar os experiments 🎉

