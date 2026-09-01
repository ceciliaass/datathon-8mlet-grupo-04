# Serviço de Decisão Adaptativa (Etapa 5 do Datathon)

API que recebe o pedido de recomendação de canal para um cliente e devolve a
escolha do bandit (Thompson Sampling); recebe depois o resultado real
(conversão ou não) e usa isso para continuar aprendendo — o aprendizado
persiste em disco e sobrevive a reinícios do processo.

## Por que isso é diferente do notebook

No notebook, a simulação inteira (milhares de decisões e recompensas) roda
dentro da mesma execução de célula, em memória. Em produção isso não existe:
cada decisão é um evento isolado no tempo, e o resultado (a pessoa converteu
ou não) só é conhecido depois — segundos, minutos ou dias depois — vindo de
outra chamada, possivelmente de outro sistema (CRM, discador, callback de
campanha). Para o bandit continuar "adaptativo de verdade" nesse cenário, ele
precisa:

1. **Persistir o estado entre chamadas e entre reinícios do processo** —
   feito salvando o `MAB` do MABWiser em disco (pickle) após cada
   atualização, e recarregando na inicialização.
2. **Amarrar cada decisão ao seu resultado eventual** — feito com um
   `decision_id` (UUID) devolvido em `/recomendar` e exigido em `/feedback`,
   com um log append-only (`data/decisions_log.jsonl`) que serve também como
   trilha de auditoria (governança).
3. **Ser seguro para chamadas concorrentes** — um lock simples protege a
   leitura/atualização/gravação do bandit contra condições de corrida quando
   várias requisições chegam ao mesmo tempo.

## Rodando localmente

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### MLflow local para tracking

Antes de registrar experimentos e métricas, inicie o servidor MLflow em outro terminal:

```bash
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5000
```

A interface do MLflow fica disponível em `http://localhost:5000`.

Na primeira execução, se `data/bandit_state.pkl` ainda não existir, o bandit
é inicializado (warm start) com `arm_stats.csv` gerado pelo Notebook 2 — o
mesmo ponto de partida usado no Notebook 3. Se esse arquivo não for
encontrado, ele começa sem viés nenhum entre os braços.

## Endpoints

- `GET /health` — checagem simples de disponibilidade.
- `POST /recomendar` — recebe (opcionalmente) o contexto do cliente e
  devolve `{"decision_id": ..., "arm": "cellular" | "telephone"}`.
- `POST /feedback` — recebe `{"decision_id": ..., "converteu": true|false}`
  e atualiza o bandit. Retorna 404 se o `decision_id` não existir e 409 se
  ele já tiver recebido feedback antes (evita contar o mesmo evento duas
  vezes).
- `GET /stats` — observações, conversões e taxa de conversão estimada por
  braço, para monitorar o aprendizado ao vivo.

## Exemplo de uso

```bash
curl -X POST localhost:8000/recomendar \
  -H "Content-Type: application/json" \
  -d '{"idade": 45, "poutcome": "unknown", "previous": 0}'
# -> {"decision_id": "...", "arm": "cellular"}

curl -X POST localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"decision_id": "...", "converteu": true}'

curl localhost:8000/stats
```

## Limitações atuais e próximos passos naturais

- **Ainda não é contextual**: o campo `client_context` já é aceito e logado
  em cada decisão, mas a escolha do braço hoje ignora esse contexto (o
  Thompson Sampling é o mesmo bandit global do Notebook 3). Evoluir para
  `LearningPolicy.LinTS` do MABWiser usando esse contexto é o próximo passo
  natural, sem precisar mudar o contrato da API.
- **Persistência em arquivo, não em banco**: adequado para uma instância
  única (ex.: um único container). Para múltiplas réplicas em produção real,
  o estado do bandit precisaria morar em algo compartilhado (Redis, uma
  tabela em Postgres/DynamoDB) em vez de um arquivo local — ver parágrafo de
  arquitetura em nuvem no `README.md` principal do repositório.
- **Sem autenticação/rate limiting** — fora do escopo do datathon, mas seria
  necessário antes de expor isso publicamente.
