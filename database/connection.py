import psycopg2
import psycopg2.extras

from config import DB_CONFIG

class DatabaseError(Exception):
    "Вывод текста при ошибке"

def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        raise DatabaseError(
            "Не удалось подключится к БД"
        ) from e

def fetch_all(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()
    except psycopg2.Error as e:
        raise DatabaseError(f"Ошибка при запросе к БД {e}") from e
    
def fetch_one(query, params=None):
    rows = fetch_all(query, params)
    if rows:
        return rows[0]
    return None

def run_in_trans(action):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                return action(cur)
    except psycopg2.Error as e:
        raise DatabaseError(f"Ошибка при сохранение данных в БД {e}") from e
    finally:
        conn.close()