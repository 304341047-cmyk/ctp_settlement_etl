import sqlite3


def exists_by_md5(conn: sqlite3.Connection, file_md5: str) -> bool:
    sql = """
    SELECT 1
    FROM source_file_record
    WHERE file_md5 = ?
    LIMIT 1
    """
    row = conn.execute(sql, (file_md5,)).fetchone()
    return row is not None


def insert_source_file_record(
    conn: sqlite3.Connection,
    source_file: str,
    file_md5: str,
    parser_name: str,
    process_status: str = "SUCCESS",
    error_message: str | None = None,
) -> None:
    sql = """
    INSERT INTO source_file_record (
        source_file,
        file_md5,
        parser_name,
        process_status,
        error_message
    ) VALUES (?, ?, ?, ?, ?)
    """
    conn.execute(
        sql,
        (source_file, file_md5, parser_name, process_status, error_message),
    )