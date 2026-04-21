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
        positon,
        open_price,
        prev_sttl,
        sttl_today,
        accum_p_l,
        mtm_p_l,
        margin,
        market_val,
        market_val_chg,
        source_file,
        raw_payload
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = []
    for r in records:
        params.append(
            (
                r.invest_unit,
                r.exchange,
                r.trading_code,
                r.product,
                r.instrument,
                r.open_date,
                r.s_h,
                r.b_s,
                r.positon,
                r.open_price,
                r.prev_sttl,
                r.sttl_today,
                r.accum_p_l,
                r.mtm_p_l,
                r.margin,
                r.market_val,
                r.market_val_chg,
                r.source_file,
                r.raw_payload,
            )
        )

    conn.executemany(sql, params)
    return len(records)