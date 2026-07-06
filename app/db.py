import psycopg2
from psycopg2 import OperationalError, DatabaseError as PsycopgDatabaseError
from psycopg2.extras import RealDictCursor

from app.exceptions import ORMDatabaseError

class Database:
    def __init__(self, dsn: str = "dbname=miniorm_db user=postgres password=mysecretpassword host=localhost port=5432"):
        self.dsn = dsn
        self._connection = None

    def connect(self):
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(self.dsn)
                self._connection.autocommit = False
            except (OperationalError, PsycopgDatabaseError) as e:
                raise ORMDatabaseError(f"Database connection failed: {e}")
    def close(self):
        if self._connection and not self._connection.closed:
            self._connection.close()
        self._connection = None

    def commit(self):
        if self._connection:
            try:
                self._connection.commit()
            except PsycopgDatabaseError as e:
                self.rollback()
                raise ORMDatabaseError(f"Commit failed: {e}")

    def rollback(self):
        if self._connection:
            try:
                self._connection.rollback()
            except PsycopgDatabaseError as e:
                raise ORMDatabaseError(f"Rollback failed: {e}")

    def execute(self, sql: str, params=None, fetch_one: bool = False):
        """
        Execute a SQL statement.
        If fetch_one=True, return one row (useful for INSERT ... RETURNING).
        """
        self.connect()
        try:
            cursor_factory = RealDictCursor if fetch_one else None
            with self._connection.cursor(cursor_factory=cursor_factory) as cursor:
                cursor.execute(sql, params)
                if fetch_one:
                    return cursor.fetchone()
        except PsycopgDatabaseError as e:
            self.rollback()
            # Intercept raw psycopg2 error and re-raise our unified custom error label
            raise ORMDatabaseError(f"Execution failed: {e}") from e

    def fetchone(self, sql: str, params=None):
        self.connect()
        try:
            with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()
        except PsycopgDatabaseError as e:
            self.rollback()
            raise ORMDatabaseError(f"Fetchone failed: {e}") from e

    def fetchall(self, sql: str, params=None):
        self.connect()
        try:
            with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except PsycopgDatabaseError as e:
            self.rollback()
            raise ORMDatabaseError(f"Fetchall failed: {e}") from e