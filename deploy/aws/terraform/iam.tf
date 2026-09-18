data "aws_iam_policy_document" "ecs_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# ---------------------------------------------------------------------------
# Execution role: usada pelo AGENTE do ECS (nao pelo codigo da app) para dar
# pull na imagem no ECR, mandar logs pro CloudWatch e ler o secret do RDS na
# hora de injetar `MLFLOW_BACKEND_STORE_URI` como env var no container.
# ---------------------------------------------------------------------------
resource "aws_iam_role" "ecs_execution" {
  name               = "${var.project_name}-ecs-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
}

resource "aws_iam_role_policy_attachment" "ecs_execution_managed" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy_document" "ecs_execution_secrets" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.rds.arn]
  }
}

resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name   = "${var.project_name}-ecs-execution-secrets"
  role   = aws_iam_role.ecs_execution.id
  policy = data.aws_iam_policy_document.ecs_execution_secrets.json
}

# ---------------------------------------------------------------------------
# Task role do FastAPI: le/escreve as duas tabelas DynamoDB do bandit.
# ---------------------------------------------------------------------------
resource "aws_iam_role" "fastapi_task" {
  name               = "${var.project_name}-fastapi-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
}

data "aws_iam_policy_document" "fastapi_task_dynamodb" {
  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:Scan",
      "dynamodb:BatchGetItem",
    ]
    resources = [
      aws_dynamodb_table.bandit_arms.arn,
      aws_dynamodb_table.bandit_decisions.arn,
    ]
  }
}

resource "aws_iam_role_policy" "fastapi_task_dynamodb" {
  name   = "${var.project_name}-fastapi-dynamodb"
  role   = aws_iam_role.fastapi_task.id
  policy = data.aws_iam_policy_document.fastapi_task_dynamodb.json
}

# ---------------------------------------------------------------------------
# Task role do MLflow: le/escreve o bucket S3 (artifact store), sob o prefixo
# mlflow-artifacts/.
# ---------------------------------------------------------------------------
resource "aws_iam_role" "mlflow_task" {
  name               = "${var.project_name}-mlflow-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
}

data "aws_iam_policy_document" "mlflow_task_s3" {
  statement {
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.data.arn]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["mlflow-artifacts/*"]
    }
  }

  statement {
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]
    resources = ["${aws_s3_bucket.data.arn}/mlflow-artifacts/*"]
  }
}

resource "aws_iam_role_policy" "mlflow_task_s3" {
  name   = "${var.project_name}-mlflow-s3"
  role   = aws_iam_role.mlflow_task.id
  policy = data.aws_iam_policy_document.mlflow_task_s3.json
}
