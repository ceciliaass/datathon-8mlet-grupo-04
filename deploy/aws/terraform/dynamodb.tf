# Estado do bandit (Thompson Sampling nao-contextual: so 2 contadores por
# braco) e o log de decisoes. O padrao de acesso real - grava decisao sem
# resultado, depois busca por decision_id e atualiza com o resultado - e
# get/update por chave primaria, por isso DynamoDB (nao S3) e a escolha
# correta para as duas tabelas (ver nota no README sobre essa correcao).

resource "aws_dynamodb_table" "bandit_arms" {
  name         = "${var.project_name}-bandit-arms"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "arm"

  attribute {
    name = "arm"
    type = "S"
  }
}

resource "aws_dynamodb_table" "bandit_decisions" {
  name         = "${var.project_name}-bandit-decisions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "decision_id"

  attribute {
    name = "decision_id"
    type = "S"
  }
}

# Warm start com os mesmos numeros historicos usados localmente em
# data/processed/bank-term-deposit-subscription_eda/arm_stats.csv:
#   cellular:  4369 conversoes / 24916 falhas (29285 observacoes)
#   telephone:  390 conversoes /  2516 falhas ( 2906 observacoes)
# `lifecycle.ignore_changes` evita que um `terraform apply` futuro sobrescreva
# contadores que a aplicacao ja atualizou via UpdateItem.
resource "aws_dynamodb_table_item" "arm_cellular" {
  table_name = aws_dynamodb_table.bandit_arms.name
  hash_key   = aws_dynamodb_table.bandit_arms.hash_key

  item = jsonencode({
    arm           = { S = "cellular" }
    success_count = { N = "4369" }
    fail_count    = { N = "24916" }
  })

  lifecycle {
    ignore_changes = [item]
  }
}

resource "aws_dynamodb_table_item" "arm_telephone" {
  table_name = aws_dynamodb_table.bandit_arms.name
  hash_key   = aws_dynamodb_table.bandit_arms.hash_key

  item = jsonencode({
    arm           = { S = "telephone" }
    success_count = { N = "390" }
    fail_count    = { N = "2516" }
  })

  lifecycle {
    ignore_changes = [item]
  }
}
