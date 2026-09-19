# 📚 Índice MLflow: Guia de Navegação

## 📄 Documentos Disponíveis

### 1. **MLflow_Jornada_Completa.md** ⭐ COMECE AQUI
- **O que é:** Guia prático completo de 5 semanas com 2 rotas opcionais
- **Para quem:** Cientistas de dados + Engenheiros ML
- **Conteúdo:**
  - Semana 1: Enriquecer Tracking nos Notebooks
  - Semana 2: Validação e Registro no Model Registry
  - Semana 3: Scripts Reproduzíveis (MLflow Projects)
  - Semana 4: Integração na API (Docker Compose Local)
  - Semana 5: Escolha sua rota
    - **Rota A:** Continuar em Docker Compose (grátis, simples)
    - **Rota B:** Escalar para AWS (profissional, automático)
  - Checklist completo de implementação
  - Exemplos de código prontos para copiar/colar

**👉 Leia isso primeiro para entender o big picture**

---

### 2. **MLflow_Arquitetura_Visual.md** 
- **O que é:** Diagramas visuais da infraestrutura
- **Para quem:** Engenheiros, DevOps, stakeholders
- **Conteúdo:**
  - Arquitetura Local (Docker Compose)
  - Arquitetura AWS (ECS + RDS + S3 + CloudWatch)
  - Fluxo completo: Notebook → Production
  - Estados do modelo no Registry
  - Visão geral da infraestrutura

**👉 Consulte quando quiser entender a arquitetura**

---

## 🎯 Quick Start (30 minutos)

### Se você é **Cientista de Dados**:

1. Leia: **Semana 1** de `MLflow_Jornada_Completa.md`
2. Copie o código de enriquecimento do notebook 03
3. Rode: `mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000`
4. Visualize no browser: http://localhost:5000

```bash
# Seus comandos principais serão:
mlflow.log_param('seed', 42)
mlflow.log_metric('conversion', 0.1367)
mlflow.log_artifact('bandit_model.pkl')
mlflow.log_figure(fig, 'dashboard.png')
```

### Se você é **Engenheiro ML**:

1. Leia: **Semana 3 e 4** de `MLflow_Jornada_Completa.md`
2. Crie `src/train.py` e `MLproject`
3. Integre na `app/main.py`: `mlflow.pyfunc.load_model()`
4. Teste: `docker compose -f deploy/docker-compose.yml up`

### Se você é **DevOps / AWS**:

1. Leia: **Semana 5** de `MLflow_Jornada_Completa.md` + `MLflow_Arquitetura_Visual.md`
2. Review do Terraform em `deploy/aws/terraform/mlflow.tf`
3. Implemente RDS PostgreSQL + S3 + ECS Task
4. Configure GitHub Actions para CI/CD

---

## 📋 Checklist de Implementação

### ✅ **Semana 1: Notebooks (Cientista)**
```
[ ] Ler: MLflow_Jornada_Completa.md (Semana 1)
[ ] Adicionar Tags no notebook 03
[ ] Aumentar Métricas (histórico, segmentos)
[ ] Logar Gráficos (4+ visualizações)
[ ] Logar Artefatos (CSV, PKL, JSON, Relatório)
[ ] Testar: mlflow ui --backend-store-uri sqlite:///mlflow.db
[ ] Visualizar no http://localhost:5000
```

### ✅ **Semana 2: Golden Set (Cientista)**
```
[ ] Ler: MLflow_Jornada_Completa.md (Semana 2)
[ ] Notebook 04 com validação Golden Set
[ ] Criar wrapper mlflow.pyfunc.PythonModel
[ ] Registrar modelo: datathon-bandit-thompson
[ ] Testar carregamento do modelo
[ ] Promover para Production (via UI)
```

