variable "aws_region" {
  description = "Regiao AWS onde o stack sera criado. us-east-2 (Ohio) escolhida por custo (uma das regioes mais baratas dos EUA); sa-east-1 (Sao Paulo) tem menor latencia mas custo ~15-25% mais alto."
  type        = string
  default     = "us-east-2"
}

variable "project_name" {
  description = "Prefixo usado no nome de todos os recursos (tambem usado nos ARNs da policy em deploy/aws/iam/deploy-user-policy.json - se mudar aqui, atualize la tambem)."
  type        = string
  default     = "datathon-bandit"
}

variable "environment" {
  description = "Rotulo de ambiente, usado so em tags."
  type        = string
  default     = "demo"
}

variable "container_image_tag" {
  description = "Tag das imagens Docker publicadas no ECR (fastapi e mlflow) pelo deploy/aws/push_images.sh."
  type        = string
  default     = "latest"
}

variable "fastapi_cpu" {
  type    = number
  default = 256
}

variable "fastapi_memory" {
  type    = number
  default = 512
}

variable "mlflow_cpu" {
  type    = number
  default = 256
}

variable "mlflow_memory" {
  description = "512-1024MiB nao e suficiente (mlflow com multiplos workers + boto3 + psycopg2 + sqlalchemy estoura e o container morre com OOMKilled/exit 137, mesmo com --workers 1 no entrypoint) - 2048 e a margem segura observada, ainda dentro do tier de CPU 256 do Fargate."
  type        = number
  default     = 2048
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "db_allocated_storage" {
  type    = number
  default = 20
}

variable "db_name" {
  type    = string
  default = "mlflow"
}

variable "db_username" {
  type    = string
  default = "mlflow_admin"
}

variable "alb_ingress_cidr" {
  description = "CIDR liberado nas portas 80 (FastAPI) e 5000 (MLflow UI) do ALB. Restrinja para o seu IP (ex.: \"200.1.2.3/32\") se quiser reduzir exposicao publica."
  type        = string
  default     = "0.0.0.0/0"
}

variable "log_retention_days" {
  type    = number
  default = 7
}
