from pathlib import Path


def load_sql(file_name: str) -> str:
    base_path = Path(__file__).resolve().parent.parent / "sql"
    file_path = base_path / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"SQL 文件不存在: {file_path}")

    return file_path.read_text(encoding="utf-8")