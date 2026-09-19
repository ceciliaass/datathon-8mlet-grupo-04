# 🔧 Operações - Datathon Bandit (AWS)

Guia prático para rodar, manter e otimizar a infraestrutura na AWS.

---

## 📋 Índice

1. [Gerenciamento Diário](#gerenciamento-diário)
2. [Deploy de Nova Versão](#deploy-de-nova-versão)
3. [Troubleshooting](#troubleshooting)
4. [Monitoramento de Custos](#monitoramento-de-custos)
5. [Rotação de Desligamento](#rotação-de-desligamento)
6. [Checklist de Segurança](#checklist-de-segurança)

---

## 🔄 Gerenciamento Diário

### ✅ Iniciar Serviços

```bash
cd datathon-8mlet-grupo-04/deploy/aws
./manage-ecs.sh start
```

O script irá:
- Ligar FastAPI + MLflow
- Monitorar até ficarem online (~1-2 min)
- Exibir URLs dos endpoints

### ⏹️ Parar Serviços

```bash
./manage-ecs.sh stop
```

Desliga e monitora até ficarem offline. **Não deleta** a infraestrutura — apenas zera as tasks do ECS.

### 📊 Verificar Status

```bash
./manage-ecs.sh status
```

Retorna:
- Número de tasks desejadas vs. em execução
- Tarefas pendentes

**O que significa cada coluna:**
- `desired`: quantas tasks você quer
- `running`: quantas estão realmente em execução
- `pending`: quantas estão iniciando

### 🔍 Monitorar em Tempo Real

```bash
./manage-ecs.sh monitor
```

Monitora indefinidamente (Ctrl+C para sair). Útil quando você liga os serviços e quer acompanhar.

---

## 🚀 Deploy de Nova Versão

Cenário: você alterou o código (FastAPI ou MLflow) e quer colocar em produção.

### Opção A: Apenas Redeploy (mesma imagem)

Se mudou **apenas** código Python (não alterou Dockerfile):

```bash
cd datathon-8mlet-grupo-04/deploy/aws

# Reconstruir imagens
AWS_REGION=us-east-2 ./push_images.sh

# Forçar nova implantação (sem destruir/recriar containers)
export AWS_PROFILE=datathon AWS_REGION=us-east-2

aws ecs update-service \
  --cluster datathon-bandit-cluster \
  --service datathon-bandit-fastapi \
  --force-new-deployment

aws ecs update-service \
  --cluster datathon-bandit-cluster \
  --service datathon-bandit-mlflow \
  --force-new-deployment
```

Leva ~2-3 min. Os containers antigos são substituídos gradualmente (rolling deployment).

### Opção B: Atualizar Infraestrutura (Terraform)

Se mudou variáveis, segurança, alocação de recursos, etc:

```bash
cd datathon-8mlet-grupo-04/deploy/aws/terraform

# Review o que vai mudar
terraform plan

# Aplicar (com confirmação)
terraform apply
```

**⚠️ Importante:** Isso pode reiniciar os serviços. Faça durante janela de manutenção.

### Checklist Pré-Deploy

```bash
# 1. Verificar se está pausado (para não derrubar prod)
./manage-ecs.sh status

# 2. Rodar testes localmente
cd ../../..
pytest app/tests/  # se houver testes

# 3. Rodar Docker Compose localmente antes de subir
docker compose -f deploy/docker-compose.yml up -d
# ... testar ...
docker compose -f deploy/docker-compose.yml down

# 4. Build da imagem (sem push ainda)
docker build -f deploy/Dockerfile.fastapi -t datathon-bandit-fastapi:test .

# 5. Se tudo OK, fazer push
cd deploy/aws
AWS_REGION=us-east-2 ./push_images.sh

# 6. Ligar e validar
./manage-ecs.sh start
# Aguarde ~1-2 min
curl http://<alb-dns>/health
```

---

## 🐛 Troubleshooting

### ❌ Problema: Serviços não ligam (ficam em Pending)

**Sintoma:** `./manage-ecs.sh start` monitora indefinidamente e não vai para `running`.

**Causas e soluções:**

#### 1. Imagem Docker não existe no ECR

```bash
# Verificar se as imagens estão no ECR
aws ecr describe-images \
  --repository-name datathon-bandit-fastapi \
  --region us-east-2

aws ecr describe-images \
  --repository-name datathon-bandit-mlflow \
  --region us-east-2
```

Se retornar vazio → reconstruir e fazer push:

```bash
cd deploy/aws
AWS_REGION=us-east-2 ./push_images.sh
```

#### 2. Task definition desatualizada

```bash
# Checar qual task definition está em uso
aws ecs describe-services \
  --cluster datathon-bandit-cluster \
  --services datathon-bandit-fastapi \
  --query 'services[0].taskDefinition' \
  --region us-east-2

# Forçar nova implantação (apanha task definition mais recente)
aws ecs update-service \
  --cluster datathon-bandit-cluster \
  --service datathon-bandit-fastapi \
  --force-new-deployment \
  --region us-east-2
```

#### 3. Recurso insuficiente (memória/CPU no Fargate)

```bash
# Ver logs do Fargate
aws logs tail /ecs/datathon-bandit-fastapi --follow --region us-east-2
```

Se vir "OOM Killed" → aumentar memória em `terraform/ecs.tf`:

```hcl
memory = 1024  # de 512 para 1024
```

Depois: `terraform apply`

#### 4. Secrets Manager com problema

```bash
# Validar se a senha do RDS está no Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id datathon-bandit-rds-password \
  --region us-east-2
```

Se falhar, recriar:

```bash
cd terraform
terraform taint aws_secretsmanager_secret.rds_password
terraform apply
```

### ❌ Problema: Endpoint retorna 503 Service Unavailable

**Sintoma:** `curl http://<alb-dns>/health` retorna 503.

**Causas:**

#### 1. Serviço está pausado

```bash
./manage-ecs.sh status
# Se `running` for 0, ligar com:
./manage-ecs.sh start
```

#### 2. Health check está falhando

```bash
# Ver logs da task
aws logs tail /ecs/datathon-bandit-fastapi --follow --region us-east-2

# Procurar por erros de conexão (DB, DynamoDB, etc)
```

Se o problema for RDS/DynamoDB, checar security groups:

```bash
# Listar security groups das tasks
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=*datathon*" \
  --region us-east-2 --output table
```

Validar que a task pode alcançar RDS:

```bash
# Dentro de um container ECS, testar:
# nc -zv <rds-endpoint> 5432
```

### ❌ Problema: API conecta mas retorna erro 500

**Sintoma:** `/recomendar` retorna erro 500.

**Debug:**

```bash
# Ver logs detalhados
aws logs tail /ecs/datathon-bandit-fastapi --follow --region us-east-2

# Procurar por stack trace (py traceback)
```

**Comum:**
- DynamoDB inacessível → verificar security group + credenciais IAM
- RDS inacessível → verificar credenciais Secrets Manager + IP da task
- Arm_stats.csv não encontrado → S3 permissões

Solução rápida: redeploy

```bash
./manage-ecs.sh stop
sleep 10
./manage-ecs.sh start
```

### ❌ Problema: MLflow UI não carrega

**Sintoma:** `curl http://<alb-dns>:5000/` retorna erro.

**Debug:**

```bash
# Verificar if MLflow está running
aws ecs describe-services \
  --cluster datathon-bandit-cluster \
  --services datathon-bandit-mlflow \
  --query 'services[0].[runningCount,desiredCount]' \
  --region us-east-2

# Se desiredCount=1 mas runningCount=0, ver logs
aws logs tail /ecs/datathon-bandit-mlflow --follow --region us-east-2
```

**Common:**
- RDS lentinho (first startup) → aguardar ~30s
- Sem conexão a RDS → validar credentials + security group

---

## 💰 Monitoramento de Custos

### Verificar Custo Atual (AWS Console)

1. AWS Console → Billing → Cost Explorer
2. Filtrar por tags: `project=datathon-bandit`
3. Agrupar por serviço

### Estimativa Rápida

A cada **hora ligado**:
```
FastAPI Fargate:     ~$0.007
MLflow Fargate:      ~$0.007
ALB:                 ~$0.016
RDS db.t4g.micro:    ~$0.018
DynamoDB:            ~$0.002
S3 + ECR + Logs:     < $0.001
─────────────────────────────
Total por hora:      ~$0.051 (~$1.22/dia)
```

### Economizar Custos

#### ✅ Desligar quando não usar

```bash
./manage-ecs.sh stop
```

Economiza **~$0.04/hora** (FastAPI + MLflow + RDS residual).

#### ✅ Destruir completamente para pausas > 1 semana

```bash
cd deploy/aws/terraform
terraform destroy
```

Economiza **~$1.50/dia**.

Quando voltar a usar:
```bash
terraform apply
./push_images.sh
./manage-ecs.sh start
```

#### ✅ Monitorar RDS

RDS é o componente mais caro. Se estiver muito ocioso:

```bash
# Reduzir de db.t4g.micro para db.t4g.nano (poupa ~50%)
# Editar terraform/rds.tf:
# instance_class = "db.t4g.nano"
terraform apply
```

Ou pausar RDS manualmente (sem Terraform):

```bash
aws rds stop-db-instance \
  --db-instance-identifier datathon-bandit-rds \
  --region us-east-2

# Retomar:
aws rds start-db-instance \
  --db-instance-identifier datathon-bandit-rds \
  --region us-east-2
```

### Alertas de Custo (CloudWatch)

Para ser notificado se o custo ultrapassar $50/mês:

```bash
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget BudgetName=datathon-bandit,BudgetLimit='{Amount=50,Unit=USD}',TimeUnit=MONTHLY,BudgetType=COST \
  --notifications-with-subscribers \
    NotificationWithSubscribers='Notification={NotificationType=FORECASTED,ComparisonOperator=GREATER_THAN,Threshold=100},Subscribers=[{SubscriptionType=EMAIL,Address=seu-email@example.com}]'
```

---

## 🔄 Rotação de Desligamento

**Cenário:** Você quer desligar os serviços no final do dia e ligá-los automaticamente no começo do dia seguinte.

### Opção 1: Manual (Mais Controle)

```bash
# Fim do dia
cd ~/projetos_new/datathon-8mlet-grupo-04/deploy/aws
./manage-ecs.sh stop
# Economiza ~$1.20

# Manhã seguinte
./manage-ecs.sh start
```

**Vantagem:** Total controle, fácil de revisar.
**Desvantagem:** Depende de você rodar manualmente.

### Opção 2: Automático com Cron (Recomendado)

```bash
# Editar crontab
crontab -e

# Adicionar essas linhas:

# Liga às 08:00 (segunda-sexta)
0 8 * * 1-5 cd ~/projetos_new/datathon-8mlet-grupo-04/deploy/aws && ./manage-ecs.sh start >> ~/datathon-ecs.log 2>&1

# Desliga às 18:00 (segunda-sexta)
0 18 * * 1-5 cd ~/projetos_new/datathon-8mlet-grupo-04/deploy/aws && ./manage-ecs.sh stop >> ~/datathon-ecs.log 2>&1
```

Testar:
```bash
# Ver logs
tail -f ~/datathon-ecs.log
```

### Opção 3: Automático com AWS Events + Lambda

Para escala maior (não é necessário para um datathon):

```bash
# EventBridge Rule: dispara Lambda todo dia às 18h
# Lambda Action: rodinha os comandos AWS CLI para desligar
```

**Não recomendado para este projeto** — complexidade alta, mais um serviço para pagar/manter.

---

## 🔒 Checklist de Segurança

### ✅ Antes de Ligar para Demo Pública

- [ ] MLflow UI **sem autenticação** — OK para demo curta, mas avisar que não é produção
- [ ] Sem HTTPS (só HTTP) — Avisar que é HTTP, não sensível
- [ ] Secrets Manager contém senha RDS? → `aws secretsmanager list-secrets --region us-east-2`
- [ ] IAM policy do usuário de deploy é a mínima necessária? → Revisar `iam/deploy-user-policy.json`
- [ ] Security groups bloqueiam acesso não autorizado?
  ```bash
  aws ec2 describe-security-groups --region us-east-2 | grep -A5 datathon
  ```
- [ ] RDS não está com backup desabilitado (skip_final_snapshot)?
  - Sim, está desabilitado no Terraform (aceitável para demo)

### ✅ Antes de Destruir

- [ ] Backup de dados importantes? (DynamoDB, RDS)
  ```bash
  # Exportar dados do DynamoDB
  aws dynamodb scan --table-name datathon-bandit-bandit-arms \
    --region us-east-2 > backup-arms-$(date +%Y%m%d).json
  ```
- [ ] Logs salvos? (CloudWatch)
  ```bash
  aws logs describe-log-groups --region us-east-2 | grep datathon
  ```
- [ ] ECR: Apagar imagens de teste?
  ```bash
  aws ecr describe-images --repository-name datathon-bandit-fastapi --region us-east-2
  ```

### ✅ Pós-Destruição

Verificar se não ficou orphan:

```bash
# Clusters ECS (deve estar vazio)
aws ecs list-clusters --region us-east-2

# Load Balancers
aws elbv2 describe-load-balancers --region us-east-2

# RDS (deve estar vazio)
aws rds describe-db-instances --region us-east-2

# DynamoDB (deve estar vazio)
aws dynamodb list-tables --region us-east-2

# S3 (procurar por datathon-bandit)
aws s3 ls | grep datathon
```

Se algo permanecer, pode ser deletado manualmente ou através do console.

---

## 📞 Referências Rápidas

### Comandos Frequentes

```bash
# Status
./manage-ecs.sh status

# Ligar
./manage-ecs.sh start

# Desligar
./manage-ecs.sh stop

# Ver logs FastAPI
aws logs tail /ecs/datathon-bandit-fastapi --follow --region us-east-2

# Ver logs MLflow
aws logs tail /ecs/datathon-bandit-mlflow --follow --region us-east-2

# Testar API
ALB=$(terraform -chdir=deploy/aws/terraform output -raw alb_dns_name)
curl http://$ALB/health
curl -X POST http://$ALB/recomendar \
  -H 'Content-Type: application/json' \
  -d '{"idade":35,"poutcome":"unknown","previous":1}'
```

### Links Úteis

- 📊 **Cost Explorer:** https://console.aws.amazon.com/costexplorer/
- 📋 **CloudWatch Logs:** https://console.aws.amazon.com/logs/
- 🐳 **ECR:** https://console.aws.amazon.com/ecr/ (região us-east-2)
- ⚡ **ECS:** https://console.aws.amazon.com/ecs/ (região us-east-2)
- 🔑 **Secrets Manager:** https://console.aws.amazon.com/secretsmanager/

---

## 📝 Log de Operações (Exemplo)

Manter um registro é útil:

```
2026-09-19 08:00 — Ligado para Demo Day (./manage-ecs.sh start)
2026-09-19 14:30 — Redeploy de nova versão (push_images.sh + force-new-deployment)
2026-09-19 18:00 — Desligado (./manage-ecs.sh stop) — Custo: ~$1.20
```

Adicionar ao `~/.zshrc`:

```bash
datathon_log() {
  echo "$(date '+%Y-%m-%d %H:%M') — $@" >> ~/datathon-operations.log
  cat ~/datathon-operations.log | tail -10
}

# Uso:
datathon_log "Ligado para teste"
```

---

**Última atualização:** 2026-09-19  
**Próximo review:** Quando realizar primeiro deploy pós-launch

