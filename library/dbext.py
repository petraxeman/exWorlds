import psycopg2 as pgs
from psycopg2 import pool
from psycopg2.extras import DictRow, NamedTupleCursor
from psycopg2.extras import execute_values
from contextlib import contextmanager
from typing import List, Tuple, Any



class Postgres:
    def __init__(self, app=None):
        self._pool = None
        self.host = "localhost"
        self.port = 5432
        self.dbname = "exworlds"
        self.db_user = ""
        self.db_passwd = ""

    def init_app(self, app):
        # Получение параметров из конфигурации
        db_config = app.config
        try:
            host, port = db_config["DB_SERVER"].split(":")
            self.host = host
            self.port = int(port)
            self.dbname = db_config["POSTGRES_DB"]
            self.db_user = db_config["POSTGRES_USER"]
            self.db_passwd = db_config["POSTGRES_PASSWORD"]

            # Создание пула соединений
            self._pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                user=self.db_user,
                password=self.db_passwd,
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                cursor_factory=NamedTupleCursor
            )
            app.extensions["postgresdb"] = self
        except Exception as e:
            raise RuntimeError(f"Database initialization error: {e}")

    @contextmanager
    def _get_connection(self):
        "Получение соединения из пула с автоматическим возвратом."
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)

    def execute(self, query: str, args: Tuple = None) -> None:
        "Выполнение запроса без возврата данных."
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, args)
                    conn.commit()
        except Exception as e:
            raise RuntimeError(f"Query execution error: {e}")

    def fetchall(self, query: str, args: Tuple = None) -> List[Tuple[Any]]:
        "Выполнение запроса с возвратом всех результатов."
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, args)
                    return cur.fetchall()
        except Exception as e:
            raise RuntimeError(f"Fetch all error: {e}")
    
    def fetchone(self, query: str, args: Tuple = None) -> List[Tuple[Any]]:
        "Выполнение запроса с возвратом одного результатов."
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, args)
                    return cur.fetchone()
        except Exception as e:
            raise RuntimeError(f"Fetch all error: {e}")
    
    def batch_insert(self, query: str, values: List[Tuple]) -> None:
        "Быстрая вставка нескольких записей."
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    execute_values(cur, query, values)
                    conn.commit()
        except Exception as e:
            raise RuntimeError(f"Batch insert error: {e}")
    
    def get_user_by_username(self, username: str):
        query = "SELECT * FROM users WHERE username = %s"
        result = self.fetchone(query, (username,))
        if result:
            return result._asdict()
        else:
            return None