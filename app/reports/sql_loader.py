from pathlib import Path

from app.config import SQL_DIR


def load_sql(filename: str) -> str:
    path = SQL_DIR / filename
    return path.read_text(encoding="utf-8")