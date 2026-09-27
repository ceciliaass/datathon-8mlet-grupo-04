resource "aws_cloudwatch_log_group" "fastapi" {
  name              = "/ecs/${var.project_name}-fastapi"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "mlflow" {
  name              = "/ecs/${var.project_name}-mlflow"
  retention_in_days = var.log_retention_days
}
