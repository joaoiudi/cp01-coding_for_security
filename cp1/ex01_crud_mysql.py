"""
Exercício 1 — Modelagem e CRUD SQL (MySQL)
Tabela: ativos(id PK AUTO_INCREMENT, nome, ip UNIQUE, tipo,
               criticidade ENUM('baixa','media','alta'), status)
"""
import mysql.connector
from mysql.connector import Error

CONFIG = {"host": "localhost", "port": 3306, "user": "root", "password": "root"}
DB = "cp01"

ATIVOS = [
    ("SRV-WEB01", "192.168.1.10", "servidor", "alta", "ativo"),
    ("PC-RH03", "192.168.1.45", "estacao", "baixa", "ativo"),
    ("SW-CORE01", "192.168.1.1", "switch", "media", "inativo"),
]


def conectar():
    """Conecta ao MySQL e garante que o banco cp01 existe."""
    try:
        conn = mysql.connector.connect(**CONFIG)
    except Error as e:
        raise SystemExit(f"[ERRO] Falha ao conectar no MySQL: {e}")
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB}")
    cur.close()
    conn.database = DB
    return conn


def criar_tabela(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS ativos")
    cur.execute("""
        CREATE TABLE ativos (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            nome        VARCHAR(50) NOT NULL,
            ip          VARCHAR(15) NOT NULL UNIQUE,
            tipo        VARCHAR(30) NOT NULL,
            criticidade ENUM('baixa','media','alta') NOT NULL,
            status      VARCHAR(20) NOT NULL
        )
    """)
    conn.commit()
    cur.close()


# ---------- CREATE ----------
def inserir(conn, ativos):
    sql = "INSERT INTO ativos (nome, ip, tipo, criticidade, status) VALUES (%s,%s,%s,%s,%s)"
    cur = conn.cursor()
    inseridos = 0
    for ativo in ativos:
        try:
            cur.execute(sql, ativo)          # query parametrizada
            inseridos += 1
        except mysql.connector.IntegrityError as e:
            # IP duplicado viola a constraint UNIQUE
            print(f"Erro de UNIQUE tratado: IP {ativo[1]} já cadastrado ({e.errno})")
    conn.commit()
    cur.close()
    return inseridos


# ---------- READ ----------
def listar_por_tipo(conn, tipo):
    cur = conn.cursor()
    cur.execute("SELECT nome, ip, criticidade, status FROM ativos WHERE tipo = %s", (tipo,))
    linhas = cur.fetchall()
    cur.close()
    return linhas


# ---------- UPDATE ----------
def atualizar_status(conn, nome, novo_status):
    cur = conn.cursor()
    cur.execute("UPDATE ativos SET status = %s WHERE nome = %s", (novo_status, nome))
    conn.commit()
    afetados = cur.rowcount
    cur.close()
    return afetados


# ---------- DELETE ----------
def remover(conn, nome):
    cur = conn.cursor()
    cur.execute("DELETE FROM ativos WHERE nome = %s", (nome,))
    conn.commit()
    afetados = cur.rowcount
    cur.close()
    return afetados


def main():
    conn = conectar()
    criar_tabela(conn)

    print(f"{inserir(conn, ATIVOS)} ativos inseridos.\n")

    print("-- Listar tipo='servidor' --")
    for nome, ip, crit, status in listar_por_tipo(conn, "servidor"):
        print(f"{nome} | {ip} | {crit} | {status}")

    print(f"\n{atualizar_status(conn, 'SW-CORE01', 'ativo')} registro atualizado")

    print("\n-- Tentando inserir IP duplicado --")
    inserir(conn, [("SRV-CLONE", "192.168.1.10", "servidor", "alta", "ativo")])

    print(f"\n{remover(conn, 'PC-RH03')} registro removido (PC-RH03)")

    print("\n-- Estado final --")
    cur = conn.cursor()
    cur.execute("SELECT id, nome, ip, tipo, criticidade, status FROM ativos")
    for linha in cur.fetchall():
        print(linha)
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
