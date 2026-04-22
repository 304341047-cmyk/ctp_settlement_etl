import sqlite3
from typing import Iterable

from app.models import PositionsDetail


def insert_many(
    conn: sqlite3.Connection,
    records: Iterable[PositionsDetail],
) -> int:
    records = list(records)
    if not records:
        return 0

    sql = """
    INSERT INTO positions_detail (
        invest_unit,
        exchange,
        trading_code,
        product,
        instrument,
        open_date,
        s_h,
        b_s,
        position_qty,
        pos_open_price,
        prev_sttl,
        settlement_price,
        accum_p_l,
        mtm_p_l,
        margin,
        market_value,
        account_id,
        source_file,
        raw_payload
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = [
        (
            r.invest_unit,
            r.exchange,
            r.trading_code,
            r.product,
            r.instrument,
            r.open_date,
            r.s_h,
            r.b_s,
            r.position_qty,
            r.pos_open_price,
            r.prev_sttl,
            r.settlement_price,
            r.accum_p_l,
            r.mtm_p_l,
            r.margin,
            r.market_value,
            r.account_id,
            r.source_file,
            r.raw_payload,
        )
        for r in records
    ]

    conn.executemany(sql, params)
    return len(records)