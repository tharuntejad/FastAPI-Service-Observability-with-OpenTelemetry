
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("app/orders.db")
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        product_name TEXT NOT NULL,
        product_id INTEGER NOT NULL,
        order_date TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

initialize_db()
