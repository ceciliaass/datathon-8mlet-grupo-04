# Datathon - Desafio de Machine Learning Engineering

## O Desafio

O Datathon propõe um desafio prático no domínio financeiro: **projetar uma plataforma de experimentação adaptativa** para ofertas, mensagens ou próximos passos em canais digitais.

Cada grupo deve construir uma solução **end-to-end de Machine Learning Engineering** e demonstrar como ela seria operada com observabilidade, avaliação e governança.

### Objetivo

O objetivo não é reproduzir um sistema bancário real, mas sim demonstrar **maturidade técnica** baseada nos conhecimentos do curso:

- Formular o problema
- Construir baselines
- Versionar dados
- Servir componentes
- Avaliar qualidade
- Monitorar risco
- Documentar limitações
- Explicar decisões para públicos técnicos e de negócio

### Contexto

Uma instituição financeira digital precisa decidir, em diferentes canais, qual oferta, mensagem ou próximo passo apresentar para cada cliente elegível.

**Problema:** Regras fixas e testes A/B longos desperdiçam tráfego, demoram para reagir a mudanças de contexto e dificultam a personalização responsável.

**Solução:** Uma abordagem adaptativa (como multi-armed bandit) que:
- Identifica comportamentos distintos
- Equilibra exploração e explotação
- Aprende com respostas observadas
- Evita congelar a decisão em regras estáticas

## Referências Algorítmicas

| Algoritmo | Papel no Desafio | Evidência Esperada |
|-----------|------------------|-------------------|
| **Thompson Sampling** | Exploração bayesiana sob incerteza para modelar conversão, clique ou recompensa esperada por braço | Priors documentados, comparação com baseline e análise de exploração |
| **Epsilon-Greedy ou UCB** | Família de algoritmos para selecionar ações com base em recompensa esperada e exploração | Implementação ou adaptação justificada, com análise do trade-off entre exploração e conversão |
| **Baseline Determinístico** | Política simples de controle (regra fixa, melhor braço histórico ou segmentação inicial) | Métrica comparativa clara para mostrar ganho ou limitação da política adaptativa |

### Flexibilidade Algorítmica (Variações)

O grupo pode implementar:
- Thompson Sampling
- Epsilon-Greedy
- UCB
- Outra variação contextual

**Requisitos:**
- Explique a escolha algorítmica
- Mostre como o contexto entra na decisão
- Documente a estratégia de exploração e recompensas

## Dados e Bases Kaggle

### Diretrizes

Use uma base Kaggle compatível com:
- Marketing
- Ofertas
- Propensão
- Campanhas
- Recomendação
- Conversão

**Como referência factual. Restrições importantes:**

❌ **Não use:**
- Dados reais de clientes
- Identificadores pessoais
- Patrimônio, renda, gênero, raça
- Regras comerciais privadas

✅ **Mantenha:**
- Decisões sensíveis com humano no loop
- Documentação de base legal
- Finalidade clara
- Minimização de dados
- Política de retenção

### Bases Kaggle Sugeridas

| Base | Autor | Uso no Desafio |
|------|-------|----------------|
| **bank-marketing** | henriqueyamahata | Campanhas bancárias, propensão de conversão e decisão de oferta |
| **bank-marketing-data-set** | tunguz | Variação do problema de marketing bancário para comparação |
| **bank-term-deposit-subscription** | dharmik34 | Assinatura de depósito a prazo como proxy de conversão |
| **telemarketing-jyb-dataset** | aguado | Campanhas de contato e resposta, útil para comparação de canal |

### Outras Bases

Outras bases serão aceitas se o grupo:
- Justificar a aderência ao desafio
- Documentar:
  - Fonte
  - Versão
  - Licença
  - Colunas
  - Target
  - Limitações

### Limpeza de Dados

⚠️ **Importante:**
- Descarte colunas de vazamento temporal (ex.: `duration` no Bank Marketing)
- Preserve a referência ao Kaggle

## Entregáveis Obrigatórios

Os entregáveis a seguir são organizados em **nove etapas**. O foco é a **simplicidade** e o **funcionamento do pipeline básico**.

