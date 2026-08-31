"""
Script de demonstração do serviço, pensado para o vídeo pitch (Etapa 8):
mostra o ciclo completo -- recomendar, dar feedback, ver o bandit aprender --
contra uma instância rodando localmente (`uvicorn app.main:app`).

Uso:
    uvicorn app.main:app --port 8000 &
    python demo_client.py
"""
import random

import requests

BASE_URL = "http://127.0.0.1:8000"


def main() -> None:
    print("=== Estado inicial do bandit ===")
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

    print("\n=== Estado final do bandit, após aprender com os 20 eventos ===")
    print(requests.get(f"{BASE_URL}/stats").json())


if __name__ == "__main__":
    main()