### ✅ **Semana 3: Scripts (Engenheiro)**
```
[ ] Ler: MLflow_Jornada_Completa.md (Semana 3)
[ ] Converter notebook 03 → src/train.py
[ ] Converter notebook 04 → src/evaluate.py
[ ] Criar MLproject na raiz
[ ] Testar: mlflow run . --entry-point train -P seed=123
[ ] Validar reproduzibilidade
```

### ✅ **Semana 4: API (Engenheiro)**
```
[ ] Ler: MLflow_Jornada_Completa.md (Semana 4)
[ ] Modificar app/main.py (load modelo do Registry)
[ ] Atualizar Dockerfile.fastapi
[ ] Testar: docker compose up
[ ] Validar: curl http://localhost:8000/recomendar
[ ] Validar: http://localhost:5002 (MLflow UI)
```

### ✅ **Semana 5: Escolha Sua Rota (DevOps)**

**ROTA A: Docker Compose Local**
```
[ ] Ler: MLflow_Jornada_Completa.md (Semana 5 - Rota A)
[ ] Documentar instruções docker compose
[ ] Testar em servidor Linux (se necessário)
[ ] Pronto para demo/apresentação
```

**ROTA B: AWS (ECS + RDS + S3)**
```
[ ] Ler: MLflow_Jornada_Completa.md (Semana 5 - Rota B) + MLflow_Arquitetura_Visual.md
[ ] Criar RDS PostgreSQL (aurora-postgresql)
[ ] Criar S3 para artifacts
[ ] Criar ECS Task MLflow
[ ] Integrar na FastAPI (MLFLOW_TRACKING_URI)
[ ] Configurar GitHub Actions (CI/CD)
[ ] Teste end-to-end na AWS
```

---

## 🔍 Procurando por Algo Específico?

| Tópico | Onde Encontrar |
|--------|------------------|
| Como usar MLflow.log_* | Semana 1, MLflow_Jornada_Completa.md |
| Model Registry (Staging/Production) | Semana 2, MLflow_Jornada_Completa.md |
| MLflow Projects | Semana 3, MLflow_Jornada_Completa.md |
| API + MLflow | Semana 4, MLflow_Jornada_Completa.md |
| AWS Deployment | Semana 5, MLflow_Jornada_Completa.md |
| Arquitetura Local | MLflow_Arquitetura_Visual.md (Docker Compose) |
| Arquitetura AWS | MLflow_Arquitetura_Visual.md (ECS + RDS + S3) |
| Fluxo Completo | MLflow_Arquitetura_Visual.md (últimas seções) |
| Exemplos de Código | MLflow_Jornada_Completa.md (cada semana tem exemplos) |

---

## 💡 Dicas Importantes

### Para Cientistas (Semana 1-2)
```python
# ✅ Faça isso: Enrich tracking
mlflow.set_tag('producao_ready', 'false')  # Depois muda para 'true'
mlflow.log_metric('thompson_conversion_rolling', conv, step=round_num)
mlflow.log_figure(fig, 'dashboard.png')
mlflow.log_dict(config, 'config.json')

# ❌ Não faça: Logging mínimo
mlflow.log_param('model', 'v1')  # muito vago
mlflow.log_metric('score', 0.85)  # sem contexto
```

### Para Engenheiros (Semana 3-4)
```python
# ✅ Faça isso: Load modelo do Registry
model = mlflow.pyfunc.load_model('models:/datathon-bandit-thompson/Production')

# ❌ Não faça: Hard-code o caminho
model = pickle.load(open('bandit_model.pkl', 'rb'))  # quebra em CI/CD
```

### Para DevOps (Semana 5)
```bash
# ✅ Faça isso: Use Secrets Manager para senhas
MLFLOW_BACKEND_STORE_URI=postgresql://user:${RDS_PASSWORD}@...

# ❌ Não faça: Senhas em código
MLFLOW_BACKEND_STORE_URI=postgresql://user:password123@...
```

---

## 📞 Dúvidas Frequentes

