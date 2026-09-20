# 📁 Qual Banco de Dados MLflow Usar?

**Data:** 2026-09-20  
**Arquivo:** Este documento esclarece EXATAMENTE qual banco usar em cada contexto

---

## 🎯 Quick Reference

| Contexto | Banco | Path | Acesso |
|----------|-------|------|--------|
| **LOCAL (Atual)** | SQLite | `/Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04/mlflow.db` | `sqlite3 mlflow.db` |
| **Docker Compose** | SQLite | `/mlflow/mlflow.db` (no container) | `docker exec datathon_mlflow sqlite3 /mlflow/mlflow.db` |
| **AWS (RDS)** | PostgreSQL | `mlflow-rds.xxxxx.rds.amazonaws.com:5432` | `psql -h ... mlflow` |

---

## 📍 CURRENT SETUP (Executando Agora)

### Local Standalone Server
```
Status: ✅ ATIVO
URL: http://localhost:5002
Banco: /Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04/mlflow.db
Comando de Startup:
  mlflow server \
    --host 0.0.0.0 \
    --port 5002 \
    --backend-store-uri sqlite:///$(pwd)/mlflow.db \
    --default-artifact-root $(pwd)/mlruns
```

### Para Consultar o Banco:
```bash
# Local no projeto
cd /Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04
sqlite3 mlflow.db

# Dentro do SQL:
.tables                              # Lista todas as tabelas
SELECT name FROM experiments;         # Experimentos registrados
SELECT name FROM registered_models;   # Modelos registrados
.quit                                # Sair
```

### Python API:
```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5002")
# OU para local file:
mlflow.set_tracking_uri("sqlite:////Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04/mlflow.db")
```

---

## 🐳 DOCKER COMPOSE (Planejado para Próxima Fase)

### Configuração
```yaml
services:
  mlflow:
    volumes:
      - mlflow_data:/mlflow
    command: mlflow server --backend-store-uri sqlite:////mlflow/mlflow.db
```

### Paths
```
DENTRO DO CONTAINER:
  /mlflow/mlflow.db

NO DOCKER HOST (Volume):
  /var/lib/docker/volumes/mlflow_data/_data/mlflow.db

URL:
  http://localhost:5002 (mapeado de 5000)
```

### Para Acessar o Banco no Docker:
```bash
# Via Docker
docker exec datathon_mlflow sqlite3 /mlflow/mlflow.db

# Via Volume Local (se precisar)
sqlite3 /var/lib/docker/volumes/mlflow_data/_data/mlflow.db
```

---

## ☁️ AWS PRODUCTION (Fase 4 - Futuro)

### RDS PostgreSQL
```
Host: mlflow-rds.xxxxx.rds.amazonaws.com
Port: 5432
Database: mlflow
User: ${RDS_USER}
Password: ${RDS_PASSWORD}

Backend Store URI:
  postgresql://${RDS_USER}:${RDS_PASSWORD}@mlflow-rds.xxxxx.rds.amazonaws.com:5432/mlflow
```

### S3 Artifacts
```
Bucket: s3://seu-bucket/mlflow
Region: us-east-2
Artifact Root: s3://seu-bucket/mlflow/artifacts
```

### Environment Variables (ECS)
```
MLFLOW_TRACKING_URI=http://mlflow.ecs.internal:5000
MLFLOW_BACKEND_STORE_URI=postgresql://...
MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://bucket/mlflow
```

---

## ⚠️ IMPORTANTE - NÃO CONFUNDIR

### ❌ ERRADO
```python
# Usando banco local quando Docker está rodando
mlflow.set_tracking_uri("sqlite:///mlflow.db")  # Procura em pwd, não no container
```

### ✅ CORRETO - LOCAL
```python
# Local (standalone)
mlflow.set_tracking_uri("http://localhost:5002")
# OU
mlflow.set_tracking_uri("sqlite:////Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04/mlflow.db")
```

### ✅ CORRETO - DOCKER
```python
# De dentro do container ou via rede Docker
mlflow.set_tracking_uri("http://mlflow:5000")
# OU
mlflow.set_tracking_uri("sqlite:////mlflow/mlflow.db")
```

### ✅ CORRETO - AWS
```python
# RDS
mlflow.set_tracking_uri("http://mlflow.ecs.internal:5000")
```

---

## 📊 Status Atual

```
✅ LOCAL STANDALONE
   Banco: /Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04/mlflow.db
   URL: http://localhost:5002
   Modelos: thompson_sampling_bandit
   Experimentos: testemlflow
   Status: OPERACIONAL
```

---

## 📝 Comandos Úteis

### Verificar Banco Local
```bash
cd /Users/vagnerantononiodasilva/projetos_new/datathon-8mlet-grupo-04

# Ver tamanho
ls -lh mlflow.db

# Backup
cp mlflow.db mlflow.db.backup

# Restaurar
cp mlflow.db.backup mlflow.db

# Consultas
sqlite3 mlflow.db "SELECT COUNT(*) FROM experiments;"
sqlite3 mlflow.db "SELECT COUNT(*) FROM registered_models;"
```

### Verificar Server
```bash
# Status
curl -s http://localhost:5002/health || echo "Offline"

# Acessar UI
open http://localhost:5002  # macOS
xdg-open http://localhost:5002  # Linux
start http://localhost:5002  # Windows
```

---

**Versão:** 1.0  
**Última Atualização:** 2026-09-20
