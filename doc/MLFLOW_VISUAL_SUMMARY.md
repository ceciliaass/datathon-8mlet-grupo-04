# 📊 MLflow Visual Summary - Tudo Em Um Lugar

## O Fluxo Completo: Do Notebook à Produção

### 1️⃣ Você treina no Notebook

```python
with mlflow.start_run(run_name="thompson_sampling_v2"):
    mlflow.log_param("alpha", 1)
    mlflow.log_metric("auc", 0.79)
    mlflow.sklearn.log_model(model, "model")
    mlflow.set_tag("ready_for_production", "true")
```

↓ **O que acontece automaticamente:**

```
Disco:
├── mlruns/
│   └── 0/
│       └── abc123def456/  ← Novo run ID
│           ├── params/
│           │   └── alpha → "1"
│           ├── metrics/
│           │   └── auc → 0.79
│           ├── tags/
│           │   └── ready_for_production → "true"
│           └── artifacts/model/
│               ├── model.pkl
│               └── MLmodel

Banco de dados:
mlflow.db → Registro novo: run_id=abc123def456, status=FINISHED
```

---

### 2️⃣ Você registra no MLflow (1 clique)

**Na UI em http://localhost:5000:**

```
┌─────────────────────────────────────────┐
│ Run: thompson_sampling_v2               │
│ ID: abc123def456                        │
│                                         │
│ [Register Model] ← Click aqui           │
│                                         │
│ Nome: thompson_bandit                   │
│ Versão: 1                               │
│ Stage: Staging (padrão)                 │
└─────────────────────────────────────────┘
```

**Resultado:**

```
mlruns/
├── models/
│   └── thompson_bandit/
│       └── version 1/
│           └── metadata.yaml
│               ├── name: thompson_bandit
│               ├── version: 1
│               ├── stage: Staging
│               └── source: runs:/abc123def456/model
```

---

### 3️⃣ Você promove para Production (1 clique)

**Na UI:**

```
Stage dropdown: "Staging" → "Production"
             ↓
mlflow.db é atualizado
             ↓
thompson_bandit versão 1 agora está em PRODUCTION
```

---

### 4️⃣ API carrega automaticamente na inicialização

**Em app/main.py:**

```python
@app.on_event("startup")
async def load_model():
    # 1. Conectar ao MLflow
    client = MlflowClient("http://localhost:5000")
    
    # 2. Procurar modelo em Production
    versions = client.get_latest_versions(
        "thompson_bandit",
        stages=["Production"]
    )
    
    # 3. Carregar em memória
    model = mlflow.sklearn.load_model(
        "models:/thompson_bandit/Production"
    )
    
    # ✅ Pronto! Pode servir requisições
```

**Logs da API:**

```
[INFO] Loading model from MLflow...
[INFO] Model: thompson_bandit v1 (Production)
[INFO] Status: ✅ Loaded successfully
[INFO] Ready to serve requests
```

---

### 5️⃣ Cliente faz requisição

```
POST /recomendar
{
  "customer_id": "C12345",
  "age": 35,
  "balance": 5000,
  ...
}

     ↓ API em memória (rápido!)

prediction = model.predict(features)

     ↓ Log no MLflow

mlflow.log_metric("predicted_channel", prediction)

     ↓ Resposta

{
  "recommendation": "cellular",
  "confidence": 0.78,
  "model_version": 1
}
```

---

### 6️⃣ Feedback registrado

```
POST /feedback
{
  "decision_id": "DECISION_12345",
  "actual_result": true  (conversão!)
}

     ↓

mlflow.log_metric("conversion", 1.0)
mlflow.log_metric("cellular_wins", 45)
mlflow.log_metric("telephone_wins", 38)

     ↓ MLflow ui atualiza em tempo real
```

---

## 📊 Timeline Comparado

### Sem MLflow ❌

```
Hora    Ação
────────────────────────────────────────────
14:00   Roda notebook
14:05   Salva modelo em arquivo local .pkl
14:06   ??? Como saber se é melhor que antes?
14:07   Copia arquivo para servidor (manual)
14:08   Redeploy (downtime)
14:09   Esperando dados de produção...

Problema: Ninguém sabe se funcionou! 😞
```

### Com MLflow ✅

