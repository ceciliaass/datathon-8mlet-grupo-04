# Bucket unico para os artifacts do MLflow (prefixo mlflow-artifacts/) e,
# opcionalmente, dados do Kaggle (prefixos raw/ e processed/). Um bucket so
# reduz recursos Terraform e superficie de "coisas para lembrar de destruir";
# a separacao logica e feita por prefixo + IAM (ver iam.tf), nao por bucket.
resource "aws_s3_bucket" "data" {
  bucket        = "${var.project_name}-data-${data.aws_caller_identity.current.account_id}"
  force_destroy = true # permite `terraform destroy` mesmo com objetos dentro
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
