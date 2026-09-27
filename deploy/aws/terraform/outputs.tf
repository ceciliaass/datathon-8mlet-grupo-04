output "alb_dns_name" {
  description = "DNS do ALB. Porta 80 = FastAPI (/docs, /recomendar, /feedback, /stats). Porta 5000 = MLflow UI."
  value       = aws_lb.main.dns_name
}

output "ecr_fastapi_repository_url" {
  value = aws_ecr_repository.fastapi.repository_url
}

output "ecr_mlflow_repository_url" {
  value = aws_ecr_repository.mlflow.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "dynamodb_arms_table" {
  value = aws_dynamodb_table.bandit_arms.name
}

output "dynamodb_decisions_table" {
  value = aws_dynamodb_table.bandit_decisions.name
}

output "rds_endpoint" {
  value     = aws_db_instance.mlflow.address
  sensitive = true
}

output "s3_bucket_name" {
  value = aws_s3_bucket.data.bucket
}

output "secrets_manager_secret_arn" {
  value = aws_secretsmanager_secret.rds.arn
}
