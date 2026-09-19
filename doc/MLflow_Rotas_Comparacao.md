# Rota A vs Rota B: Qual Escolher?

## 🎯 Quick Decision

| Pergunta | Resposta → Rota |
|----------|---|
| Quer fazer demo em um hackathon? | **→ Rota A (Local)** |
| Precisa de infraestrutura profissional? | **→ Rota B (AWS)** |
| Quer zero custo? | **→ Rota A (Local)** |
| Precisa de alta disponibilidade (99.9%)? | **→ Rota B (AWS)** |
| Quer escalabilidade automática? | **→ Rota B (AWS)** |
| Quer algo rápido para apresentar? | **→ Rota A (Local)** |
| Será usado em produção? | **→ Rota B (AWS)** |

---

## 🏠 ROTA A: Docker Compose (Local)

### Visualização

```
Seu Laptop / Servidor Local
┌──────────────────────────────────────────────────────┐
│                                                      │
│  docker-compose.yml (1 arquivo, tudo aqui!)        │
│  ├─ MLflow Service                                  │
│  │  ├─ Backend: SQLite (mlflow.db)                  │
│  │  ├─ Artifacts: mlruns/                          │
│  │  └─ Port: 5002                                   │
│  │                                                  │
│  └─ FastAPI Service                                │
│     ├─ Carrega modelo do MLflow                    │
│     ├─ /recomendar endpoint                        │
│     └─ Port: 8000                                  │
│                                                      │
│  Data:                                              │
│  └─ mlruns/                                         │
│     ├─ Experimentos                                │
│     └─ Artifacts (models, CSVs, gráficos)         │
│                                                      │
└──────────────────────────────────────────────────────┘

Acesso:
  http://localhost:5002  → MLflow UI
  http://localhost:8000  → API
  http://{server_ip}:5002  → De outras máquinas
```

### O que você precisa fazer

```bash
# 1. Semanas 1-4 (treinar e validar localmente)
mlflow run . --entry-point train -P seed=42
# notebook 04: validar e promover para Production

# 2. Semana 5: Subir os containers
docker compose -f deploy/docker-compose.yml up -d

# 3. Pronto! Acessar:
# - MLflow: http://localhost:5002
# - API: http://localhost:8000/docs

# Se em servidor Linux:
# - Copiar projeto para servidor
# - Rodar: docker compose -f deploy/docker-compose.yml up -d
# - Acessar via IP do servidor
```

### Características

| Aspecto | Rota A |
|--------|--------|
| **Custo** | R$ 0 (grátis) |
| **Setup** | 5 minutos |
| **Uptime** | Enquanto máquina está ligada |
| **Replicas** | 1 (não escala) |
| **Monitoramento** | Logs locais (stdout) |
| **Backup** | Manual |
| **Auto-scaling** | Não |
| **CI/CD** | Manual (você roda scripts) |
| **Segurança** | Sem HTTPS (local), acesso por rede |
| **Melhor para** | Demo, Dev, Hackathon, Teste |

### Estrutura de Arquivos

```
datathon-8mlet-grupo-04/
├── mlflow.db                 ← Backend (criado automaticamente)
├── mlruns/                    ← Artifacts
│   ├── 0/                     ← Experimento 0
│   └── 1/                     ← Experimento 1
│
├── docker-compose.yml         ← Tudo que você precisa
├── deploy/
│   ├── Dockerfile.fastapi
│   ├── Dockerfile.mlflow
│   └── docker-compose.yml     ← Já existe!
│
├── src/
│   ├── train.py
│   └── evaluate.py
│
└── app/
    └── main.py
```

### Comandos Principais

```bash
# Subir
docker compose -f deploy/docker-compose.yml up -d

# Ver logs
docker compose -f deploy/docker-compose.yml logs -f fastapi
docker compose -f deploy/docker-compose.yml logs -f mlflow

# Parar
docker compose -f deploy/docker-compose.yml down

# Remover volumes (limpar tudo)
docker compose -f deploy/docker-compose.yml down -v

# Retreinar
mlflow run . --entry-point train -P seed=123

# Promover modelo
# Via UI: http://localhost:5002 → Models → transition stage
```

