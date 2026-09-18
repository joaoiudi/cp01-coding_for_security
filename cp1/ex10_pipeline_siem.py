"""
Exercício 10 (Desafio) — Mini-pipeline SIEM: log -> MongoDB -> ML

Fluxo: ler auth.log -> normalizar -> inserir no MongoDB -> agregar FAILs por IP
       -> montar dataset -> treinar classificador -> prever IP novo.
"""
import os
import re

import numpy as np
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from sklearn.ensemble import RandomForestClassifier

URI = "mongodb://localhost:27017/"
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth.log")
LIMIAR = 5          # a partir de 5 falhas o IP é rotulado como suspeito
IP_NOVO = [[8]]

# TIMESTAMP TIPO usuario=NOME ip=IP
PADRAO = re.compile(
    r"^(?P<data>\d{4}-\d{2}-\d{2})\s+(?P<hora>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<tipo>\w+)\s+usuario=(?P<usuario>\S+)\s+ip=(?P<ip>\S+)$"
)


def conectar():
    try:
        client = MongoClient(URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        return client
    except ServerSelectionTimeoutError as e:
        raise SystemExit(f"[ERRO] Falha ao conectar no MongoDB: {e}")


# ---------- (1) parsing / normalização ----------
def parse_log(caminho):
    docs = []
    try:
        with open(caminho, encoding="utf-8") as f:
            for n, linha in enumerate(f, start=1):
                linha = linha.strip()
                if not linha:
                    continue
                m = PADRAO.match(linha)
                if not m:
                    print(f"[AVISO] linha {n} fora do formato, ignorada: {linha}")
                    continue
                d = m.groupdict()
                docs.append({
                    "timestamp": f"{d['data']} {d['hora']}",
                    "tipo": d["tipo"],
                    "usuario": d["usuario"],
                    "ip": d["ip"],
                })
    except FileNotFoundError:
        raise SystemExit(f"[ERRO] auth.log não encontrado em {caminho}")
    return docs


# ---------- (3) agregação ----------
def fails_por_ip(col):
    pipeline = [
        {"$match": {"tipo": "FAIL"}},
        {"$group": {"_id": "$ip", "fails": {"$sum": 1}}},
        {"$sort": {"fails": -1}},
    ]
    return list(col.aggregate(pipeline))


def main():
    client = conectar()
    col = client["cp01"]["auth_events"]
    col.delete_many({})

    # ---------- (2) carga no MongoDB ----------
    docs = parse_log(LOG)
    col.insert_many(docs)
    print(f"Eventos inseridos no MongoDB: {col.count_documents({})}\n")

    agregado = fails_por_ip(col)
    print("-- FAILs por IP (agregação) --")
    for item in agregado:
        suspeito = 1 if item["fails"] >= LIMIAR else 0
        print(f"{item['_id']:16s} -> {item['fails']:2d} FAILs (suspeito={suspeito})")

    # ---------- (4) dataset ----------
    X = [[item["fails"]] for item in agregado]
    y = [1 if item["fails"] >= LIMIAR else 0 for item in agregado]

    # Três IPs reais são poucos para treinar: acrescento pontos de referência
    # rotulados pela mesma regra de negócio, para o modelo enxergar a fronteira.
    for fails in [0, 1, 2, 4, 6, 7, 9, 12]:
        X.append([fails])
        y.append(1 if fails >= LIMIAR else 0)

    X, y = np.array(X), np.array(y)
    print(f"\nDataset de treino: {X.ravel().tolist()} rótulos {y.tolist()}")

    # ---------- (5) treino e previsão ----------
    modelo = RandomForestClassifier(random_state=42)
    modelo.fit(X, y)

    pred = modelo.predict(IP_NOVO)[0]
    rotulo = "Suspeito" if pred == 1 else "Normal"
    print(f"Previsão para IP com {IP_NOVO[0][0]} falhas -> {rotulo} ({pred})")

    client.close()


if __name__ == "__main__":
    main()
