import sqlite3
from typing import Iterable

from app.models import DepositWithdrawal


def insert_many(
    conn: sqlite3.Connection,
    records: Iterable[DepositWithdrawal],
) -> int:
    records = list(records)
    if not records:
        return 0

    sql = """
    INSERT INTO deposit_withdrawal (
        date,
        type,
        deposit,
        withdrawal,
        exchange_rate,
        account_id,
        note,
        source_file,
        raw_payload
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = [
        (
            r.date,
            r.type,
            r.deposit,
            r.withdrawal,
            r.exchange_rate,
            r.account_id,
            r.note,
            r.source_file,
            r.raw_payload,
        )
        for r in records
    ]

    conn.executemany(sql, params)
    return len(records)