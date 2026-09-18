"""
Exercício 4 — Query parametrizada (defesa contra SQL Injection)

ATENÇÃO: exercício defensivo. A função insegura existe apenas para demonstrar
o vazamento e deve ser executada SOMENTE no banco local de laboratório.
"""
import mysql.connector
from mysql.connector import Error

CONFIG = {"host": "localhost", "port": 3306, "user": "root", "password": "root"}
DB = "cp01"

USUARIOS = [("admin", "admin@x.com"), ("ana", "ana@x.com"), ("bruno", "bruno@x.com")]
ENTRADA = "' OR '1'='1"


def conectar():
    try:
        conn = mysql.connector.connect(**CONFIG)
    except Error as e:
        raise SystemExit(f"[ERRO] Falha ao conectar no MySQL: {e}")
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB}")
    cur.close()
    conn.database = DB
    return conn


def preparar(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS usuarios")
    cur.execute("""
        CREATE TABLE usuarios (
            id    INT AUTO_INCREMENT PRIMARY KEY,
            nome  VARCHAR(50) NOT NULL,
            email VARCHAR(80) NOT NULL
        )
    """)
    cur.executemany("INSERT INTO usuarios (nome, email) VALUES (%s,%s)", USUARIOS)
    conn.commit()
    cur.close()


def busca_insegura(conn, nome):
    """VULNERÁVEL: concatena a entrada direto na string SQL."""
    sql = f"SELECT nome, email FROM usuarios WHERE nome = '{nome}'"
    cur = conn.cursor()
    cur.execute(sql)
    linhas = cur.fetchall()
    cur.close()
    return linhas


def busca_segura(conn, nome):
    """SEGURA: a entrada viaja como parâmetro, nunca como código SQL."""
    cur = conn.cursor()
    cur.execute("SELECT nome, email FROM usuarios WHERE nome = %s", (nome,))
    linhas = cur.fetchall()
    cur.close()
    return linhas


def main():
    conn = conectar()
    preparar(conn)

    inseguro = busca_insegura(conn, ENTRADA)
    print(f"[INSEGURO] entrada={ENTRADA}  -> {len(inseguro)} usuários (VAZAMENTO)")
    for linha in inseguro:
        print(f"   {linha[0]} | {linha[1]}")

    seguro = busca_segura(conn, ENTRADA)
    print(f"[SEGURO]   entrada={ENTRADA}  -> {len(seguro)} usuários (defesa OK)")

    # Sanidade: com uma entrada legítima a versão segura funciona normalmente
    print(f"[SEGURO]   entrada=ana         -> {len(busca_segura(conn, 'ana'))} usuário")

    conn.close()


if __name__ == "__main__":
    main()
