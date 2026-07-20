import sqlite3
import os
from fastapi import HTTPException

def get_db_connection():
    db_paths = [
        # Look relative to backend/database/db.py
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "PythonProject1", "guidelines.db")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "guidelines.db")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "guidelines.db")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "guidelines.db")),
        "guidelines.db",
        "PythonProject1/guidelines.db"
    ]
    for p in db_paths:
        if os.path.exists(p):
            conn = sqlite3.connect(p)
            conn.row_factory = sqlite3.Row
            return conn
    raise HTTPException(status_code=500, detail="guidelines.db SQLite database not found on backend server.")
