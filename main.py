from app.db import Database
from app.exceptions import ORMDatabaseError

def test_database_roundtrip():
    db = Database()

    try:
        print("Connecting...")
        db.connect()

        print("Resetting table...")
        db.execute("DROP TABLE IF EXISTS test_people")
        db.execute("""
            CREATE TABLE test_people (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            )
        """)

        print("Inserting row...")
        row = db.execute(
            "INSERT INTO test_people (name) VALUES (%s) RETURNING id, name",
            ("Mouad",),
            fetch_one=True
        )
        print("Inserted:", row)

        print("Reading rows...")
        rows = db.fetchall("SELECT id, name FROM test_people ORDER BY id")
        print("Rows:", rows)

        db.commit()

    except ORMDatabaseError as exc:
        print("DB error:", exc)
        db.rollback()

    finally:
        db.close()

if __name__ == "__main__":
    test_database_roundtrip()