### Quando usar Rota A

✅ Desenvolvimento e testes  
✅ Demo em eventos/hackathons  
✅ Prototipagem rápida  
✅ Ambiente de teste local  
✅ Sem recursos AWS  
✅ Projeto pequeno/médio  

---

## ☁️ ROTA B: AWS (ECS + RDS + S3)

### Visualização

```
AWS (us-east-2)
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Application Load Balancer (ALB)               │  │
│  │                                                          │  │
│  │  http://alb-xxx.us-east-2.elb.amazonaws.com             │  │
│  │  ├─ :80 → FastAPI (auto-escalável, 3x replicas)        │  │
│  │  └─ :5000 → MLflow UI                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                     ↓ (ECS Fargate)                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           ECS Cluster (Containers Gerenciados)           │  │
│  │                                                          │  │
│  │  FastAPI Task                   MLflow Task             │  │
│  │  ├─ Replica 1                   └─ 1 instância         │  │
│  │  ├─ Replica 2                                           │  │
│  │  └─ Replica 3                                           │  │
│  │     (Auto-escalável: 2-5 based on CPU)                 │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ RDS PostgreSQL │  │      S3      │  │   DynamoDB       │  │
│  │                │  │              │  │                  │  │
│  │ • Backup 7d   │  │ • Artifacts  │  │ • Bandit state   │  │
│  │ • Multi-AZ    │  │ • Versionado │  │ • Decisões       │  │
│  │ • Failover    │  │ • Durável    │  │ • Escalável      │  │
│  │  automático   │  │              │  │                  │  │
│  └────────────────┘  └──────────────┘  └──────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              CloudWatch Logs + Métricas                  │  │
│  │                                                          │  │
│  │  • ECS logs (fastapi, mlflow)                           │  │
│  │  • CPU/Memory/Network metrics                           │  │
│  │  • Alertas automáticos                                  │  │
│  │  • Dashboard personalizado                              │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Acesso:
  http://alb-xxx.us-east-2.elb.amazonaws.com     → API
  http://alb-xxx.us-east-2.elb.amazonaws.com:5000 → MLflow
  CloudWatch: AWS Console
```

### O que você precisa fazer

```bash
# 1. Semanas 1-4 (igual à Rota A - treinar localmente)
mlflow run . --entry-point train -P seed=42
# notebook 04: validar e promover para Production

# 2. Semana 5: Deploy na AWS
cd deploy/aws/terraform

# Configurar credenciais AWS
aws configure

# Initialize Terraform
terraform init

# Ver o que vai criar
terraform plan

# Criar infraestrutura
terraform apply

# Outputs (URLs da sua API e MLflow)
terraform output

# 3. GitHub Actions (CI/CD automático)
# Adicione secrets no GitHub:
# - AWS_ACCOUNT_ID
# - AWS_REGION
# - AWS_ROLE_TO_ASSUME

# Agora a cada push:
# - GitHub Actions roda CI/CD
# - Treina novo modelo
# - Deploy automático
# - Rollback automático se falhar

# 4. Pronto! Acessar:
# - MLflow: http://alb-xxx.us-east-2.elb.amazonaws.com:5000
# - API: http://alb-xxx.us-east-2.elb.amazonaws.com
```

### Características

| Aspecto | Rota B |
|--------|--------|
| **Custo** | ~R$ 300-500/mês (RDS + ECS + S3) |
| **Setup** | 30 minutos primeira vez |
| **Uptime** | 99.9% (SLA AWS) |
| **Replicas** | 2-5 (auto-escalável) |
| **Monitoramento** | CloudWatch automático |
| **Backup** | Automático (7 dias RDS) |
| **Auto-scaling** | Sim (baseado em CPU/memória) |
| **CI/CD** | GitHub Actions automático |
| **Segurança** | HTTPS, IAM, Secrets Manager |
| **Melhor para** | Produção, Alta disponibilidade |

