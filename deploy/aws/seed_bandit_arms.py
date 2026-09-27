"""
Fallback opcional para (re)popular a tabela DynamoDB de contadores do bandit
com o warm start usado localmente (ver
data/processed/bank-term-deposit-subscription_eda/arm_stats.csv).

O Terraform ja faz esse seed declarativamente (aws_dynamodb_table_item em
deploy/aws/terraform/dynamodb.tf) na primeira vez que a tabela e criada. Use
este script somente se quiser resetar os contadores manualmente sem re-rodar
`terraform apply` (ex.: depois de testes que "sujaram" os numeros antes de
uma demonstracao).

Uso:
    AWS_REGION=sa-east-1 DYNAMODB_TABLE_ARMS=datathon-bandit-bandit-arms \
        python deploy/aws/seed_bandit_arms.py
"""
import os

import boto3

AWS_REGION = os.environ.get("AWS_REGION", "sa-east-1")
TABLE_NAME = os.environ["DYNAMODB_TABLE_ARMS"]

# Mesmos numeros de data/processed/bank-term-deposit-subscription_eda/arm_stats.csv
ARM_STATS = {
    "cellular": {"success_count": 4369, "fail_count": 24916},
    "telephone": {"success_count": 390, "fail_count": 2516},
}


def main() -> None:
    table = boto3.resource("dynamodb", region_name=AWS_REGION).Table(TABLE_NAME)
    for arm, counts in ARM_STATS.items():
        table.put_item(Item={"arm": arm, **counts})
        print(f"Seed aplicado: {arm} -> {counts}")


if __name__ == "__main__":
    main()
