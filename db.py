import mysql.connector
from src.config import settings
import mysql.connector




def get_conn():
    return mysql.connector.connect(
        host=settings.TIDB_HOST,
        port=settings.TIDB_PORT,
        user=settings.TIDB_USER,
        password=settings.TIDB_PASS,
        database=settings.TIDB_DB,
        ssl_ca=settings.TIDB_CA,
        ssl_verify_identity=True,
        
    )

def execute(query: str, params=None, dictionary=False):
    conn = get_conn()
    cur = conn.cursor(dictionary=dictionary)
    cur.execute(query, params or ())
    conn.commit()
    cur.close()
    conn.close()

def fetchall(query: str, params=None, dictionary=True):
    conn = get_conn()
    cur = conn.cursor(dictionary=dictionary)
    cur.execute(query, params or ())
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
