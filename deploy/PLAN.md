# Plano de implantação — datathon-8mlet-grupo-04

Objetivo: criar um `docker-compose` que levante simultaneamente a aplicação FastAPI e um servidor MLflow, usando imagens baseadas em `ubuntu:26.04`, com volumes montados para persistência do `mlflow.db` e dos artefatos em `mlruns`.

Fases:

1) Preparação (esta fase)
- Criar pasta `deploy` com os artefatos de deploy.
- Adicionar `Dockerfile.fastapi` e `Dockerfile.mlflow` (base: `ubuntu:26.04`).
- Adicionar `docker-compose.yml` para orquestrar os dois serviços.

2) Build e teste local
- Construir as imagens com `docker compose build` a partir de `deploy`.
- Subir os serviços com `docker compose up` e validar:
  - FastAPI disponível em `http://localhost:8000`.
  - MLflow UI em `http://localhost:5000`.
- Verificar que `mlflow.db` e a pasta `mlruns` são criadas no diretório do projeto.

3) Ajustes e otimizações
- Se necessário, ajustar dependências em `app/requirements.txt`.
- Adicionar healthchecks ao `docker-compose.yml`.
- Tornar volumes mais específicos (ex.: separar logs, artefatos).

4) Documentação e runbook
- Documentar comandos de build/exec no `deploy/PLAN.md`.
- Incluir instruções para backup do `mlflow.db` e `mlruns`.

Comandos rápidos (executar a partir de `deploy`):

```bash
docker compose build
docker compose up -d
docker compose logs -f
```

Persistência:
- `./mlflow.db` (SQLite) será montado em `/app/mlflow.db` no container MLflow.
- `./mlruns` será montado em `/app/mlruns` para artefatos do MLflow.

Próximos passos: construir as imagens e iniciar o `docker-compose`. Posso executar a construção e o `up` localmente se você autorizar.
