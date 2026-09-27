resource "random_password" "rds" {
  length  = 24
  special = false # evita caracteres que quebram a connection string do Postgres
}

resource "aws_secretsmanager_secret" "rds" {
  name                    = "${var.project_name}-rds-credentials"
  recovery_window_in_days = 0 # deleção imediata no destroy, sem soft-delete de 30 dias
}

resource "aws_secretsmanager_secret_version" "rds" {
  secret_id = aws_secretsmanager_secret.rds.id

  secret_string = jsonencode({
    username          = var.db_username
    password          = random_password.rds.result
    host              = aws_db_instance.mlflow.address
    port              = 5432
    dbname            = var.db_name
    backend_store_uri = "postgresql://${var.db_username}:${random_password.rds.result}@${aws_db_instance.mlflow.address}:5432/${var.db_name}"
  })
}
