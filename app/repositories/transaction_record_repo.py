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
        premium_r_p,
        trans_no,
        source_file,
        raw_payload
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = []
    for r in records:
        params.append(
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
                r.premium_r_p,
                r.trans_no,
                r.source_file,
                r.raw_payload,
            )
        )

    conn.executemany(sql, params)
    return len(records)