# 🐳 Docker Compose - Configuração MLflow Local

Guia para rodar o projeto localmente com Docker Compose e visualizar os experiments do MLflow.

---

## 📋 O que foi atualizado

### Docker Compose (`docker-compose.yml`)

#### ✨ Melhorias adicionadas:

| Melhoria | Antes | Depois |
|----------|-------|--------|
| **Volumes** | Básico | Comentado (explica cada mount) |
| **Variáveis** | Mínimas | Documentadas com explicações |
| **Allowed Hosts** | Fixo | Dinâmico com `*` (localhost, 127.0.0.1, browser) |
| **Health Check** | Simples | Melhorado (aguarda MLflow estar pronto) |
| **Depends On** | `depends_on: [mlflow]` | `depends_on: mlflow: {condition: service_healthy}` |
| **Labels** | Nenhum | Identificação dos serviços |
| **Start Period** | 10s | 15s MLflow, 20s FastAPI (mais tempo) |

---

## 🚀 Como Usar

### Pré-requisito: Docker Desktop instalado

```bash
docker --version
docker compose --version
```

### 1️⃣ Preparar os dados (rodar notebooks ANTES)

```bash
# Ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Rodar os notebooks (criam Experiment 1 em mlruns/)
jupyter notebook notebooks/03_Baseline_e_Thompson.ipynb
# ... após completar, fechar o notebook ...

jupyter notebook notebooks/04_Avaliacao_e_Golden_Set.ipynb
# ... após completar, fechar o notebook ...
```

**Resultado:** `mlruns/1/` contém os runs de treinamento ✅

### 2️⃣ Iniciar Docker Compose

```bash
cd datathon-8mlet-grupo-04

# Build + start dos serviços
docker compose -f deploy/docker-compose.yml build
docker compose -f deploy/docker-compose.yml up -d

# Aguardar ~15-20 segundos
# Status:
docker compose -f deploy/docker-compose.yml ps
```

**Output esperado:**
```
NAME                   STATUS           PORTS
datathon_mlflow        Up (healthy)     0.0.0.0:5002->5000/tcp
datathon_fastapi       Up (healthy)     0.0.0.0:8000->8000/tcp
```

### 3️⃣ Validar o setup (NOVO SCRIPT)

```bash
# Script de validação cria e valida a configuração
./deploy/validate-mlflow-local.sh
```

**Output esperado:**
```
ℹ Verificando se MLflow está acessível...
✅ MLflow está online em http://localhost:5002

ℹ Verificando se FastAPI está acessível...
✅ FastAPI está online em http://localhost:8000

📊 Experiments registrados no MLflow:
  Exp 1: datathon-bandit-canal (Treinamento - 2 runs)
  Exp 2: datathon-bandit-app (Produção - N runs)

📁 Estrutura local de mlruns:
  Exp 1: Treinamento (Notebooks 03, 04) - 2 runs
  Exp 2: Produção (API) - 0 runs (ainda)

🌐 Endpoints úteis:
  MLflow UI: http://localhost:5002
  FastAPI Docs: http://localhost:8000/docs
  Health Check: http://localhost:8000/health
```

### 4️⃣ Acessar o MLflow no navegador

**URLs:**
```
🌐 MLflow UI
   http://localhost:5002

📊 Experiments
   http://localhost:5002/experiments

📈 Experiment 1 (Training)
   http://localhost:5002/experiments/1

🚀 Experiment 2 (Production)
   http://localhost:5002/experiments/2
```

---

## 📊 O que você verá no MLflow UI

### Experiment 1: `datathon-bandit-canal` (Training)

**Runs:**
| Run ID | Name | Objetivo | Artifacts |
|--------|------|----------|-----------|
| `70fce3e...` | etapa3_baseline_vs_thompson | Treinamento do modelo | baseline_results.csv, conversao_e_distribuicao.png |
| `685d3f34...` | etapa4_avaliacao_golden_set | Avaliação do modelo | golden_set_results.csv, evaluation_metrics.json |

**Métricas visíveis:**
- `baseline_conversion`: 10.44%
- `thompson_conversion`: 13.67%
- `conversion_lift_relative_pct`: +31.0%

### Experiment 2: `datathon-bandit-app` (Production)

**Runs:** (criados quando você chama a API)

**Como criar runs de teste:**
```bash
# Terminal 1: Observar logs
docker compose -f deploy/docker-compose.yml logs -f fastapi

# Terminal 2: Fazer requisições
# 1. Recomendação
DECISION=$(curl -s -X POST http://localhost:8000/recomendar \
  -H 'Content-Type: application/json' \
  -d '{"idade":35,"poutcome":"unknown","previous":1}')
echo $DECISION

# Extrair decision_id (manualmente ou com jq)
DECISION_ID=$(echo $DECISION | grep -o '"decision_id":"[^"]*' | cut -d'"' -f4)
echo "Decision ID: $DECISION_ID"

# 2. Feedback (conversão)
curl -X POST http://localhost:8000/feedback \
  -H 'Content-Type: application/json' \
  -d "{\"decision_id\":\"$DECISION_ID\",\"converteu\":true}"

# 3. Ver estatísticas
curl http://localhost:8000/stats

# Novo run aparecerá em:
# http://localhost:5002/experiments/2
```

---

## 🔄 Estrutura de Volumes

```
Seu Computador              Docker Container
═══════════════════════════════════════════

projeto/
├── mlruns/          ←→     /app/mlruns
│   ├── 1/                  (Notebooks)
│   └── 2/                  (API)
│
├── mlflow.db        ←→     /app/mlflow.db
│                           (Backend store)
│
├── app/             ←→     /app/app
├── notebooks/       ←→     /app/notebooks
└── ...              ←→     /app/...
```

