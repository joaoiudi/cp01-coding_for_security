"""
Exercício 3 — Agregação: Top 3 IPs com mais eventos do tipo FAIL
"""
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

URI = "mongodb://localhost:27017/"

EVENTOS = [
    {"tipo": "FAIL", "ip": "185.220.101.1"}, {"tipo": "FAIL", "ip": "185.220.101.1"},
    {"tipo": "OK",   "ip": "192.168.1.10"},  {"tipo": "FAIL", "ip": "91.240.118.172"},
    {"tipo": "FAIL", "ip": "185.220.101.1"}, {"tipo": "FAIL", "ip": "91.240.118.172"},
    {"tipo": "FAIL", "ip": "45.33.32.156"},  {"tipo": "FAIL", "ip": "185.220.101.1"},
]


def conectar():
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        return client
    except ServerSelectionTimeoutError as e:
        raise SystemExit(f"[ERRO] Falha ao conectar no MongoDB: {e}")


def top_ips_fail(col, limite=3):
    """Agregação no servidor — evita trazer todos os docs e contar em laço no Python."""
    pipeline = [
        {"$match": {"tipo": "FAIL"}},
        {"$group": {"_id": "$ip", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": limite},
    ]
    return list(col.aggregate(pipeline))


def main():
    client = conectar()
    col = client["cp01"]["eventos"]
    col.delete_many({})
    col.insert_many(EVENTOS)

    print(f"{col.count_documents({})} eventos inseridos.\n")
    print("-- Top 3 IPs com mais FAIL --")
    for doc in top_ips_fail(col):
        print(f"{doc['_id']} -> {doc['total']}")

    client.close()


if __name__ == "__main__":
    main()
