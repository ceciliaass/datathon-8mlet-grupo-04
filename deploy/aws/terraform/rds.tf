resource "aws_db_subnet_group" "mlflow" {
  name       = "${var.project_name}-db-subnets"
  subnet_ids = data.aws_subnets.default.ids
}

resource "aws_db_instance" "mlflow" {
  identifier     = "${var.project_name}-mlflow-db"
  engine         = "postgres"
  engine_version = "16"
  instance_class = var.db_instance_class

  allocated_storage = var.db_allocated_storage
  storage_type      = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = random_password.rds.result

  db_subnet_group_name   = aws_db_subnet_group.mlflow.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  # Fica em subnet publica (sem VPC/NAT proprios), mas sem IP publico e com
  # acesso restrito pelo SG a só as tasks ECS - ver network.tf.
  publicly_accessible = false
  multi_az            = false

  skip_final_snapshot = true # permite `terraform destroy` limpo (dados recriaveis via warm start)
  deletion_protection = false
  apply_immediately   = true
}
