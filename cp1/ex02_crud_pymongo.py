"""
Exercício 2 — CRUD com PyMongo (coleção vulnerabilidades)
"""
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

URI = "mongodb://localhost:27017/"

VULNS = [
    {"cve_id": "CVE-2024-001", "tipo": "SQL Injection", "severidade": "Alta", "corrigida": False},
    {"cve_id": "CVE-2024-002", "tipo": "XSS", "severidade": "Media", "corrigida": True},
    {"cve_id": "CVE-2024-003", "tipo": "Path Traversal", "severidade": "Critica", "corrigida": False},
]


def conectar():
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")          # força a validação da conexão
        return client
    except ServerSelectionTimeoutError as e:
        raise SystemExit(f"[ERRO] Falha ao conectar no MongoDB: {e}")


def main():
    client = conectar()
    col = client["cp01"]["vulnerabilidades"]
    col.delete_many({})                       # ambiente limpo a cada execução

    # ---------- CREATE ----------
    res = col.insert_many(VULNS)
    print(f"{len(res.inserted_ids)} vulnerabilidades inseridas.\n")

    # ---------- READ ----------
    print("-- Buscar severidade='Alta' --")
    for doc in col.find({"severidade": "Alta"}):
        print(f"{doc['cve_id']}: {doc['tipo']}")

    # ---------- UPDATE ----------
    up = col.update_one({"cve_id": "CVE-2024-001"}, {"$set": {"corrigida": True}})
    print(f"\n{up.modified_count} documento modificado")

    print(f"Vulnerabilidades ainda abertas: {col.count_documents({'corrigida': False})}")

    # ---------- DELETE ----------
    de = col.delete_one({"cve_id": "CVE-2024-002"})
    print(f"\n{de.deleted_count} documento removido (CVE-2024-002)")

    print("\n-- Estado final --")
    for doc in col.find({}, {"_id": 0}):
        print(doc)

    client.close()


if __name__ == "__main__":
    main()
