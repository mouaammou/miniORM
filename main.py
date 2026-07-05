# main.py
from app.db import Database

if __name__ == "__main__":
    db = Database()
    
    print("Testing connection...")
    db.connect()
    print("Connected successfully!")
    
    # 1. Create a dummy table
    db.execute("""
        CREATE TABLE IF NOT EXISTS test_users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        );
    """)
    db.commit()
    
    # 2. Insert a record
    db.execute("INSERT INTO test_users (name) VALUES (%s);", ("Alice",))
    db.commit()
    
    # 3. Fetch the record back
    user = db.fetchone("SELECT * FROM test_users WHERE name = %s;", ("Alice",))
    print(f"Fetched User from Postgres: {user}")
    
    # Clean up and close
    db.execute("DROP TABLE test_users;")
    db.commit()
    db.close()
    print("Connection closed cleanly.")