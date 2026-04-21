import sqlite3
from pathlib import Path

from app.config import DB_PATH, SQL_DIR, ensure_directories


def get_connection() -> sqlite3.Connection:
    ensure_directories()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    ensure_directories()
    sql_file = SQL_DIR / "init_tables.sql"
    if not sql_file.exists():
        raise FileNotFoundError(f"建表文件不存在: {sql_file}")

    sql_text = sql_file.read_text(encoding="utf-8")

    with get_connection() as conn:
        conn.executescript(sql_text)
        conn.commit()