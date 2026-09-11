# Deploy README — datathon-8mlet-grupo-04

Resumo rápido
- FastAPI: http://localhost:8000
- MLflow UI: http://localhost:5002 (host) -> container expõe 5000

Comandos úteis (executar em `datathon-8mlet-grupo-04`):

```bash
# Build
docker compose -f deploy/docker-compose.yml build

# Start (detached)
docker compose -f deploy/docker-compose.yml up -d --force-recreate

# Show status
docker compose -f deploy/docker-compose.yml ps

# Follow logs
docker compose -f deploy/docker-compose.yml logs -f --tail=200

# Run a command in the mlflow container (ex: migrate DB)
docker compose -f deploy/docker-compose.yml exec -T mlflow mlflow db upgrade sqlite:///mlflow.db

# Stop and remove
docker compose -f deploy/docker-compose.yml down
```

Volumes & persistência
- `./mlflow.db` — arquivo SQLite do MLflow (montado em `/app/mlflow.db`).
- `./mlruns` — diretório de artefatos do MLflow (montado em `/app/mlruns`).

Backup e restauração

```bash
# Backup
cp mlflow.db mlflow.db.bak
tar -czf mlruns-backup.tar.gz mlruns

# Restauração (pare os containers antes)
docker compose -f deploy/docker-compose.yml down
cp mlflow.db.bak mlflow.db
tar -xzf mlruns-backup.tar.gz -C .
docker compose -f deploy/docker-compose.yml up -d
```

Observações operacionais
- Se a porta host `5000` estiver ocupada, o compose aqui mapeia MLflow para `5002`.
- Para voltar a mapear MLflow em `5000` edite `deploy/docker-compose.yml` (ports) e garanta que nada no host esteja escutando em `5000`.
- Se o MLflow reclamar de schema desatualizado execute a migração:

```bash
docker compose -f deploy/docker-compose.yml exec -T mlflow mlflow db upgrade sqlite:///mlflow.db
```

Healthchecks
- O `docker-compose.yml` inclui healthchecks:
  - MLflow: verifica `http://127.0.0.1:5000/` dentro do container MLflow.
  - FastAPI: verifica `/health` e que `mlflow:5000` esteja acessível (readiness).

Dicas de troubleshooting
- Verifique `docker compose -f deploy/docker-compose.yml logs mlflow` para erros de DB.
- Se o container reiniciar repetidamente, faça backup de `mlflow.db` e execute a migração manualmente.

Quem comita
- Você optou por commitar manualmente; recomendo adicionar e commitar `deploy/*` e `app/requirements.txt` ao repositório quando estiver satisfeito.
