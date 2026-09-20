# 🚀 Como Usar Banco MLflow em Outro Ambiente

**Data:** 2026-09-20  
**Status:** O banco foi commitado no git - permite replicação sem retreinar

---

## 📋 Resumo

O arquivo `mlflow.db` foi **commitado no repositório** com:
- ✅ Modelo: `thompson_sampling_bandit` (v1, Production)
- ✅ Experimento: `testemlflow`
- ✅ 4 runs com parâmetros e métricas
- ✅ 32 tags do modelo
- ✅ 4 artefatos (CSV, JSON, PNG, modelo pickle)

Ao clonar o repositório em **outro ambiente**, o banco já vem com esses dados.

---

## 🔧 Passos para Usar em Outro Ambiente

### 1️⃣ Clonar Repositório
```bash
git clone https://github.com/seu-user/datathon-8mlet-grupo-04.git
cd datathon-8mlet-grupo-04
```

### 2️⃣ Verificar Banco
```bash
ls -lh mlflow.db
# Resultado esperado: ~852K mlflow.db
```

### 3️⃣ Iniciar MLflow Server (Opção A - Local Standalone)
```bash
cd /seu/caminho/datathon-8mlet-grupo-04

mlflow server \
  --host 0.0.0.0 \
  --port 5002 \
  --backend-store-uri sqlite:///$(pwd)/mlflow.db \
  --default-artifact-root $(pwd)/mlruns
```

**Ou (Opção B - Docker Compose - futuro)**
```bash
docker compose -f deploy/docker-compose.yml up -d
```

### 4️⃣ Acessar MLflow UI
```
URL: http://localhost:5002

Esperado:
✅ Experimento "testemlflow" visível
✅ Run "etapa3_baseline_vs_thompson" listado
✅ Modelo "thompson_sampling_bandit" no Model Registry
✅ Versão 1 em Production
✅ 32 tags visíveis
✅ 4 artefatos disponíveis
```

### 5️⃣ Verificar Banco Localmente
```bash
# Entrar no SQL
sqlite3 mlflow.db

# Dentro do SQL:
SELECT name FROM experiments;
# Resultado: testemlflow

SELECT name FROM registered_models;
# Resultado: thompson_sampling_bandit

SELECT COUNT(*) FROM registered_model_tags;
# Resultado: 32

.quit
```

---

## 📊 O Que Vem No Banco

### Experimentos
```
Name: testemlflow
ID: 1
Runs: 4 (incluindo etapa3_baseline_vs_thompson)
```

### Modelo
```
Name: thompson_sampling_bandit
Description: ✅ 741 caracteres (algoritmo, dataset, performance)
Tags: ✅ 32
Versão: ✅ 1 (Production)
```

### Run Principal
```
Name: etapa3_baseline_vs_thompson
Status: FINISHED
Parâmetros: 9
Métricas: 6
  - baseline_conversion: 0.1044
  - thompson_conversion: 0.1367
  - conversion_lift_relative_pct: 30.95
Artefatos: 4
  - bandit_results.csv
  - bandit_metrics.json
  - conversao_e_distribuicao.png
  - bandit_model_temp.pkl
```

---

## ⚙️ Usar o Modelo em Python

### Carregando o Modelo Registrado
```python
import mlflow

# Conectar ao MLflow
mlflow.set_tracking_uri("http://localhost:5002")

# Obter modelo
from mlflow.tracking import MlflowClient
client = MlflowClient()

# Opção 1: Via URI
model_uri = "models:/thompson_sampling_bandit/Production"
model = mlflow.pyfunc.load_model(model_uri)

# Opção 2: Via arquivo direto
import pickle
with open("mlruns/1/[run_id]/artifacts/model/bandit_model_temp.pkl", "rb") as f:
    bandit = pickle.load(f)
```

### Fazer Predições
```python
# Exemplo com MABWiser
arm_selected = bandit.predict()
print(f"Braço selecionado: {arm_selected}")
# Resultado esperado: 'cellular' ou 'telephone'
```

---

## 🐳 Docker Compose (Quando Implementar)

### Dockerfile.mlflow
```dockerfile
FROM python:3.11-slim

WORKDIR /mlflow

RUN pip install mlflow==2.10.2

COPY mlflow.db /mlflow/mlflow.db

EXPOSE 5000

CMD mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri sqlite:////mlflow/mlflow.db \
  --default-artifact-root /mlflow/artifacts
```

### docker-compose.yml
```yaml
services:
  mlflow:
    build:
      context: .
      dockerfile: Dockerfile.mlflow
    ports:
      - "5002:5000"
    volumes:
      - mlflow_data:/mlflow
    networks:
      - datathon_net
```

**Iniciar:**
```bash
docker compose up -d
# Acessar: http://localhost:5002
```

---

## 🔄 Atualizar o Banco

Se adicionar novos modelos/experimentos no ambiente atual:

### Atualizar no Git
```bash
# Adicionar mudanças
git add mlflow.db

# Commit
git commit -m "chore: atualizar banco MLflow com novos experimentos"

# Push
git push origin feature/deploy
```

### Puxar em Outro Ambiente
```bash
git pull origin feature/deploy
# Novo banco já vem carregado
```

---

## ✅ Checklist de Validação

- [ ] Banco `mlflow.db` existe (852K ou maior)
- [ ] MLflow server iniciado (`http://localhost:5002` respondendo)
- [ ] Experimento `testemlflow` visível no UI
- [ ] Modelo `thompson_sampling_bandit` no Model Registry
- [ ] Versão 1 em Production
- [ ] 32 tags visíveis
- [ ] 4 artefatos listados
- [ ] Métricas: baseline 10.44%, thompson 13.67%
- [ ] Python consegue carregar modelo

---

## 📍 Localização do Banco

```
Repositório:    datathon-8mlet-grupo-04/mlflow.db
Tamanho:        ~852K
Tipo:           SQLite
Versionado:     ✅ Sim (git)
Replicável:     ✅ Sim (sem retreinamento)
```

---

## 🚀 Próximas Fases

### Fase 3: API Integration
- Adicionar logging de inferências ao MLflow
- Endpoints `/recomendar` e `/feedback`
- Novos runs aparecerão automáticamente

### Fase 4: AWS RDS
- Migrar banco para RDS PostgreSQL
- Trocar `sqlite:///` por `postgresql://`
- S3 para artifacts
- Mesmo banco em ECS/Lambda

---

## 📞 Suporte

Se o banco não aparecer em outro ambiente:

1. Verificar se arquivo existe: `ls -lh mlflow.db`
2. Verificar permissões: `ls -la mlflow.db`
3. Verificar se git commitou: `git log --oneline mlflow.db | head -5`
4. Verificar SQLite: `sqlite3 mlflow.db "SELECT name FROM experiments;"`
5. Verificar MLflow server: `curl http://localhost:5002/health`

---

**Versão:** 1.0  
**Última Atualização:** 2026-09-20  
**Autor:** Documentação MLflow
