# 📚 Documentação MLflow - Índice Completo

## 🎯 Qual documento ler?

### 🟦 Se você quer entender **CONCEITOS** (por que MLflow importa)
→ **[MLFLOW_MLOPS_GUIDE.md](MLFLOW_MLOPS_GUIDE.md)**

Cobre:
- ❌ Problemas SEM MLflow (6 problemas reais)
- ✅ Como MLflow resolve cada um
- 🏗️ Arquitetura com diagramas Mermaid
- 💻 Exemplo de código prático
- 📊 Dashboard MLflow
- 📋 FAQ e próximos passos

**Tempo:** 15-20 min de leitura

---

### 🟩 Se você quer entender **NA PRÁTICA** (como funciona o fluxo)
→ **[MLFLOW_WORKFLOW_PRATICO.md](MLFLOW_WORKFLOW_PRATICO.md)**

Cobre:
- 🔄 Fluxo passo-a-passo quando você treina um modelo
- 📁 O que é salvo onde (disco, banco de dados)
- 🚀 Como a API carrega o modelo automaticamente
- 📊 Timeline real (quanto tempo leva cada etapa)
- ✅ Checklist prático para seu primeiro deploy
- 🐛 Troubleshooting comum

**Tempo:** 20-30 min (com exemplos práticos)

---

### 🟨 Se você quer **RODAR UMA DEMO** (ver funcionando)
→ **[mlflow_demo_script.py](mlflow_demo_script.py)**

Execute:
\`\`\`bash
python doc/mlflow_demo_script.py
\`\`\`

O que faz:
1. Simula treinamento de modelo no notebook
2. Registra no MLflow
3. Promove para Production
4. API carrega modelo
5. Faz predição
6. Registra feedback

**Saída:** Logs coloridos mostrando cada etapa + runs criados no MLflow

---

## 🚀 Quick Start (5 min)

### Opção 1: Ver funcionando (Recomendado!)

\`\`\`bash
# Terminal 1: Iniciar MLflow
mlflow server --backend-store-uri sqlite:///mlflow.db \\
              --default-artifact-root ./mlruns \\
              --host 0.0.0.0 --port 5000

# Terminal 2: Rodar demo
python doc/mlflow_demo_script.py

# Terminal 3: Abrir browser
# http://localhost:5000/
# Você verá:
# - 3 runs criados em tempo real
# - Métricas de treino, predição, feedback
# - Modelo registrado e em Production
\`\`\`

---

## 📊 Arquitetura Visual

### Local Development

\`\`\`mermaid
graph TB
    NB["📓 Notebook<br/>03_Baseline_Thompson"]
    MLLocal["🎛️ MLflow Server<br/>localhost:5000"]
    DB["💾 mlflow.db<br/>SQLite"]
    Artifacts["📦 ./mlruns/<br/>artifacts"]
    Registry["📋 Model Registry<br/>thompson_bandit"]
    API["🚀 API FastAPI<br/>localhost:8000"]
    Client["👥 Cliente"]
    
    NB -->|log_params<br/>log_metrics<br/>log_model| MLLocal
    MLLocal --> DB
    MLLocal --> Artifacts
    MLLocal --> Registry
    
    API -->|load_model<br/>Production| Registry
    API -->|log inference| MLLocal
    
    Client -->|POST /recomendar| API
    Client -->|POST /feedback| API
    
    style NB fill:#fff3e0
    style MLLocal fill:#f3e5f5
    style API fill:#e3f2fd
    style Client fill:#fce4ec
\`\`\`

### AWS Production

\`\`\`mermaid
graph TB
    subgraph AWS["☁️ AWS us-east-2"]
        ALB["⚖️ Application Load Balancer<br/>Port 80 & 5000"]
        
        subgraph ECS["🐳 ECS Fargate"]
            FastAPI["🚀 FastAPI<br/>Thompson Sampling"]
            MLflowUI["🎛️ MLflow Server"]
        end
        
        DynamoDB["🗄️ DynamoDB<br/>bandit-arms<br/>bandit-decisions"]
        
        subgraph MLflowBackend["💾 MLflow Backend"]
            RDS["🐘 RDS PostgreSQL<br/>experiment metadata"]
            S3["🪣 S3 Bucket<br/>artifacts"]
        end
        
        Secrets["🔐 Secrets Manager<br/>DB credentials"]
        CW["📊 CloudWatch<br/>logs & metrics"]
    end
    
    Client["👥 Cliente<br/>Browser"]
    
    Client -->|HTTP| ALB
    ALB -->|:80| FastAPI
    ALB -->|:5000| MLflowUI
    
    FastAPI -->|get/put items| DynamoDB
    FastAPI -->|log runs| MLflowUI
    
    MLflowUI --> RDS
    MLflowUI --> S3
    MLflowUI -.->|read creds| Secrets
    
    ECS -.->|stream logs| CW
    
    style AWS fill:#e8f5e9
    style ECS fill:#f3e5f5
    style MLflowBackend fill:#e0f2f1
\`\`\`

### Fluxo Completo: Notebook → API → Produção

\`\`\`mermaid
graph LR
    subgraph Dev["LOCAL"]
        NB["📓 Notebook<br/>03_Baseline_Thompson"]
        ML1["🎛️ MLflow<br/>SQLite"]
    end
    
    subgraph Prod["AWS"]
        ALB["⚖️ ALB"]
        API["🚀 API FastAPI"]
        ML2["🎛️ MLflow<br/>RDS + S3"]
    end
    
    NB -->|mlflow.start_run<br/>log_params/metrics| ML1
    ML1 -->|mlflow.register_model<br/>Transition to Production| Prod
    API -->|load_model<br/>models:/thompson/Production| ML2
    ALB --> API
    
    style Dev fill:#fff3e0
    style Prod fill:#e8f5e9
    style NB fill:#ffe0b2
    style API fill:#bbdefb
\`\`\`

---

## ✅ Checklist Rápido de Implementação

- [ ] 1. Ler [MLFLOW_MLOPS_GUIDE.md](MLFLOW_MLOPS_GUIDE.md) - Conceitos
- [ ] 2. Rodar `python doc/mlflow_demo_script.py` - Ver funcionando
- [ ] 3. Ler [MLFLOW_WORKFLOW_PRATICO.md](MLFLOW_WORKFLOW_PRATICO.md) - Fluxo prático
- [ ] 4. Adicionar `mlflow.start_run()` ao notebook 03
- [ ] 5. Adicionar `mlflow.log_param/metric()` ao treino
- [ ] 6. Registrar modelo na Model Registry
- [ ] 7. Promover versão para "Production"
- [ ] 8. Integrar carregamento em `app/main.py`
- [ ] 9. Testar API em localhost:8000
- [ ] 10. Fazer commit e preparar para AWS

---

**Última atualização:** 2026-09-20  
**Status:** Pronto para implementação! ✅
