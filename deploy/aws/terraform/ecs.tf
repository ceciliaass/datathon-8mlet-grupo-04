resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
}

resource "aws_ecs_task_definition" "fastapi" {
  family                   = "${var.project_name}-fastapi"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.fastapi_cpu
  memory                   = var.fastapi_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.fastapi_task.arn

  runtime_platform {
    cpu_architecture        = "ARM64" # Graviton: mais barato, e builda nativo em Apple Silicon
    operating_system_family = "LINUX"
  }

  container_definitions = jsonencode([
    {
      name      = "fastapi"
      image     = "${aws_ecr_repository.fastapi.repository_url}:${var.container_image_tag}"
      essential = true

      portMappings = [
        { containerPort = 8000, protocol = "tcp" }
      ]

      environment = [
        { name = "BANDIT_STORE_BACKEND", value = "dynamodb" },
        { name = "AWS_REGION", value = var.aws_region },
        { name = "DYNAMODB_TABLE_ARMS", value = aws_dynamodb_table.bandit_arms.name },
        { name = "DYNAMODB_TABLE_DECISIONS", value = aws_dynamodb_table.bandit_decisions.name },
        { name = "MLFLOW_TRACKING_URI", value = "http://${aws_lb.main.dns_name}:5000" },
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.fastapi.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "fastapi"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "mlflow" {
  family                   = "${var.project_name}-mlflow"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.mlflow_cpu
  memory                   = var.mlflow_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.mlflow_task.arn

  runtime_platform {
    cpu_architecture        = "ARM64"
    operating_system_family = "LINUX"
  }

  container_definitions = jsonencode([
    {
      name      = "mlflow"
      image     = "${aws_ecr_repository.mlflow.repository_url}:${var.container_image_tag}"
      essential = true

      portMappings = [
        { containerPort = 5000, protocol = "tcp" }
      ]

      environment = [
        { name = "AWS_REGION", value = var.aws_region },
        { name = "MLFLOW_DEFAULT_ARTIFACT_ROOT", value = "s3://${aws_s3_bucket.data.bucket}/mlflow-artifacts/" },
        # "*" cobre o healthcheck do target group da ALB, que usa o IP
        # privado da task (dinamico a cada deploy) como Host header - nao da
        # para colocar isso numa allowlist estatica.
        { name = "MLFLOW_ALLOWED_HOSTS", value = "${aws_lb.main.dns_name},localhost,127.0.0.1,*" },
        # MLflow >=3.16 bloqueia por padrao (403) chamadas POST da UI cuja
        # origem nao seja localhost - sem isso a UI acessada pelo DNS da ALB
        # quebra com "INTERNAL_ERROR" (runs/search, experiments/search-datasets etc.)
        { name = "MLFLOW_SERVER_CORS_ALLOWED_ORIGINS", value = "http://${aws_lb.main.dns_name}:5000" },
      ]

      # Injetado pela execution role a partir do Secrets Manager - nunca em
      # texto plano na task definition.
      secrets = [
        {
          name      = "MLFLOW_BACKEND_STORE_URI"
          valueFrom = "${aws_secretsmanager_secret.rds.arn}:backend_store_uri::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.mlflow.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "mlflow"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "fastapi" {
  name            = "${var.project_name}-fastapi"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.fastapi.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true # obrigatorio sem NAT Gateway - so assim a task alcanca ECR/DynamoDB/etc.
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.fastapi.arn
    container_name   = "fastapi"
    container_port   = 8000
  }

  # Sem isso o ECS conta falhas de healthcheck do ALB desde o segundo 0 do
  # container e mata a task antes dela terminar de subir (loop de restart).
  health_check_grace_period_seconds = 90

  depends_on = [aws_lb_listener.fastapi]
}

resource "aws_ecs_service" "mlflow" {
  name            = "${var.project_name}-mlflow"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.mlflow.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.mlflow.arn
    container_name   = "mlflow"
    container_port   = 5000
  }

  # MLflow cria as tabelas no Postgres na primeira conexao - precisa de mais
  # tempo que o default (grace period 0) antes do ALB comecar a valer a
  # falha de healthcheck contra a task.
  health_check_grace_period_seconds = 120

  # A task definition referencia aws_secretsmanager_secret.rds.arn (o
  # "container" do secret), nao aws_secretsmanager_secret_version.rds (o
  # valor em si, que so existe depois do RDS terminar) - sem este
  # depends_on explicito o ECS tenta lancar a task antes do valor existir
  # e falha com "secret not found".
  depends_on = [aws_lb_listener.mlflow, aws_secretsmanager_secret_version.rds]
}