💡 **Importante:** Toda a documentação deve ser consolidada diretamente no arquivo **README.md** do repositório, sem necessidade de múltiplos arquivos soltos de governança.

### Etapa 0 — Organização do Projeto

- Repositório público (ex: `datathon-7mlet-grupo-XX`)
- Arquivo `README.md` contendo a visão do problema e instruções de execução
- Arquivo `requirements.txt` ou `pyproject.toml` com as dependências

### Etapa 1 — Base Kaggle e EDA

- No `README.md`, insira o link da base Kaggle escolhida
- Um notebook simples contendo:
  - Análise Exploratória (EDA)
  - Tratamento de dados

### Etapa 2 — Preparação da Base

Se a base Kaggle escolhida já possuir dados claros de conversão/clique, você pode usá-la diretamente, sem precisar gerar dados sintéticos complexos.

**Objetivo:** Ter as features do cliente e a variável alvo prontas para o modelo.

### Etapa 3 — Baseline e Estratégia Algorítmica

- No notebook, calcule a **métrica de conversão de uma regra fixa** (Baseline - ex: oferecer sempre o mesmo produto ou melhor histórico)
- Implemente o **algoritmo adaptativo** (Thompson Sampling ou Epsilon-Greedy) e mostre a métrica dele **superando o Baseline**

### Etapa 4 — Avaliação e Casos de Teste

- Cálculo das **métricas de avaliação** do modelo
- No notebook ou `README.md`, crie um pequeno conjunto de **testes com apenas 5 exemplos de clientes** (Golden Set simplificado):
  - Qual oferta o modelo recomendou para cada um
  - Se a decisão fez sentido

### Etapa 5 — Serviço ou Interface Demonstrável

Um dos seguintes:
- Script Python
- Notebook interativo
- API básica (FastAPI)

**Funcionalidade:** Ao receber os dados de um cliente, retorne a oferta recomendada.

### Etapa 6 — Arquitetura-Alvo em Nuvem

Escreva um ou dois parágrafos no `README.md` explicando, de forma simples, quais serviços da nuvem o grupo utilizaria para colocar esse projeto no ar:
- AWS
- Azure
- Oracle
- GCP

**Nota:** A criação de diagramas é opcional.

### Etapa 7 — Ciclo de Vida MLOps

Utilize a ferramenta de **Controle de Versão para ML** abordada no curso (ex: MLflow localmente) para:
- Registrar os parâmetros do modelo
- Registrar as métricas obtidas na **Etapa 3**

### Etapa 8 — Apresentação Final (Demo Day)

**Vídeo Pitch** de até **5 minutos**:
- Explique rapidamente o problema de negócio
- Qual modelo foi usado
- Mostre a **Etapa 5 rodando na prática** (o modelo gerando uma recomendação)

💡 **Dica:** Não é necessário criar dezenas de slides.

## Critérios de Avaliação

A avaliação segue o contrato da Fase 05 e valoriza o esforço de entrega do ciclo de ponta a ponta:

| Dimensão | Peso | O que a Banca Procura |
|----------|------|----------------------|
| **Critérios de Negócio** | 30% | Clareza na explicação do problema e impacto da solução |
| **Validação Técnica Global** | 70% | Código organizado, modelo funcionando e superando o baseline, uso básico de MLflow e sucesso na demonstração prática |

## Checklist antes do Demo Day

- [ ] Repositório organizado com código e dependências (`requirements.txt` ou `pyproject.toml`)
- [ ] Notebook de EDA com a base Kaggle devidamente limpa e referenciada
- [ ] Modelo Baseline e Modelo Adaptativo implementados e comparados
- [ ] Notebook ou README demonstrando 5 casos de teste com as recomendações geradas
- [ ] Código executável (script, notebook ou API) que retorna a predição funcionando perfeitamente
- [ ] `README.md` preenchido com:
  - Link da base Kaggle
  - Parágrafo explicativo sobre a infraestrutura em nuvem
  - Instruções claras de execução local
- [ ] Tracking de experimentos registrado via ferramenta MLOps (MLflow ou equivalente)
- [ ] Vídeo de apresentação (até 5 min) gravado:
  - Demonstrando o código funcionando
  - Justificando as escolhas técnicas

---

## 🎯 Boa Sorte!