### Estrutura de Arquivos

```
datathon-8mlet-grupo-04/
├── deploy/aws/
│   └── terraform/
│       ├── main.tf                 ← VPC, subnets
│       ├── ecs.tf                  ← ECS Cluster, Services
│       ├── ecs_fastapi.tf           ← FastAPI Task Definition
│       ├── ecs_mlflow.tf            ← MLflow Task Definition
│       ├── rds.tf                  ← RDS PostgreSQL
│       ├── s3.tf                   ← S3 buckets
│       ├── alb.tf                  ← Application Load Balancer
│       ├── cloudwatch.tf            ← Logs e métricas
│       ├── iam.tf                  ← Roles e policies
│       ├── variables.tf             ← Configurações
│       └── terraform.tfvars         ← Valores específicos
│
├── .github/workflows/
│   └── mlflow-train-aws.yml        ← GitHub Actions CI/CD
│
├── src/
│   ├── train.py
│   └── evaluate.py
│
└── app/
    └── main.py
```

### Comandos Principais

```bash
# Terraform
cd deploy/aws/terraform

terraform init                    # Initialize
terraform plan                    # Ver mudanças
terraform apply                   # Deploy
terraform destroy                 # Remover (cuidado!)

# Pausar/Resumir (economizar custos)
aws ecs update-service \
  --cluster datathon-bandit-cluster \
  --service datathon-bandit-fastapi \
  --desired-count 0              # Pausar

aws ecs update-service \
  --cluster datathon-bandit-cluster \
  --service datathon-bandit-fastapi \
  --desired-count 1              # Resumir

# Ver logs
aws logs tail /ecs/fastapi --follow
aws logs tail /ecs/mlflow --follow

# Retreinar (trigger GitHub Actions)
git push  # Automático se schedule/manual

# Monitorar (CloudWatch)
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=datathon-bandit-fastapi
```

### Custo Estimado

```
Serviço              | Custo/mês
----------------------|----------
ECS Fargate          | ~R$ 150 (2x 0.5 GB)
RDS Aurora           | ~R$ 100 (db.t3.micro)
S3                   | ~R$ 5 (storage)
Data Transfer        | ~R$ 10
CloudWatch Logs      | ~R$ 5
----------------------|----------
TOTAL                | ~R$ 270
```

**Pode pausar fora de horário:** use `desired_count=0` para economizar.

### Quando usar Rota B

✅ Produção real  
✅ Alta disponibilidade exigida  
✅ Multi-replica necessário  
✅ Orçamento disponível  
✅ Monitoramento automático necessário  
✅ CI/CD integrado querido  
✅ Backup automático necessário  
✅ Projeto grande/crítico  

---

## 📊 Comparação Lado a Lado

```
                          ROTA A (Local)      ROTA B (AWS)
┌──────────────────────────┬─────────────────┬──────────────────┐
│ Aspecto                  │ Docker Compose  │ ECS + RDS + S3   │
├──────────────────────────┼─────────────────┼──────────────────┤
│ Custo                    │ R$ 0            │ R$ 270-500/mês   │
│ Setup                    │ 5 min           │ 30 min           │
│ Uptime                   │ Manual          │ 99.9% SLA        │
│ Auto-scaling             │ Não             │ Sim (2-5)        │
│ Replicas                 │ 1               │ 2-5              │
│ Backup                   │ Manual          │ Automático (7d)  │
│ Monitoramento            │ Nenhum          │ CloudWatch       │
│ CI/CD                    │ Manual          │ GitHub Actions   │
│ HTTPS                    │ Não             │ Sim (ALB)        │
│ Segurança                │ Básica          │ IAM + Secrets    │
│ Latência                 │ ~50ms local     │ ~100ms (internet)│
│ Multi-AZ                 │ Não             │ Sim              │
│ Failover automático      │ Não             │ Sim              │
│ Melhor para              │ Demo/Dev/Hack   │ Produção Real    │
└──────────────────────────┴─────────────────┴──────────────────┘
```

