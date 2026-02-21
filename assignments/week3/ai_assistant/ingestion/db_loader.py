import sqlite3
import os

DB_PATH = "data/upgrade.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool TEXT,
            version TEXT,
            category TEXT,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_changes(changes):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for change in changes:
        c.execute("""
            INSERT INTO changes (tool, version, category, description)
            VALUES (?, ?, ?, ?)
        """, (
            change["tool"],
            change["version"],
            change["category"],
            change["description"]
        ))
    conn.commit()
    conn.close()
