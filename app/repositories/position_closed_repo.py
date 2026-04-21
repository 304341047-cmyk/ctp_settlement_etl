import sqlite3
from typing import Iterable

from app.models import PositionClosed


def insert_many(
    conn: sqlite3.Connection,
    records: Iterable[PositionClosed],
) -> int:
    records = list(records)
    if not records:
        return 0

    sql = """
    INSERT INTO position_closed (
        close_date,
        invest_unit,
        exchange,
        trading_code,
        product,
        instrument,
        open_date,
        s_h,
        b_s,
        lots,
        pos_open_price,
        prev_sttl,
        trans_price,
        realized_p_l,
        premium_received_paid,
        premium_netting,
        source_file,
        raw_payload
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = []
    for r in records:
        params.append(
            (
                r.close_date,
                r.invest_unit,
                r.exchange,
                r.trading_code,
                r.product,
                r.instrument,
                r.open_date,
                r.s_h,
                r.b_s,
                r.lots,
                r.pos_open_price,
                r.prev_sttl,
                r.trans_price,
                r.realized_p_l,
                r.premium_received_paid,
                r.premium_netting,
                r.source_file,
                r.raw_payload,
            )
        )

    conn.executemany(sql, params)
    return len(records)