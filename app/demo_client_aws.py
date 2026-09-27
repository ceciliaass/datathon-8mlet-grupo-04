"""
Mesmo script de demonstração de demo_client.py, mas apontando para o
serviço já implantado na AWS (deploy/aws/) em vez de localhost -- útil
para preparar/validar o ambiente antes do vídeo pitch (Etapa 8) sem
precisar subir nada localmente.

Uso:
    python app/demo_client_aws.py

Se o DNS do ALB mudar (ex.: depois de um `terraform apply` que recria o
load balancer), atualize BASE_URL abaixo ou rode:
    terraform -chdir=deploy/aws/terraform output -raw alb_dns_name
"""
import random

import requests

BASE_URL = "http://datathon-bandit-alb-361652049.us-east-2.elb.amazonaws.com"


def main() -> None:
    print("=== Estado inicial do bandit (AWS) ===")
    print(requests.get(f"{BASE_URL}/stats").json())

    print("\n=== Simulando 20 clientes chegando e convertendo (ou não) ===")
    for i in range(20):
        contexto = {
            "idade": random.randint(20, 70),
            "poutcome": random.choice(["unknown", "failure", "success", "other"]),
            "previous": random.choice([0, 0, 0, 1, 2]),
        }
        recomendacao = requests.post(f"{BASE_URL}/recomendar", json=contexto).json()
        decision_id, arm = recomendacao["decision_id"], recomendacao["arm"]

        # Em produção este "converteu" viria de um evento real, minutos/dias
        # depois. Aqui simulamos com a taxa histórica aproximada de cada canal.
        taxa = {"cellular": 0.15, "telephone": 0.13}[arm]
        converteu = random.random() < taxa

        feedback = requests.post(
            f"{BASE_URL}/feedback",
            json={"decision_id": decision_id, "converteu": converteu},
        ).json()
        print(f"cliente {i+1:02d}: canal={arm:<10} converteu={converteu} -> {feedback}")

    print("\n=== Estado final do bandit (AWS), após aprender com os 20 eventos ===")
    print(requests.get(f"{BASE_URL}/stats").json())
    print(f"\nMLflow UI: {BASE_URL}:5000")
    print(f"Swagger:   {BASE_URL}/docs")


if __name__ == "__main__":
    main()
