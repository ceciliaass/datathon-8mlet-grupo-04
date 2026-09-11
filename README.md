| ![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg) ![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688?logo=fastapi) ![MLflow](https://img.shields.io/badge/MLOps-MLflow-0194E2?logo=mlflow) ![Epsilon-Greedy](https://img.shields.io/badge/Algorithm-Epsilon--Greedy-blue.svg) ![Scikit-learn](https://img.shields.io/badge/ML-Scikit--learn-F7931E?logo=scikit-learn) ![Status](https://img.shields.io/badge/Status-Fase%201-green.svg) |
|:----------------------------------------------------------------------------------------------------------------------------------------:|

# 🎯 Datathon — Plataforma de Experimentação Adaptativa para Ofertas Financeiras

## 📌 Descrição

Solução completa **end-to-end** para personalização adaptativa de ofertas financeiras usando **Epsilon-Greedy** (Multi-Armed Bandit). Plataforma que aprende continuamente qual oferta cada cliente prefere, otimizando taxas de conversão em tempo real.

---

## 🚀 Status Atual

| Fase | Objetivo | Status |
|------|----------|--------|
| **Fase 1** | EDA e Preparação de Dados | ✅ Em andamento |
| **Fase 2** | Baseline + Epsilon-Greedy | ⏳ Próximo |
| **Fase 3** | Avaliação e Golden Set | ⏳ Pendente |
| **Fase 4** | API FastAPI | ⏳ Pendente |
| **Fase 5** | MLflow Tracking | ⏳ Pendente |
| **Fase 6-8** | Cloud, Docs e Demo | ⏳ Pendente |

---

## 📊 Base de Dados

O projeto utiliza a base Kaggle abaixo com cache local:

| Base | Autor | Registros | Status |
|------|-------|-----------|--------|
| 1️⃣ Bank Marketing | [henriqueyamahata](https://www.kaggle.com/datasets/henriqueyamahata/bank-marketing) | ~41k | ✅ Funcionando |

**Leakage:** `duration` é removida por ser conhecida somente após a ligação. `pdays`, `previous` e `poutcome` são mantidas como histórico anterior ao contato.

---

## 🚀 Quick Start

### 1️⃣ Setup (2 min)

```bash
# Ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2️⃣ Configurar Kaggle (2 min)

```bash
# 1. Gerar token em: https://www.kaggle.com/settings/account
# 2. Baixar arquivo kaggle.json
# 3. Configurar:

mkdir -p ~/.kaggle
cp ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# 4. Testar
kaggle datasets list | head -5
```

**Guia detalhado:** `.kaggle/KAGGLE_SETUP.md`

### 3️⃣ Iniciar servidor MLflow (opcional, mas recomendado)

```bash
# Terminal 1: sobe o servidor local do MLflow
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5000
```

A interface será disponibilizada em: `http://localhost:5000`

Se preferir apenas abrir a UI, sem iniciar o servidor em modo explícito, também funciona:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000
```

### 4️⃣ Executar Fase 1 (15 min)

```bash
jupyter notebook notebooks/01_EDA.ipynb

# Célula 4️⃣: Baixa 4 bases com cache
# Célula 5-6️⃣: Carrega e explora dados
# Célula 7-12️⃣: Processa e salva
```

**Resultado:** `data/processed/bank-marketing_eda/bank_marketing_tratado.csv` ✅

---

## 📁 Estrutura do Projeto

```
mle_tech_chalenge_5/
│
├── 📓 notebooks/
│   └── 01_EDA.ipynb                    ← EXECUTE PRIMEIRO
│
├── 🐍 src/
│   ├── __init__.py
│   ├── data_processing.py              ← Funções de EDA
│   ├── baseline.py                     ← Fase 2
│   ├── adaptive_model.py               ← Fase 2
│   ├── api.py                          ← Fase 4
│   └── train_and_log.py                ← Fase 5
│
├── 📊 data/
│   ├── raw/                            ← Dados brutos (não versiona)
│   └── processed/                      ← Dados processados (não versiona)
│       └── bank-marketing_eda/
│
├── 🎛️ models/
│   ├── scaler_*.pkl                    ← StandardScaler por dataset (não versiona)
│   └── label_encoders_*.pkl            ← Encoders por dataset (não versiona)
│
├── 📚 doc/
│   ├── SETUP.md                        ← Guia de setup
│   ├── FASES_DETALHADAS.md             ← Arquitetura completa
│   ├── datathon.md                     ← Briefing oficial
│   ├── FASE_1_CHECKLIST.md             ← Checklist Fase 1 (local)
│   ├── FASE_1_README.md                ← Guia Fase 1 (local)
│   └── QUICK_START.md                  ← Inicio rápido (local)
│
├── 🔑 .kaggle/
│   ├── KAGGLE_SETUP.md                 ← Como configurar token
│   └── kaggle.json                     ← Arquivo real (não versiona)
│
├── 📋 README.md                        ← Este arquivo
├── 📦 requirements.txt                 ← Dependências Python
├── .gitignore                          ← Exclusões do git
├── PLANO_EXECUCAO.md                   ← Roadmap das 9 fases
└── .env.example                        ← Template de variáveis
```

---

## 🎓 Fluxo de Trabalho

```
1. Setup Kaggle
   ↓
2. Executar Notebook 01_EDA.ipynb
   ├─ Célula 4️⃣: Baixa 4 bases com cache
   ├─ Célula 5-6️⃣: Exploração de dados
   └─ Célula 7-12️⃣: Processamento
   ↓
3. Dados salvos em: data/processed/{dataset}/
   ├─ data_processed.csv (features + target)
   ├─ X_features.csv
   ├─ y_target.csv
   └─ dataset_info.md
   ↓
4. Modelos salvos em: models/
   ├─ scaler_{dataset}.pkl
   └─ label_encoders_{dataset}.pkl
   ↓
5. Pronto para Fase 2 (Baseline + Epsilon-Greedy)
```

---

## 🔧 Tecnologias

| Componente | Tecnologia | Versão |
|-----------|------------|--------|
| Linguagem | Python | 3.12+ |
| Data Science | Pandas, NumPy | 2.0+, 1.25+ |
| ML | Scikit-learn | 1.4+ |
| Visualização | Matplotlib, Seaborn | 3.8+, 0.13+ |
| Notebooks | Jupyter | 1.0+ |
| API | FastAPI | 0.105+ |
| MLOps | MLflow | 2.10+ |
| Config | Python-dotenv, PyYAML | 1.0+, 6.0+ |

---

## 📊 Fase 1: O que você vai aprender

✅ **Exploração de Dados (EDA)**
- Distribuição de variáveis
- Correlações com target
- Valores faltantes e outliers

✅ **CRÍTICO: Vazamento Temporal**
- Identificar e remover vazamento
- Por que `duration` não pode ser usado
- Impacto em produção

✅ **Preparação de Dados**
- Tratamento de missings
- Encoding de categóricas
- Normalização com StandardScaler

✅ **Pipeline Modular**
- Funções reutilizáveis
- Salvamento de modelos
- Reprodutibilidade

---

## ⚡ Sistema de Cache

**Primeira execução:**
```
⬇️ Bank Marketing: 5s
⬇️ Bank Marketing Dataset: 8s
⬇️ Bank Term Deposit: 2s
⬇️ Telemarketing JYB: 1s
─────────────────────
⏱️ Total: ~16s
```

**Próximas execuções:**
```
✅ Todas as bases: <4s (cache)
⚡ 4x mais rápido!
```

---

## 📝 Dados Excluídos do Git

Pelo `.gitignore`:
```
❌ data/                    (Dados brutos e processados)
❌ models/                  (Modelos treinados)
❌ .env                     (Variáveis de ambiente)
❌ .kaggle/kaggle.json      (Credenciais)
❌ *.log                    (Logs)
❌ mlruns/                  (Experimentos)
```

---

## 🎯 Próximas Fases

### Fase 2: Baseline + Epsilon-Greedy
- Implementar modelo baseline
- Implementar Epsilon-Greedy
- Comparar performance
- Gráficos de convergência

### Fase 3: Avaliação
- Golden Set com 5 clientes
- Validação manual
- Análise de coerência

### Fase 4: API FastAPI
- Endpoint `/recommend`
- Endpoint `/arms-stats`
- Documentação Swagger

### Fase 5: MLflow
- Iniciar o servidor local do MLflow antes dos experimentos
- Rastreamento de experimentos
- Versionamento de modelos
- Dashboard em `http://localhost:5000`

```bash
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5001
```

---

## 🤝 Contribuindo

1. Clone o repositório
2. Configure Kaggle (`.kaggle/KAGGLE_SETUP.md`)
3. Execute Notebook Fase 1
4. Implemente sua Fase
5. Commit + Push

---

## 📖 Documentação Completa

- **Setup Kaggle:** `.kaggle/KAGGLE_SETUP.md`
- **Guia Setup:** `doc/SETUP.md`
- **Roadmap:** `PLANO_EXECUCAO.md`
- **Arquitetura:** `doc/FASES_DETALHADAS.md`
- **Briefing:** `doc/datathon.md`

---

## 📞 Status & Links

- **GitHub:** https://github.com/vagnerasilva/mle_tech_chalenge_5
- **Status:** Fase 1 - EDA ✅
- **Última atualização:** 2026-08-11

---

**Pronto para começar?** 🚀
```bash
source venv/bin/activate
jupyter notebook notebooks/01_EDA.ipynb
```
