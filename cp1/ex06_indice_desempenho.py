"""
Exercício 6 — Índice e desempenho (1000 eventos no MongoDB)
"""
import random
from datetime import datetime, timedelta

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

URI = "mongodb://localhost:27017/"
IPS = ["185.220.101.1", "91.240.118.172", "45.33.32.156", "192.168.1.10"]
ALVO = "185.220.101.1"

random.seed(42)   # reprodutibilidade


def conectar():
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        return client
    except ServerSelectionTimeoutError as e:
        raise SystemExit(f"[ERRO] Falha ao conectar no MongoDB: {e}")


def gerar_eventos(n=1000):
    base = datetime(2025, 2, 20, 8, 0, 0)
    eventos = []
    for i in range(n):
        eventos.append({
            "ts": base + timedelta(seconds=i),
            "ip": IPS[i % len(IPS)],          # distribuição uniforme: 250 por IP
            "tipo": random.choice(["OK", "FAIL"]),
            "porta": random.choice([22, 80, 443]),
        })
    return eventos


def main():
    client = conectar()
    col = client["cp01"]["eventos_massa"]
    col.drop()

    col.insert_many(gerar_eventos(1000))
    print(f"{col.count_documents({})} eventos inseridos.")

    col.create_index("ip")
    print("Índice criado em 'ip'.")

    print(f"Eventos do IP {ALVO}: {col.count_documents({'ip': ALVO})}")

    # Prova de que o índice está sendo usado: IXSCAN em vez de COLLSCAN
    plano = col.find({"ip": ALVO}).explain()["queryPlanner"]["winningPlan"]
    print(f"Plano de execução: {plano}")

    # Comentário: sem índice o MongoDB faz COLLSCAN, varrendo os 1000 documentos um a um
    # (custo O(n)); com índice ele percorre uma B-tree ordenada e vai direto às chaves (~O(log n)),
    # diferença que vira minutos vs. milissegundos quando a coleção chega a milhões de eventos.

    client.close()


if __name__ == "__main__":
    main()
