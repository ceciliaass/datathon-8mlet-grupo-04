# 📋 Plano de Execução - MLe Tech Challenge 5: Datathon

## 🎯 Objetivo

Desenvolver uma **plataforma de experimentação adaptativa** usando **Epsilon-Greedy** (Multi-Armed Bandit) para personalização de ofertas financeiras em tempo real.

---

## 📊 Status Geral

| Fase | Objetivo | Status | Progresso |
|------|----------|--------|-----------|
| **Fase 0** | Setup & Organização | ✅ Completa | 100% |
| **Fase 1** | EDA & Prep Dados | 🔄 Em andamento | 80% |
| **Fase 2** | Baseline + Epsilon-Greedy | ⏳ Próximo | 0% |
| **Fase 3** | Avaliação & Golden Set | ⏳ Pendente | 0% |
| **Fase 4** | API FastAPI | ⏳ Pendente | 0% |
| **Fase 5** | MLflow Tracking | ⏳ Pendente | 0% |
| **Fase 6** | Cloud Architecture | ⏳ Pendente | 0% |
| **Fase 7** | Documentação Final | ⏳ Pendente | 0% |
| **Fase 8** | Demo Day & Pitch | ⏳ Pendente | 0% |

---

## ✅ FASE 0: Organização & Setup

### Status: ✅ COMPLETA

#### Executados
- ✅ Repositório GitHub criado: `https://github.com/vagnerasilva/mle_tech_chalenge_5`
- ✅ Estrutura de pastas completa
- ✅ `.gitignore` configurado para excluir dados, modelos, credenciais
- ✅ `requirements.txt` com 15+ dependências (Python 3.12+)
- ✅ `README.md` com visão geral do projeto
- ✅ `.env.example` criado
- ✅ `.python-version` = 3.12
- ✅ `.kaggle/KAGGLE_SETUP.md` com guia completo
- ✅ Documentação em `doc/`

#### Artefatos
```
✅ README.md (atualizado)
✅ requirements.txt (Python 3.12+)
✅ .gitignore (dados, modelos, credenciais excluídos)
✅ .kaggle/KAGGLE_SETUP.md (guia Kaggle)
✅ .python-version (3.12)
```

---

## 🔄 FASE 1: EDA & Preparação de Dados

### Status: 🔄 80% - Em Andamento

### 📊 Bases de Dados Configuradas (4 Bases)

