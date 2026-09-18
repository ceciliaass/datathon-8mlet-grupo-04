# 📋 Plano de Execução - MLe Tech Challenge 5: Datathon

## 🎯 Objetivo

Desenvolver uma **plataforma de experimentação adaptativa** usando **Thompson Sampling** (Multi-Armed Bandit, via MABWiser) para personalização de canal de oferta financeira em tempo real, com baseline determinístico para comparação.

---

## 📊 Status Geral

| Etapa | Objetivo | Status | Progresso |
|------|----------|--------|-----------|
| **Etapa 0** | Organização & Setup | ✅ Completa | 100% |
| **Etapa 1** | Base Kaggle & EDA | ✅ Completa | 100% |
| **Etapa 2** | Preparação da Base | ✅ Completa | 100% |
| **Etapa 3** | Baseline + Thompson Sampling | ✅ Completa | 100% |
| **Etapa 4** | Avaliação & Golden Set | ✅ Completa | 100% |
| **Etapa 5** | Serviço Demonstrável (API) | ✅ Completa | 100% |
| **Etapa 6** | Arquitetura Cloud | ✅ Completa (AWS) | 100% |
| **Etapa 7** | Ciclo de Vida MLOps (MLflow) | ✅ Completa (verificada via Docker Compose) | 100% |
| **Etapa 8** | Demo Day & Vídeo Pitch | ⏳ Não iniciado | 0% |

**Última verificação:** 2026-09-17, a partir do estado real do código (não apenas da documentação).

---

## ✅ ETAPA 0: Organização & Setup

### Status: ✅ COMPLETA

#### Executados
- ✅ Repositório GitHub criado: `https://github.com/vagnerasilva/mle_tech_chalenge_5`
- ✅ Estrutura de pastas completa (`src/`, `app/`, `deploy/`, `notebooks/`, `doc/`)
- ✅ `.gitignore` configurado para excluir dados, modelos, credenciais
- ✅ `requirements.txt` (raiz) + `app/requirements.txt` (serviço)
- ✅ `.env.example` criado
- ✅ `.python-version` = 3.12
- ✅ `.kaggle/KAGGLE_SETUP.md` com guia completo
- ✅ Documentação em `doc/` (briefing oficial em `doc/datathon.md`)

---

## ✅ ETAPA 1: Base Kaggle & EDA

### Status: ✅ COMPLETA