```
Hora    Ação
────────────────────────────────────────────
14:00   Roda notebook
14:01   Modelo no MLflow automaticamente
14:02   Abre UI: vê +30% de melhora! 🎉
14:03   Click "Register Model" (1 clique)
14:04   Click "→ Production" (1 clique)
14:05   API recarrega AUTOMATICAMENTE
14:06   Cliente chamando /recomendar
14:07   MLflow mostrando performance ao vivo

Vantagem: Automático, rastreável, reversível! ✅
```

---

## 🏗️ Arquitetura Por Ambiente

### Local (Desenvolvimento)

```
Você (Notebook)
    │
    ├─ Treina modelo
    ├─ Loga no MLflow
    │
    ▼
🎛️ MLflow Server (localhost:5000)
    │
    ├─ Backend: SQLite (mlflow.db)
    ├─ Artifacts: ./mlruns/
    └─ Modelos: Memória + ./mlruns/models/
    
    │
    ▼
🚀 API (localhost:8000)
    │
    ├─ Carrega modelo do MLflow
    └─ Serve /recomendar, /feedback

    │
    ▼
👥 Cliente (Browser/Script)
    │
    └─ POST /recomendar → resposta
```

### Produção AWS

```
Você (Jupyter Notebook LOCAL ou EC2)
    │
    ├─ Treina modelo
    ├─ Loga no MLflow AWS
    │
    ▼
☁️ AWS
    │
    ├─ 🎛️ MLflow Server (ECS Fargate)
    │   ├─ Backend: RDS PostgreSQL
    │   ├─ Artifacts: S3 Bucket
    │   └─ Modelos: RDS + S3
    │
    ├─ 🚀 API FastAPI (ECS Fargate)
    │   ├─ Carrega modelo de RDS + S3
    │   ├─ Estado do bandit em DynamoDB
    │   └─ Logs em CloudWatch
    │
    ├─ 📊 ALB (Application Load Balancer)
    │   └─ Roteia :80 → API
    │           :5000 → MLflow UI
    │
    └─ 🔐 Secrets Manager, CloudWatch

    │
    ▼
👥 Cliente (Internet)
    │
    └─ HTTP → ALB:80 → API → /recomendar
```

---

## 🔄 Comparação: Sem vs Com MLflow

| Aspecto | ❌ SEM MLflow | ✅ COM MLflow |
|---------|---|---|
| **Treino** | Notebook isolado | Rastreado + versionado |
| **Artefatos** | Arquivos espalhados | Centralizados no MLflow |
| **Métricas** | Variáveis soltas | Tabelas estruturadas |
| **Reprodução** | Impossível | 1 clique no UI |
| **Deploy** | Manual + arriscado | Automático + seguro |
| **Monitoramento** | Nenhum | Dashboard ao vivo |
| **Auditoria** | Sem histórico | Log imutável |
| **Colaboração** | Retrabalho | Centralizado no UI |

---

## 📈 Exemplo Real: +30% de Conversão

### Baseline (SEM Thompson)

```
Regra: sempre recomenda "cellular"

Resultado: 15% de conversão
│
├─ Conversão: 150 em 1000
├─ Custo: 5000 reais em ligações improdutivas
└─ Problema: Não aprende

[Registrado em MLflow]
```

### Thompson Sampling (COM MLflow)

```
Aprende qual canal cada cliente prefere

Resultado: 19.7% de conversão (+31% relativo!)
│
├─ Conversão: 197 em 1000 (47 mais!)
├─ Economia: 47 conversões extra
├─ Recurso: Prático no mesmo custo
└─ Vantagem: Continua aprendendo

[Comparação visual no MLflow UI]
mlrun-1 baseline        AUC: 0.72, Conv: 15.0%
mlrun-2 thompson_v1  ★ AUC: 0.79, Conv: 19.7% ← MELHOR!
```

---

## 🚀 Próximos Passos

### Hoje
- [x] Entender como MLflow funciona
- [x] Ver o fluxo completo visualmente
- [ ] Rodar `python doc/mlflow_demo_script.py`

### Semana que vem
- [ ] Adicionar mlflow ao notebook 03
- [ ] Rodar treino e registrar modelo
- [ ] Integrar na API
- [ ] Testar em localhost

### Próximo mês
- [ ] Deploy na AWS com Terraform
- [ ] Configurar RDS + S3 + DynamoDB
- [ ] Monitoring contínuo
- [ ] Demo Day!

---

**Criado para:** datathon-8mlet-grupo-04  
**Data:** 2026-09-20  
**Status:** Pronto para começar! 🚀
