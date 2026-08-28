import sqlite3
from pathlib import Path

DB_PATH = Path("data/netflix.db")


def get_connection() -> sqlite3.Connection:
    """Create a connection to the Netflix SQLite database."""
    return sqlite3.connect(DB_PATH)