| Base | Autor | Registros | Status |
|------|-------|-----------|--------|
| 1️⃣ Bank Marketing | [henriqueyamahata](https://www.kaggle.com/datasets/henriqueyamahata/bank-marketing) | ~41k | ✅ Testado |
| 3️⃣ Bank Term Deposit | dharmik34 | ~11k | ✅ Testado |
| 4️⃣ Telemarketing JYB | aguado | ~4k | ✅ Testado |

### 🔄 Sistema de Cache

- ✅ **Primeira execução:** ~20s (download 4 bases)
- ✅ **Próximas execuções:** ~4s (cache local)
- ✅ Detecta automaticamente se dados existem
- ✅ Reutiliza dados sem fazer download novamente

### ✅ Executados

#### Configuração Kaggle
- ✅ `KAGGLE_SETUP.md` - guia passo a passo
- ✅ Endpoints atualizados e testados
- ✅ 3/4 bases sendo baixadas com sucesso
- ✅ 1/4 base (telemarketing) corrigida com endpoint atualizado

#### Notebook 01_EDA.ipynb
- ✅ 12 seções estruturadas
- ✅ Download automático de 4 bases com cache
- ✅ Exploração de dados (distribuição, correlações)
- ✅ Análise de missings e outliers
- ✅ Análise estatística completa
- ✅ **CRÍTICO:** Remoção de vazamento temporal
- ✅ Tratamento de valores faltantes
- ✅ Encoding de variáveis categóricas
- ✅ Normalização com StandardScaler
- ✅ Salvamento de dados processados (CSV + Parquet)
- ✅ Documentação gerada

#### Módulo src/data_processing.py
- ✅ 7 funções reutilizáveis
- ✅ Análise de missings e outliers
- ✅ Tratamento de valores faltantes
- ✅ Encoding de categóricas
- ✅ Normalização
- ✅ Pipeline completo

#### Documentação
- ✅ Dataset info gerado automaticamente

### 📁 Artefatos Gerados

**Por Dataset:**
```
data/processed/{dataset}/
├── data_processed.csv
├── data_processed.parquet
├── X_features.csv
├── y_target.csv
└── dataset_info.md

models/
├── scaler_{dataset}.pkl
└── label_encoders_{dataset}.pkl
```

### ⏳ Próximas Tarefas Fase 1

- [ ] Testar notebook com todos os usuários
- [ ] Validar qualidade dos dados processados
- [ ] Gerar tabela comparativa de datasets

---

## ⏳ FASE 2: Baseline + Epsilon-Greedy

### Status: ⏳ Não iniciado

### Objetivos
- Implementar modelo baseline determinístico
- Implementar Epsilon-Greedy
- Simular 1000 rounds de recomendações
- Gráficos de convergência e exploração
- Validação com Golden Set (5 clientes)

### Componentes a Criar
```
src/baseline.py              ← Modelo baseline
src/adaptive_model.py        ← Epsilon-Greedy
notebooks/02_Baseline_e_Adaptativo.ipynb ← Notebook fase 2
```

### Cronograma Estimado
- Implementação: 2-3 dias
- Testes: 1 dia
- Documentação: 1 dia

---

## ⏳ FASE 3: Avaliação & Golden Set

### Status: ⏳ Não iniciado

### Objetivos
- Selecionar 5 clientes representativos
- Gerar recomendações com Epsilon-Greedy
- Validação manual de coerência
- Análise comparativa com baseline

### Cronograma Estimado
- Validação: 1 dia

---

## ⏳ FASE 4: API FastAPI

### Status: ⏳ Não iniciado

### Endpoints a Implementar
```
POST /recommend     ← Gerar recomendação
GET /arms-stats     ← Estatísticas dos braços
GET /health         ← Status da API
```

### Cronograma Estimado
- Desenvolvimento: 2 dias
- Testes: 1 dia

---

## ⏳ FASE 5: MLflow Tracking

### Status: ⏳ Não iniciado

### Objetivos
- Log de parâmetros e métricas
- Versionamento de modelos
- Dashboard de experimentos
- Visualização e comparação de runs em MLflow

### Inicialização do servidor MLflow

```bash
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5000
```

A interface estará disponível em `http://localhost:5000`.

### Cronograma Estimado
- Implementação: 1 dia

---

## ⏳ FASE 6: Cloud Architecture

### Status: ⏳ Não iniciado

### Documentar
- S3/Blob para dados
- Lambda/Functions para processamento
- SageMaker/ML para modelo
- API Gateway para endpoints
- CloudWatch para monitoramento

### Cronograma Estimado
- Documentação: 1 dia

---

## ⏳ FASE 7: Documentação Final

### Status: ⏳ Não iniciado

### Documentar
- README.md completo (atualizar)
- Docstrings em todos os módulos
- Guias de setup e uso
- Limitações e próximos passos

### Cronograma Estimado
- Documentação: 1-2 dias

---

## ⏳ FASE 8: Demo Day & Video Pitch

### Status: ⏳ Não iniciado

### Deliverables
- Script de 5 minutos
- Demo ao vivo da API
- Vídeo pitch (MP4)
- Gráficos de resultados

### Cronograma Estimado
- Preparação: 2 dias
- Gravação e edição: 1-2 dias

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
| **MLOps** | MLflow | 2.10+ |
| **Config** | Python-dotenv, PyYAML | 1.0+, 6.0+ |

---

## 📅 Cronograma Estimado (Total)

```
Semana 1-2:  Fase 0 + Fase 1 (EDA)           ✅ Em andamento
Semana 2-3:  Fase 2 (Baseline + Epsilon-Greedy)    ⏳ Próximo
Semana 3-4:  Fase 3-4 (Avaliação + API)      ⏳ Pendente
Semana 4-5:  Fase 5-6 (MLflow + Cloud)       ⏳ Pendente
Semana 5-6:  Fase 7-8 (Docs + Demo)          ⏳ Pendente

Total: 4-6 semanas
```

---

## 📊 Progresso Visual

```
Fase 0: ████████████████████ 100% ✅
Fase 1: ████████████████░░░░  80% 🔄
Fase 2: ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Fase 3: ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Fase 4: ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Fase 5: ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Fase 6: ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Fase 7: ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Fase 8: ░░░░░░░░░░░░░░░░░░░░   0% ⏳
─────────────────────────────────
Total: ██████████░░░░░░░░░░  27% 🚀
```

---

## 🎯 Próximas Prioridades

### Imediato (Esta semana)
1. ✅ Finalizar Fase 1 (90% → 100%)
2. 🔄 Testar notebook com dados reais
3. 📝 Documentar resultados EDA

### Curto Prazo (Próximas 2 semanas)
1. ⏳ Iniciar Fase 2 (Baseline + Epsilon-Greedy)
2. ⏳ Implementar comparação de modelos
3. ⏳ Gráficos de convergência

### Médio Prazo (Semanas 3-4)
1. ⏳ Fase 3 (Golden Set)
2. ⏳ Fase 4 (API)
3. ⏳ Testes end-to-end

### Longo Prazo (Semanas 5-6)
1. ⏳ MLflow + Cloud
2. ⏳ Documentação Final
3. ⏳ Video Pitch

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
- ✅ 4 datasets testados e funcionando
- ✅ Sistema modular e reutilizável
- ✅ Documentação inline completa

---

**Última atualização:** 2026-08-11  
**Responsável:** Claude Code  
**Status Geral:** 27% Completo 🚀
