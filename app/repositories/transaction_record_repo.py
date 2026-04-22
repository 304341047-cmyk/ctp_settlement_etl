import sqlite3
from typing import Iterable

from app.models import TransactionRecord


def insert_many(
    conn: sqlite3.Connection,
    records: Iterable[TransactionRecord],
) -> int:
    records = list(records)
    if not records:
        return 0

    sql = """
    INSERT INTO transaction_record (
        date,
        invest_unit,
        exchange,
        trading_code,
        product,
        instrument,
        b_s,
        s_h,
        price,
        lots,
        turnover,
        o_c,
        fee,
        realized_p_l,
        premium_received_paid,
        trans_no,
        account_id,
        source_file,
        raw_payload
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = [
        (
            r.date,
            r.invest_unit,
            r.exchange,
            r.trading_code,
            r.product,
            r.instrument,
            r.b_s,
            r.s_h,
            r.price,
            r.lots,
            r.turnover,
            r.o_c,
            r.fee,
            r.realized_p_l,
            r.premium_received_paid,
            r.trans_no,
            r.account_id,
            r.source_file,
            r.raw_payload,
        )
        for r in records
    ]

    conn.executemany(sql, params)
    return len(records)