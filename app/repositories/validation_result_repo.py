import sqlite3
from typing import Iterable

from app.models import ValidationResult


def insert_many(
    conn: sqlite3.Connection,
    records: Iterable[ValidationResult],
) -> int:
    records = list(records)
    if not records:
        return 0

    sql = """
    INSERT INTO validation_result (
        check_name,
        status,
        actual_value,
        expected_value,
        diff_value,
        tolerance,
        details,
        source_file,
        created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = [
        (
            r.check_name,
            r.status,
            r.actual_value,
            r.expected_value,
            r.diff_value,
            r.tolerance,
            r.details,
            r.source_file,
            r.created_at,
        )
        for r in records
    ]

    conn.executemany(sql, params)
    return len(records)