---

## 🚀 Recomendação por Caso de Uso

### Case 1: Hackathon / Demo
```
✅ ROTA A (Local)

Razão:
- Setup instantâneo (já tem docker compose)
- Zero custo
- Fácil de apresentar
- Deploy em qualquer laptop

Workflow:
1. Treinar localmente (Semanas 1-4)
2. docker compose up
3. Mostrar MLflow + API
4. Pronto para apresentar!
```

### Case 2: Projeto Acadêmico
```
✅ ROTA A (Local)

Razão:
- Sem orçamento
- Simplicidade
- Fácil de entender
- Tudo em um arquivo

Extra:
- Se precisar escalar depois → muda para Rota B
```

### Case 3: Produção em Empresa
```
✅ ROTA B (AWS)

Razão:
- Alta disponibilidade necessária
- Monitoramento profissional
- Backup automático
- CI/CD automático
- Time pode manter sem downtime

Bonus:
- Pause quando não usar para economizar
```

### Case 4: MVP / Prototipagem
```
🟡 ROTA A (Local) OU ROTA B (AWS)?

- Começa em ROTA A (desenvolvimento rápido)
- Se MVP virar produto → migra para ROTA B
  (código é 100% compatível entre as duas!)
```

---

## 🔄 Como Migrar de Rota A para Rota B?

Se você começa em Docker Compose (Rota A) e quer ir para AWS (Rota B):

```bash
# PASSO 1: Código já é compatível!
# Tudo que você tem em Rota A funciona em Rota B
# - SQLite → RDS PostgreSQL (mesmo formato)
# - mlruns/ → S3 (mesmo formato)
# - docker-compose.yml → Terraform (mesma app)

# PASSO 2: Build + Push imagens para ECR
docker build -f deploy/Dockerfile.fastapi -t fastapi:latest .
docker tag fastapi:latest {account}.dkr.ecr.us-east-2.amazonaws.com/fastapi:latest
docker push {account}.dkr.ecr.us-east-2.amazonaws.com/fastapi:latest

# Idem para MLflow

# PASSO 3: Aplicar Terraform
cd deploy/aws/terraform
terraform init
terraform apply

# PASSO 4: Pronto! Mesma API + MLflow, mas na AWS
# URLs mudam, mas comportamento é 100% igual
```

---

## ❓ FAQ

**P: Preciso rodar ambas as rotas em paralelo?**  
R: Não! Escolha uma. Código é 100% compatível, então pode mudar depois.

**P: Qual é mais fácil?**  
R: Rota A é mais fácil (docker compose já existe). Rota B é mais fácil depois que está setup.

**P: Posso voltar de AWS para Local?**  
R: Sim! Dados em RDS/S3 são compatíveis com SQLite/mlruns.

**P: Quanto custa a Rota B?**  
R: ~R$ 270/mês se sempre ligado. Mas você pode pausar com `desired_count=0`.

**P: E se quiser HTTPS em Rota A?**  
R: Use nginx na frente do docker compose (extra config).

**P: Qual é mais rápido?**  
R: Rota A é mais rápido (tudo local, ~50ms). Rota B tem latência de internet (~100ms).

---

## 🎯 Decisão Final

```
Fluxograma de Decisão:

┌─ É hackathon/demo?
│  ├─ SIM → ROTA A ✅
│  └─ NÃO → próxima
│
├─ É projeto acadêmico?
│  ├─ SIM → ROTA A ✅
│  └─ NÃO → próxima
│
├─ Precisa de produção?
│  ├─ SIM → ROTA B ✅
│  └─ NÃO → próxima
│
├─ Tem orçamento AWS?
│  ├─ SIM → ROTA B ✅
│  └─ NÃO → ROTA A ✅
```

**Lembrete:** Ambas as rotas usam as MESMAS semanas 1-4. Você apenas escolhe em qual infraestrutura rodar a semana 5!

---

**Dúvida? Consulte `MLflow_Jornada_Completa.md` para os detalhes técnicos!** 📖
