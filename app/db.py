import psycopg2
from psycopg2 import OperationalError, DatabaseError
from psycopg2.extras import RealDictCursor


class Database:
    def __init__(self, dsn: str = "dbname=miniorm_db user=postgres password=mysecretpassword host=localhost port=5432"):
        self.dsn = dsn
        self._connection = None

    def connect(self):
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(self.dsn)
                self._connection.autocommit = False
            except OperationalError as e:
                raise ConnectionError(f"Database connection failed: {e}")

    def close(self):
        if self._connection and not self._connection.closed:
            self._connection.close()
        self._connection = None

    def commit(self):
        if self._connection:
            self._connection.commit()

    def rollback(self):
        if self._connection:
            self._connection.rollback()

    def execute(self, sql: str, params=None, fetch_result: bool = False):
        """
        Execute a SQL statement.
        If fetch_result=True, return one row (useful for INSERT ... RETURNING).
        """
        self.connect()
        try:
            cursor_factory = RealDictCursor if fetch_result else None
            with self._connection.cursor(cursor_factory=cursor_factory) as cursor:
                cursor.execute(sql, params)
                if fetch_result:
                    return cursor.fetchone()
        except DatabaseError as e:
            self.rollback()
            raise e

    def fetchone(self, sql: str, params=None):
        self.connect()
        try:
            with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()
        except DatabaseError as e:
            self.rollback()
            raise e

    def fetchall(self, sql: str, params=None):
        self.connect()
        try:
            with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except DatabaseError as e:
            self.rollback()
            raise e