- ✅ Base escolhida: **Bank Marketing** ([henriqueyamahata](https://www.kaggle.com/datasets/henriqueyamahata/bank-marketing), ~41k registros)
- ✅ `notebooks/01_EDA.ipynb`: download com cache, exploração de distribuição/correlações, análise de missings/outliers
- ✅ **Vazamento temporal tratado:** `duration` removida; `pdays`, `previous`, `poutcome` mantidas como histórico pré-contato
- ✅ Encoding categórico + normalização (`StandardScaler`)
- ✅ Módulo `src/data_processing.py` com funções reutilizáveis de EDA/pipeline

### Pendente
- [ ] Confirmar que o link da base Kaggle está destacado no README principal (Etapa 1 do enunciado pede isso explicitamente)

---

## ✅ ETAPA 2: Preparação da Base

### Status: ✅ COMPLETA

- ✅ `notebooks/02_Preparacao_da_Base.ipynb`: features do cliente e variável alvo prontas para o modelo
- ✅ Dados processados salvos em `data/processed/bank-term-deposit-subscription_eda/`

---

## ✅ ETAPA 3: Baseline + Thompson Sampling

### Status: ✅ COMPLETA

- ✅ `notebooks/03_Baseline_e_Thompson.ipynb`: baseline determinístico (regra fixa) implementado
- ✅ Algoritmo adaptativo escolhido: **Thompson Sampling** (via [MABWiser](https://github.com/fidelity/mabwiser)), não Epsilon-Greedy como planejado originalmente
- ✅ Métrica do adaptativo comparada e superando o baseline
- ✅ Mesmo bandit (estado inicial via `arm_stats.csv`) reaproveitado depois pela API (Etapa 5), garantindo consistência notebook → serviço

> Nota: o README principal ainda cita "Epsilon-Greedy" no título/badges — desatualizado frente à escolha real (Thompson Sampling). Ajustar na próxima atualização do README.

---

## ✅ ETAPA 4: Avaliação & Golden Set

### Status: ✅ COMPLETA

- ✅ `notebooks/04_Avaliacao_e_Golden_Set.ipynb`: métricas de avaliação do modelo
- ✅ Golden Set com casos de teste de clientes e validação manual de coerência das recomendações

---

## ✅ ETAPA 5: Serviço Demonstrável (API FastAPI)

### Status: ✅ COMPLETA

Serviço real em `app/` (ver `app/README.md` para detalhes), não apenas planejado:

- ✅ `GET /health` — checagem de disponibilidade
- ✅ `POST /recomendar` — recebe contexto do cliente, devolve `decision_id` + braço escolhido (canal: `cellular`/`telephone`)
- ✅ `POST /feedback` — recebe `decision_id` + conversão, atualiza o bandit (404 se `decision_id` não existe, 409 se já teve feedback)
- ✅ `GET /stats` — observações/conversões/taxa por braço
- ✅ Persistência do estado do bandit em disco (`data/bandit_state.pkl`), sobrevive a reinícios
- ✅ Log de decisões append-only (`data/decisions_log.jsonl`) como trilha de auditoria
- ✅ Lock para concorrência entre requisições simultâneas
- ✅ Deploy containerizado: `deploy/Dockerfile.fastapi`, `deploy/Dockerfile.mlflow`, `deploy/docker-compose.yml` com healthchecks (FastAPI em `:8000`, MLflow UI em `:5002`)

### Limitações já documentadas (`app/README.md`)
- Ainda não é contextual (ignora `client_context` na escolha do braço — próximo passo natural seria `LearningPolicy.LinTS`)
- Persistência em arquivo local, não em store compartilhado (ok para 1 réplica)
- Sem autenticação/rate limiting (fora do escopo do datathon)

### Pendente
- [ ] Branch `feature/deploy` (onde vive todo o trabalho de Docker/deploy) ainda não foi mergeada em `main` — decidir e abrir PR

---

## ✅ ETAPA 6: Arquitetura-Alvo em Nuvem

### Status: ✅ COMPLETA E IMPLANTADA DE VERDADE — Provedor: **AWS** (região `us-east-2`)

Foi além do exigido pelo enunciado (que pede só 1-2 parágrafos documentando a arquitetura): a arquitetura foi **implementada em Terraform e implantada de verdade na AWS**, com todos os endpoints validados ponta a ponta (não é só um desenho).

- ✅ Seção "☁️ Arquitetura-Alvo em Nuvem (AWS)" no `README.md` principal
- ✅ `notebooks/06_Arquitetura_Cloud.ipynb` referencia a decisão e resume os serviços
- ✅ **Terraform completo** em `deploy/aws/terraform/` (17 arquivos `.tf`) provisionando:
  - **Compute:** ECR + ECS Fargate (ARM64/Graviton) atrás de um Application Load Balancer (porta 80 = FastAPI, porta 5000 = MLflow UI)
  - **Dados:** S3 (artifact store do MLflow)
  - **Estado do bandit:** DynamoDB (tabelas `bandit-arms` e `bandit-decisions`, com seed automático via Terraform usando os números reais do warm start)
  - **MLflow backend:** RDS PostgreSQL (substitui o SQLite local)
  - **Observabilidade:** CloudWatch Logs
  - **Segredos:** Secrets Manager (credenciais do RDS, injetadas na task via `secrets` do ECS, nunca em texto plano)
  - **IAM:** política dedicada para o usuário de deploy em `deploy/aws/iam/deploy-user-policy.json` (escopada por serviço/ARN, sem `AdministratorAccess`)
- ✅ **Validado end-to-end na infra real**: `/recomendar` → `/feedback` → `/stats` respondendo via DynamoDB, MLflow UI acessível, contadores do bandit batendo com o warm start + as chamadas de teste
- ✅ Runbook completo (deploy, verificação, pausa sem destruir, teardown, custo estimado) em `deploy/aws/README.md`

### Bugs reais encontrados e corrigidos durante o deploy (não eram visíveis rodando só localmente)
1. **FastAPI aceitava a conexão mas nunca respondia** (sem nenhum log de acesso) — incompatibilidade sutil do `uvloop`/`httptools` (padrão do `uvicorn[standard]`) no Fargate ARM64/Graviton. Corrigido forçando `--loop asyncio --http h11` (Python puro) no `Dockerfile.fastapi`.
2. **MLflow rejeitava com 403** — o healthcheck do Target Group da ALB usa o IP interno da task (dinâmico) como Host header, que não cabe numa allowlist estática de `--allowed-hosts`. Resolvido com um `*` na lista.
3. **MLflow morria com `OutOfMemoryError`** (exit 137) — 512MB não bastava com múltiplos workers; reduzido para `--workers 1` e memória subida para 2048MB.
4. **Corrida de dependência no Terraform**: o serviço ECS do MLflow podia subir antes do valor do secret existir no Secrets Manager (a task definition referenciava o secret "container", não a versão com o valor) — corrigido com `depends_on` explícito.
5. **Sem `health_check_grace_period_seconds`**: o ECS matava as tasks antes delas terminarem de subir, gerando loop de restart. Configurado 90s (FastAPI) e 120s (MLflow).
6. **`mlflow.set_experiment()` sem tratamento de erro** no `app/main.py` podia derrubar a API inteira se o MLflow ainda não estivesse de pé — envolvido em try/except (mesmo padrão já usado em `_log_recommendation`/`_log_feedback`).

### Notas
- Região escolhida (`us-east-2`, Ohio) por custo, não latência — variável (`var.aws_region`) fácil de trocar
- Justificativa de troca (pickle → DynamoDB, SQLite → RDS) explicitamente ligada às limitações já documentadas em `app/README.md`
- Diagrama não foi criado (opcional pelo enunciado)
- **Controle de custo**: stack pode ser pausado (`desired_count=0` nos serviços ECS, ~1-2min pra voltar) ou destruído por completo (`terraform destroy`, ~US$0 parado) — ver `deploy/aws/README.md`

---

## ✅ ETAPA 7: Ciclo de Vida MLOps (MLflow)

### Status: ✅ COMPLETA — verificada rodando o Docker Compose local

Correção em relação à avaliação anterior: o tracking da Etapa 7 **não** está no notebook `07_MLflow_Tracking.ipynb` (que é de fato só um stub) — ele está implementado dentro do próprio `03_Baseline_e_Thompson.ipynb`, numa seção chamada "Etapa 7 - Tracking com MLflow". Achado ao inspecionar o banco `mlflow.db` diretamente.

- ✅ Experimento `datathon-bandit-canal` (run `etapa3_baseline_vs_thompson`) registra exatamente o que a Etapa 3 pede:
  - **Params:** `dataset`, `arms`, `baseline_policy` ("regra fixa (sempre telephone)"), `algoritmo_adaptativo` ("MABWiser ThompsonSampling"), `seed`, `test_size`, `contextual_rate_prior_weight`, `best_arm_oracle_referencia`
  - **Métricas:** `baseline_conversion` (10,44%), `thompson_conversion` (13,67%), `conversion_lift_pp` (+3,23pp), `conversion_lift_relative_pct` (+30,95%), distribuição de escolhas por braço
  - Artefatos anexados: figura de conversão acumulada + resultados/metrics em CSV/JSON
- ✅ Experimento `datathon-bandit-app` registra runs de produção (`recomendacao`/`feedback`) vindos do `app/main.py` em tempo real
- ✅ **Validado em 2026-09-17** subindo `deploy/docker-compose.yml` (build + up) e consultando a API do MLflow (`GET /api/2.0/mlflow/runs/get`) — o run da Etapa 3 aparece com todos os params/métricas acima, servido pelo container em `http://localhost:5002`

### 🐛 Bugs de deploy corrigidos durante essa validação
Os healthchecks do `docker-compose.yml` reportavam `unhealthy` mesmo com os serviços respondendo corretamente. Duas causas raiz, corrigidas em `deploy/Dockerfile.fastapi` e `deploy/Dockerfile.mlflow`:
1. **`curl` não estava instalado** nas imagens Ubuntu — o healthcheck (`CMD-SHELL curl -f ...`) sempre falhava com "curl: not found". Adicionado `curl` à lista de pacotes `apt-get install` nos dois Dockerfiles.
2. **MLflow rejeitava o Host header do healthcheck** (proteção anti DNS-rebinding): a lista `--allowed-hosts` não incluía `127.0.0.1:5000` (com porta), só `127.0.0.1` sem porta. Ajustado o `CMD` do `Dockerfile.mlflow` para incluir as variantes com porta.

Após as correções, `docker compose ps` mostra os dois serviços como `healthy`.

### Nota / possível próximo passo (não bloqueia a etapa)
- O `experiment_id=1` (`datathon-bandit-canal`) tem `artifact_location` apontando para um caminho absoluto do host (`.../notebooks/mlruns/1`) porque foi criado rodando o notebook localmente, fora do container. Os **params e métricas** aparecem normalmente na UI/API servida pelo container; só a aba de **artefatos** desse experimento específico pode não resolver dentro do container. Não afeta o requisito da Etapa 7 (registrar params/métricas), mas vale registrar como limitação conhecida.

### Inicialização do servidor MLflow (local)

```bash
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5000
```

A interface estará disponível em `http://localhost:5000` (ou `:5002` via Docker Compose, ver `deploy/README.md`).

---

## ❌ ETAPA 8: Demo Day & Vídeo Pitch

### Status: ❌ Não iniciado

- ⚠️ `notebooks/08_Demo_Day.ipynb` é apenas um checklist que verifica se artefatos existem em disco — não é o roteiro/demo em si
- ❌ Vídeo pitch (até 5 min) ainda não gravado

### Deliverables pendentes
- [ ] Roteiro de até 5 minutos: problema de negócio → modelo (Thompson Sampling) → Etapa 5 (API) rodando na prática
- [ ] Gravação e edição do vídeo

---

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologia | Versão |
|-----------|------------|--------|
| **Python** | Python | 3.12+ |
| **Data** | Pandas, NumPy | 2.1+, 1.25+ |
| **ML** | Scikit-learn | 1.4+ |
| **Visualização** | Matplotlib, Seaborn | 3.8+, 0.13+ |
| **Notebooks** | Jupyter | 1.0+ |
| **API** | FastAPI | 0.105+ |
| **Bandit** | MABWiser (Thompson Sampling) | — |
| **MLOps** | MLflow | 2.10+ |
| **Deploy** | Docker / Docker Compose | — |
| **Config** | Python-dotenv, PyYAML | 1.0+, 6.0+ |

---

## 📊 Progresso Visual

```
Etapa 0 (Organização):        ████████████████████ 100% ✅
Etapa 1 (EDA):                ████████████████████ 100% ✅
Etapa 2 (Preparação):         ████████████████████ 100% ✅
Etapa 3 (Baseline+Thompson):  ████████████████████ 100% ✅
Etapa 4 (Avaliação/Golden):   ████████████████████ 100% ✅
Etapa 5 (API/Serviço):        ████████████████████ 100% ✅
Etapa 6 (Cloud):              ████████████████████ 100% ✅
Etapa 7 (MLflow):             ████████████████████ 100% ✅
Etapa 8 (Demo Day):           ░░░░░░░░░░░░░░░░░░░░   0% ❌
─────────────────────────────────────────────────
Total:                        ██████████████████░░  89% 🚀
```

Falta apenas a Etapa 8 (vídeo pitch) para fechar as 9 etapas do enunciado.

---

## 🎯 Próximas Prioridades

### Imediato
1. ⏳ Etapa 8 — escrever roteiro do vídeo pitch (≤5 min) mostrando a Etapa 5 (API) rodando via Docker Compose, com a comparação baseline vs. Thompson Sampling da Etapa 3/7
2. 📝 Atualizar o restante do `README.md` principal para refletir o progresso real (badge/tabela de status ainda diz "Fase 1" / Epsilon-Greedy, desatualizados)

### Curto Prazo
1. ⏳ Decidir sobre merge da branch `feature/deploy` → `main` (é onde vivem as correções de Dockerfile feitas hoje)
2. ⏳ Gravar e editar o vídeo pitch

### Antes do Demo Day
1. ⏳ Passar pelo checklist oficial do enunciado (`doc/datathon.md`) item a item

---

## 📞 Configuração Kaggle

**Status:** ✅ Pronto

Para começar, configure Kaggle:
```bash
# Guia em: .kaggle/KAGGLE_SETUP.md

# Quick setup:
1. Acesse: https://www.kaggle.com/settings/account
2. Gere token API
3. Configure: ~/.kaggle/kaggle.json
4. Teste: kaggle datasets list
```

---

## 📌 Notas Importantes

- ✅ Python 3.12+ obrigatório
- ✅ Gitignore configurado para não subir dados
- ✅ Cache automático para evitar re-downloads
- ✅ Base Kaggle (Bank Marketing) testada e funcionando
- ✅ Algoritmo adaptativo real: **Thompson Sampling** (não Epsilon-Greedy — o README principal ainda precisa ser corrigido nesse ponto)
- ✅ API de serviço (Etapa 5) já em produção local via Docker Compose, com persistência e log de auditoria
- ⚠️ Trabalho de deploy vive na branch `feature/deploy`, ainda não mergeado em `main`
- ✅ Etapa 6 resolvida com **AWS** como provedor-alvo (ECS Fargate, S3, DynamoDB, RDS, CloudWatch)
- ✅ Etapa 7 (MLflow) confirmada e validada rodando `docker compose up` localmente — params/métricas da Etapa 3 registrados corretamente
- 🐛 Corrigidos 2 bugs de healthcheck no deploy Docker (curl ausente + allowed-hosts do MLflow) encontrados durante essa validação
- ❌ Falta apenas: vídeo pitch (Etapa 8)

---

**Última atualização:** 2026-09-17
**Responsável:** Claude Code (a partir da inspeção do código, commits reais e execução local do `docker-compose`)
**Status Geral:** ~89% Completo (Etapas 0-7 prontas e verificadas; 8 pendente) 🚀
