# Sem VPC/NAT Gateway proprios: reaproveita a VPC default da conta e suas
# subnets publicas para manter o custo baixo (ambiente de demo de curta duracao).
# As tasks Fargate recebem IP publico (assign_public_ip=true no ecs.tf), mas o
# trafego de entrada e restrito pelos Security Groups abaixo.

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Trafego publico para o ALB (FastAPI na porta 80, MLflow UI na porta 5000)."
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP - FastAPI"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.alb_ingress_cidr]
  }

  ingress {
    description = "HTTP - MLflow UI"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = [var.alb_ingress_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_tasks" {
  name        = "${var.project_name}-ecs-tasks-sg"
  description = "Trafego permitido somente vindo do ALB para as tasks Fargate (fastapi:8000, mlflow:5000)."
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "FastAPI (via ALB)"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    description     = "MLflow (via ALB)"
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Postgres acessivel somente pelas tasks ECS (backend store do MLflow)."
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "Postgres (via tasks ECS)"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