### P: Por onde começo?
**R:** Leia `MLflow_Jornada_Completa.md` **Semana 1** (15 min). Depois implemente o código de tracking no seu notebook.

### P: Qual a diferença entre Staging e Production?
**R:** 
- **Staging**: Versão testada, aguardando aprovação
- **Production**: Versão em uso na API
Leia Semana 2 para detalhes.

### P: Como retreinar automaticamente?
**R:** Configure GitHub Actions (Semana 5) para rodar `src/train.py` em schedule e fazer deploy automático.

### P: Preciso rodar tudo na AWS desde o início?
**R:** Não! Desenvolva localmente (Semana 1-4 com Docker Compose), depois suba na AWS (Semana 5).

### P: Como monitorar a API em produção?
**R:** CloudWatch logs + métricas (Semana 5). MLflow também rastreia predictions e feedbacks.

---

## 🚀 Próximos Passos

1. **Agora (5 min):** Escolha seu role (Cientista/Engenheiro/DevOps)
2. **Hoje (1-2 horas):** Leia a Semana correspondente
3. **Semana 1:** Implemente o código no seu notebook
4. **Semana 2-5:** Siga o checklist progressivamente

**Objetivo final:** Sistema de ML Ops profissional com rastreamento completo, versionamento e deploy automático.

---

## 📚 Estrutura de Arquivos

```
datathon-8mlet-grupo-04/
├── doc/
│   ├── MLflow_INDEX.md                    ← Você está aqui!
│   ├── MLflow_Jornada_Completa.md         ← Guia completo (5 semanas)
│   ├── MLflow_Arquitetura_Visual.md       ← Diagramas e arquitetura
│   ├── datathon.md
│   └── PLANO_EXECUCAO.md
│
├── notebooks/
│   ├── 01_EDA.ipynb                       (Etapa 1)
│   ├── 02_Preparacao_da_Base.ipynb        (Etapa 2)
│   ├── 03_Baseline_e_Thompson.ipynb       (Etapa 3) ← Enriqueça aqui (Semana 1)
│   ├── 04_Avaliacao_e_Golden_Set.ipynb    (Etapa 4) ← Valide aqui (Semana 2)
│   └── 07_MLflow_Tracking.ipynb           (Etapa 7) ← Será preenchido
│
├── src/                                   ← Crie aqui (Semana 3)
│   ├── train.py                           (novo)
│   ├── evaluate.py                        (novo)
│   └── data_processing.py                 (já existe)
│
├── app/
│   ├── main.py                            (modifique aqui - Semana 4)
│   └── requirements.txt
│
├── deploy/
│   ├── docker-compose.yml                 (já existe, testar Semana 4)
│   ├── Dockerfile.fastapi                 (modifique - Semana 4)
│   ├── Dockerfile.mlflow
│   └── aws/
│       └── terraform/                     (implementar - Semana 5)
│           ├── mlflow.tf                  (novo)
│           └── fastapi.tf                 (modificar)
│
├── MLproject                              ← Crie aqui (Semana 3)
├── python_env.yaml                        ← Crie aqui (Semana 3)
└── mlflow.db                              (criado automaticamente)
```

---

## 🎯 Resumo Final

| Fase | Semana | Role | Ação | Resultado |
|------|--------|------|------|-----------|
| **Experimentação** | 1-2 | Cientista | Enriquecer tracking + registrar modelo | Modelo no Registry |
| **Reproduzibilidade** | 3 | Engenheiro | Converter notebooks em scripts | MLflow Projects |
| **Integração** | 4 | Engenheiro | API carrega modelo do Registry | Deploy local |
| **Operação** | 5 | DevOps | Infraestrutura AWS + CI/CD | Production ready |

**Tempo total estimado:** 2-3 semanas (paralelo + dedicado)

**Resultado:** Sistema profissional de MLOps com rastreamento, versionamento, automação e monitoramento. ✅

---

**Dúvidas? Consulte os documentos mencionados acima!** 📖
