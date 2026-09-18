#!/bin/bash
# Builda e publica as imagens fastapi/mlflow no ECR.
#
# Rodar a partir da raiz do repositorio:
#   AWS_REGION=us-east-2 ./deploy/aws/push_images.sh
#
# Requer: aws cli configurado (`aws sts get-caller-identity` funcionando) e
# docker rodando localmente.
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-2}"
PROJECT_NAME="${PROJECT_NAME:-datathon-bandit}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "==> Autenticando no ECR ($REGISTRY)"
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$REGISTRY"

for SERVICE in fastapi mlflow; do
  REPO="${PROJECT_NAME}-${SERVICE}"
  IMAGE="${REGISTRY}/${REPO}:${IMAGE_TAG}"

  echo "==> Build ${SERVICE} (linux/arm64) -> ${IMAGE}"
  docker build --platform linux/arm64 -f "deploy/Dockerfile.${SERVICE}" -t "$IMAGE" .

  echo "==> Push ${IMAGE}"
  docker push "$IMAGE"
done

cat <<EOF
==> Concluido. Se os servicos ECS ja existirem, force um novo deployment:
    aws ecs update-service --cluster ${PROJECT_NAME}-cluster --service ${PROJECT_NAME}-fastapi --force-new-deployment --region $AWS_REGION
    aws ecs update-service --cluster ${PROJECT_NAME}-cluster --service ${PROJECT_NAME}-mlflow  --force-new-deployment --region $AWS_REGION
EOF
