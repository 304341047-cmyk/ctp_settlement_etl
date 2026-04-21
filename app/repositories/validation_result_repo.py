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
        source_file,
        rule_code,
        rule_name,
        status,
        actual_value,
        expected_value,
        diff_value,
        message
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = []
    for r in records:
        params.append(
            (
                r.source_file,
                r.rule_code,
                r.rule_name,
                r.status,
                r.actual_value,
                r.expected_value,
                r.diff_value,
                r.message,
            )
        )

    conn.executemany(sql, params)
    return len(records)