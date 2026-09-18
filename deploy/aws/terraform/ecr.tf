resource "aws_ecr_repository" "fastapi" {
  name                 = "${var.project_name}-fastapi"
  image_tag_mutability = "MUTABLE"
  force_delete         = true # permite `terraform destroy` mesmo com imagens dentro

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "mlflow" {
  name                 = "${var.project_name}-mlflow"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}
