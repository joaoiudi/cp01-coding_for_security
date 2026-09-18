"""
Exercício 5 — Transação com rollback (transferência entre contas)
"""
import mysql.connector
from mysql.connector import Error

CONFIG = {"host": "localhost", "port": 3306, "user": "root", "password": "root"}
DB = "cp01"

CONTAS = [(1, "Alice", 1000), (2, "Bob", 500)]


def conectar():
    try:
        conn = mysql.connector.connect(**CONFIG)
    except Error as e:
        raise SystemExit(f"[ERRO] Falha ao conectar no MySQL: {e}")
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB}")
    cur.close()
    conn.database = DB
    conn.autocommit = False        # controle manual do commit/rollback
    return conn


def preparar(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS contas")
    cur.execute("""
        CREATE TABLE contas (
            id      INT PRIMARY KEY,
            titular VARCHAR(50) NOT NULL,
            saldo   DECIMAL(10,2) NOT NULL
        ) ENGINE=InnoDB
    """)                            # InnoDB é obrigatório: MyISAM não suporta transação
    cur.executemany("INSERT INTO contas (id, titular, saldo) VALUES (%s,%s,%s)", CONTAS)
    conn.commit()
    cur.close()


def saldo(conn, conta_id):
    cur = conn.cursor()
    cur.execute("SELECT saldo FROM contas WHERE id = %s", (conta_id,))
    valor = cur.fetchone()[0]
    cur.close()
    return float(valor)


def transferir(conn, origem, destino, valor):
    """Débito + crédito na mesma transação: ou as duas operações valem, ou nenhuma."""
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE contas SET saldo = saldo - %s WHERE id = %s AND saldo >= %s",
            (valor, origem, valor),
        )
        if cur.rowcount == 0:
            raise ValueError(f"conta origem {origem} inexistente ou saldo insuficiente")

        cur.execute("UPDATE contas SET saldo = saldo + %s WHERE id = %s", (valor, destino))
        if cur.rowcount == 0:
            raise ValueError(f"conta destino {destino} inexistente")

        conn.commit()
        return True, "OK"
    except (ValueError, Error) as e:
        conn.rollback()           # desfaz o débito já executado
        return False, str(e)
    finally:
        cur.close()


def main():
    conn = conectar()
    preparar(conn)
    print(f"Saldos iniciais: Alice={saldo(conn,1):.0f}, Bob={saldo(conn,2):.0f}\n")

    ok, msg = transferir(conn, 1, 2, 200)
    print(f"Transferência 1 {'OK' if ok else 'FALHOU (' + msg + ')'}. "
          f"Alice={saldo(conn,1):.0f}, Bob={saldo(conn,2):.0f}")

    ok, msg = transferir(conn, 1, 99, 100)
    print(f"Transferência 2 {'OK' if ok else 'FALHOU'} ({msg}). Rollback. "
          f"Alice={saldo(conn,1):.0f}")

    print("\nSaldo de Alice inalterado após o rollback -> atomicidade garantida.")
    conn.close()


if __name__ == "__main__":
    main()
