# Deploy AWS (Terraform)

Implementação real da seção "☁️ Arquitetura-Alvo em Nuvem (AWS)" do [README.md](../../README.md) principal: ECR + ECS Fargate + ALB, DynamoDB, RDS PostgreSQL, S3, CloudWatch e Secrets Manager. Ambiente de **demo de curta duração** (datathon, não produção) — o objetivo é subir perto do Demo Day, validar, e derrubar tudo em seguida (ver [Teardown](#teardown--controle-de-custo)).

## 🔴 Endpoints ao vivo (região `us-east-2`)

> Válidos enquanto o stack estiver de pé. Mudam a cada `terraform apply`/`destroy` (o DNS do ALB é recriado); depois de um `terraform destroy`, param de responder. Sem HTTPS e sem autenticação (ver [Notas de segurança](#notas-de-segurança-aceitas-ambiente-de-demo-curto)).

| Serviço | URL |
|---|---|
| **API FastAPI** (docs, `/recomendar`, `/feedback`, `/stats`, `/health`) | http://datathon-bandit-alb-361652049.us-east-2.elb.amazonaws.com |
| **MLflow UI** | http://datathon-bandit-alb-361652049.us-east-2.elb.amazonaws.com:5000 |

Para redescobrir o DNS atual a qualquer momento (ex.: depois de recriar o ALB):
```bash
terraform -chdir=deploy/aws/terraform output -raw alb_dns_name
```

## Estrutura

```
deploy/aws/
├── terraform/              # toda a infra (terraform init roda aqui)
├── push_images.sh          # build + push das imagens fastapi/mlflow para o ECR
├── seed_bandit_arms.py     # fallback opcional p/ resetar contadores do bandit sem reaplicar Terraform
├── iam/deploy-user-policy.json  # política IAM p/ o usuário que vai rodar este runbook
└── README.md                # este arquivo
```

## 0. Pré-requisitos

```bash
brew install terraform awscli
terraform -version   # >= 1.5
aws --version        # aws-cli/2.x
```

### Criar o usuário IAM de deploy

Não use `AdministratorAccess`. Este repo já traz a política com exatamente as permissões necessárias em [`iam/deploy-user-policy.json`](iam/deploy-user-policy.json) (escopada por serviço, e por prefixo `datathon-bandit-*` nos recursos que suportam permissão a nível de recurso — ARNs de DynamoDB, S3, Secrets Manager, CloudWatch Logs e IAM roles; EC2/ECS/ELB/RDS não suportam isso na maioria das ações e ficam com `Resource: "*"` mesmo assim).

No console AWS (ou via CLI):
1. IAM → Users → Create user (ex.: `datathon-deploy`), sem acesso ao console (só programático).
2. IAM → Policies → Create policy → aba JSON → cole o conteúdo de `iam/deploy-user-policy.json` → nome `datathon-bandit-deploy-policy`.
3. Anexe essa policy ao usuário `datathon-deploy`.
4. Security credentials → Create access key (tipo "CLI") → guarde Access Key ID/Secret.

> Se mudar `project_name` em `terraform/variables.tf` (default `datathon-bandit`), atualize também os prefixos `datathon-bandit-*` na policy JSON.

### Configurar credenciais localmente

```bash
aws configure --profile datathon
# Default region name: us-east-2
export AWS_PROFILE=datathon
aws sts get-caller-identity   # valida
```

## 1. Deploy

```bash
# 1) infra base — ECR primeiro, resolve a dependencia circular imagem<->servico ECS
cd deploy/aws/terraform
terraform init
terraform apply -target=aws_ecr_repository.fastapi -target=aws_ecr_repository.mlflow

# 2) build + push das imagens reais (raiz do repo)
cd ../../..
AWS_REGION=us-east-2 ./deploy/aws/push_images.sh

# 3) resto da infra (RDS, DynamoDB + seed, ALB, ECS services etc.)
cd deploy/aws/terraform
terraform apply

# 4) conferir
terraform output alb_dns_name
```

Redeploy de nova imagem sem mudar infra:
```bash
./deploy/aws/push_images.sh
aws ecs update-service --cluster datathon-bandit-cluster --service datathon-bandit-fastapi --force-new-deployment --region us-east-2
aws ecs update-service --cluster datathon-bandit-cluster --service datathon-bandit-mlflow  --force-new-deployment --region us-east-2
```

## 2. Verificação end-to-end

```bash
ALB=$(terraform -chdir=deploy/aws/terraform output -raw alb_dns_name)

curl -f "http://$ALB/health"
curl -s -X POST "http://$ALB/recomendar" -H 'Content-Type: application/json' -d '{"idade":35,"poutcome":"unknown","previous":1}'
# use o decision_id retornado acima:
curl -s -X POST "http://$ALB/feedback" -H 'Content-Type: application/json' -d '{"decision_id":"<id>","converteu":true}'
curl -s "http://$ALB/stats"
curl -f "http://$ALB:5000/"   # UI do MLflow
```

Confirme que os dados estão indo para a AWS de verdade (não é fallback local silencioso — o backend DynamoDB não tem fallback, mas vale conferir):
```bash
aws dynamodb scan --table-name datathon-bandit-bandit-arms --region us-east-2
aws dynamodb scan --table-name datathon-bandit-bandit-decisions --region us-east-2
aws s3 ls "s3://datathon-bandit-data-$(aws sts get-caller-identity --query Account --output text)/mlflow-artifacts/" --recursive
```
Na UI do MLflow, o experimento `datathon-bandit-app` deve ganhar runs novos correspondentes às chamadas acima.

## 2.1 Pausar sem destruir (fora do horário de dev/demo)

Zera as tasks do ECS — API e MLflow ficam inacessíveis (o ALB responde 503) em poucos segundos, sem destruir RDS/DynamoDB/S3/ALB. Custo residual pequeno enquanto pausado (ALB + RDS parado continuam cobrando, só o Fargate para); ideal para pausas de poucas horas dentro do mesmo dia. Para pausas mais longas (vários dias), prefira o [teardown completo](#teardown--controle-de-custo).

```bash
export AWS_PROFILE=datathon AWS_REGION=us-east-2

# Pausar
aws ecs update-service --cluster datathon-bandit-cluster --service datathon-bandit-fastapi --desired-count 0
aws ecs update-service --cluster datathon-bandit-cluster --service datathon-bandit-mlflow  --desired-count 0

# Retomar (mesmas imagens, sem rebuild)
aws ecs update-service --cluster datathon-bandit-cluster --service datathon-bandit-fastapi --desired-count 1
aws ecs update-service --cluster datathon-bandit-cluster --service datathon-bandit-mlflow  --desired-count 1
```

> `desired_count` aqui é alterado fora do Terraform. Se rodar `terraform apply` de novo enquanto estiver pausado, ele vai notar a diferença e voltar `desired_count` para `1` (o valor fixo no `ecs.tf`) — normal, é só reaplicar o `--desired-count 0` de novo se quiser continuar pausado.

## 3. Teardown / controle de custo

```bash
cd deploy/aws/terraform
terraform destroy
```

Já coberto para destruir limpo (sem precisar de passo manual): `force_delete`/`force_destroy` no ECR/S3, `skip_final_snapshot=true` no RDS, `recovery_window_in_days=0` no secret do Secrets Manager. Depois, confira que nada ficou órfão:
```bash
aws ecs list-clusters --region us-east-2
aws elbv2 describe-load-balancers --region us-east-2
aws rds describe-db-instances --region us-east-2
```

**Não apague `terraform.tfstate` antes de rodar `destroy`** — o state fica local (não versionado, ver `.gitignore`), é a única referência que o Terraform tem de tudo que foi criado.

## 4. Custo estimado (24/7, `us-east-2`)

| Recurso | ~US$/mês |
|---|---|
| ALB (fixo + LCU) | 20 |
| 2x Fargate ARM64 (0.25 vCPU/0.5GB) | 18-22 |
| RDS db.t4g.micro + 20GB gp3 | 15-18 |
| DynamoDB, S3, ECR, Secrets Manager, CloudWatch Logs | < 4 |
| NAT Gateway | 0 (evitado por design — tasks em subnet pública) |
| **Total** | **~55-65** |

Cobrado por hora — poucos dias ligado custam poucos dólares. Suba perto do Demo Day, demonstre, e rode o teardown na sequência.

## Notas de segurança aceitas (ambiente de demo curto)

- MLflow UI pública sem autenticação (restrinja com `var.alb_ingress_cidr` em `terraform/variables.tf` se quiser).
- Sem HTTPS/ACM/Route53 — tudo via HTTP no DNS do ALB.
- Tasks Fargate em subnet pública (com IP público) para evitar o custo fixo de um NAT Gateway; acesso de entrada continua restrito pelos Security Groups (`terraform/network.tf`).
