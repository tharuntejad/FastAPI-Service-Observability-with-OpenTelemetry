
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("app/inventory.db")
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        count INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()

initialize_db()