**Implicações:**
- ✅ Notebooks podem escrever em `mlruns/` (ligadas diretamente)
- ✅ MLflow dentro do container lê/escreve `mlruns/` (mesmo diretório)
- ✅ FastAPI dentro do container acessa `mlruns/` (compartilhado)
- ✅ Alterações aparecem em tempo real (sem rebuild)

---

## 🔧 Variáveis de Ambiente

### MLflow (`mlflow` service)

```yaml
environment:
  # Backend: SQLite local
  MLFLOW_BACKEND_STORE_URI=sqlite:////app/mlflow.db
  
  # Artifacts: pasta mlruns (contém Exp 1 + 2)
  MLFLOW_DEFAULT_ARTIFACT_ROOT=/app/mlruns
  
  # Hosts permitidos (para acesso local)
  MLFLOW_ALLOWED_HOSTS=mlflow:5000,mlflow,localhost,localhost:5000,localhost:5002,127.0.0.1,*
  
  # Debug (descomente se necessário)
  # MLFLOW_TRACKING_DEBUG=true
```

### FastAPI (`fastapi` service)

```yaml
environment:
  PYTHONUNBUFFERED=1
  
  # Conecta ao MLflow (nome DNS dentro da rede Docker)
  MLFLOW_TRACKING_URI=http://mlflow:5000
  
  # Debug (descomente se necessário)
  # MLFLOW_TRACKING_DEBUG=true
```

---

## 🆘 Troubleshooting

### ❌ Problema: "Connection refused" ao acessar MLflow

**Sintoma:**
```
curl: (7) Failed to connect to localhost port 5002: Connection refused
```

**Solução:**
```bash
# Verificar se container está rodando
docker compose -f deploy/docker-compose.yml ps

# Se não está, ver logs
docker compose -f deploy/docker-compose.yml logs mlflow

# Se erro de build, reconstruir
docker compose -f deploy/docker-compose.yml build --no-cache
docker compose -f deploy/docker-compose.yml up -d
```

### ❌ Problema: "No experiments found" no MLflow UI

**Sintoma:** MLflow abre, mas está vazio (nem Exp 1, nem Exp 2)

**Causas:**
1. Notebooks não foram executados (falta Exp 1)
2. Pasta `mlruns/` não está mapeada corretamente

**Solução:**
```bash
# 1. Verificar pasta local
ls -la mlruns/
# Deve mostrar: 1/ e 2/

# 2. Verificar se volume está montado
docker compose -f deploy/docker-compose.yml exec mlflow ls -la /app/mlruns/

# 3. Se vazio, notebooks não rodaram:
jupyter notebook notebooks/03_Baseline_e_Thompson.ipynb
jupyter notebook notebooks/04_Avaliacao_e_Golden_Set.ipynb

# 4. Reiniciar Docker
docker compose -f deploy/docker-compose.yml restart mlflow
```

### ❌ Problema: "File exists" ao fazer build

**Sintoma:**
```
ERROR: mkdir /app: file exists
```

**Solução:**
```bash
# Remover containers antigos
docker compose -f deploy/docker-compose.yml down -v

# Reconstruir from scratch
docker compose -f deploy/docker-compose.yml build --no-cache
docker compose -f deploy/docker-compose.yml up -d
```

### ❌ Problema: FastAPI não consegue acessar MLflow

**Sintoma:**
```
Failed to connect to MLflow tracking server: http://mlflow:5000
```

**Solução:**
```bash
# Verificar conectividade dentro do container
docker compose -f deploy/docker-compose.yml exec fastapi \
  curl -v http://mlflow:5000/

# Se falhar, MLflow ainda está iniciando:
# Aguardar 15-20 segundos e tentar novamente
```

---

## 📝 Fluxo Completo (Passo a Passo)

```bash
# 1. Estar no diretório do projeto
cd datathon-8mlet-grupo-04

# 2. Rodar notebooks (fora do Docker)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter notebook notebooks/03_Baseline_e_Thompson.ipynb
# ... fecha notebook ...
jupyter notebook notebooks/04_Avaliacao_e_Golden_Set.ipynb
# ... fecha notebook ...

# 3. Docker Compose
docker compose -f deploy/docker-compose.yml build
docker compose -f deploy/docker-compose.yml up -d

# 4. Validação
./deploy/validate-mlflow-local.sh

# 5. Acessar MLflow
# Abrir navegador: http://localhost:5002

# 6. Testar API
curl -X POST http://localhost:8000/recomendar \
  -H 'Content-Type: application/json' \
  -d '{"idade":35,"poutcome":"unknown","previous":1}'

# 7. Ver novo run em MLflow
# http://localhost:5002/experiments/2

# 8. Parar tudo
docker compose -f deploy/docker-compose.yml down
```

---

## 🎯 Resumo das Mudanças

| Arquivo | Mudança | Impacto |
|---------|---------|--------|
| `docker-compose.yml` | Comentários, variáveis, health check | Melhor debugging + documentação |
| `validate-mlflow-local.sh` | **Novo** | Validação automática do setup |

---

## 🔗 Próximos Passos

1. **Testar localmente:**
   ```bash
   docker compose -f deploy/docker-compose.yml up -d
   ./deploy/validate-mlflow-local.sh
   ```

2. **Explorar no MLflow UI:**
   - Ver Experiment 1 (treinamento)
   - Ver Experiment 2 (produção - com seus testes)
   - Comparar runs
   - Baixar artifacts

3. **Integrar com Etapa 8 (Demo Day):**
   - Gravar vídeo mostrando o MLflow UI
   - Fazer requisições e ver novo runs sendo criados

---

**Status:** ✅ Docker Compose otimizado para MLflow local  
**Última atualização:** 2026-09-19

