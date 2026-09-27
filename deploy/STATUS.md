# 📊 Status de Deployment: datathon-8mlet-grupo-04

## 🔴 LOCAL (Docker Compose)

**Status:** ✅ DESLIGADO (2026-09-19 21:54)

```
FastAPI:    ✓ Parado
MLflow:     ✓ Parado
Network:    ✓ Removida
```

**Como Ligar:**
```bash
./deploy/scripts/docker-control.sh up

# Ou
docker compose -f deploy/docker-compose.yml up -d
```

**Acesso (quando ligado):**
- API: http://localhost:8000
- MLflow: http://localhost:5002
- Docs: http://localhost:8000/docs

---

## ☁️ AWS (ECS)

**Status:** ✅ PAUSADO (para economizar)

```
Region:                us-east-2
Cluster:               datathon-bandit-cluster
FastAPI Service:       desired_count = 0 (pausado)
MLflow Service:        desired_count = 0 (pausado)
```

**Custo Economizado:** ~R$ 270/mês

**Como Retomar (caro!):**
```bash
./deploy/scripts/ecs-control.sh resume

# Ou manualmente:
aws ecs update-service --cluster datathon-bandit-cluster \
  --service datathon-bandit-fastapi --desired-count 1 --region us-east-2
aws ecs update-service --cluster datathon-bandit-cluster \
  --service datathon-bandit-mlflow --desired-count 1 --region us-east-2
```

**Acesso (quando ligado):**
- API: http://datathon-alb-xxx.us-east-2.elb.amazonaws.com
- MLflow: http://datathon-alb-xxx.us-east-2.elb.amazonaws.com:5000

---

## 📋 Scripts Disponíveis

### Menu Interativo
```bash
./deploy/scripts/control.sh
```

### Controle Local
```bash
./deploy/scripts/docker-control.sh [up|down|pause|unpause|status|logs|restart|rebuild|clean]
```

### Controle AWS
```bash
./deploy/scripts/ecs-control.sh [pause|resume|status|list]
```

---

## 🎯 Recomendações

### Para Este Fim de Semana
✅ **Use LOCAL (Docker Compose)**
- Gratuito
- Rápido (~5 min para subir)
- Ideal para desenvolvimento/testes
- Documentação completa em `/doc/`

### Para Produção Real
⚠️ **Será necessário retomar AWS (ECS)**
- Custará ~R$ 270/mês
- Alta disponibilidade (99.9%)
- Auto-escalável
- Monitoramento com CloudWatch

---

## 📈 Timeline

| Data | Ação | Custo |
|------|------|-------|
| 2026-09-19 21:54 | Docker Compose DOWN | R$ 0 |
| 2026-09-19 | ECS PAUSED | R$ 0 |
| Quando necessário | ECS UP | ~R$ 270/mês |

---

## 🔧 Verificar Status Agora

```bash
# Local
docker ps

# AWS (se tenho credenciais)
aws ecs describe-services \
  --cluster datathon-bandit-cluster \
  --services datathon-bandit-fastapi datathon-bandit-mlflow \
  --region us-east-2 \
  --query 'services[*].[serviceName,desiredCount,runningCount]' \
  --output table
```

---

**Última atualização:** 2026-09-19 21:54
**Responsável:** Group-04
**Status:** ✅ Tudo pausado (economizando)
