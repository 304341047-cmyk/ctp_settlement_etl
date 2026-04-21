import sqlite3
from typing import Iterable

from app.models import Positions


def insert_many(
    conn: sqlite3.Connection,
    records: Iterable[Positions],
) -> int:
    records = list(records)
    if not records:
        return 0

    sql = """
    INSERT INTO positions (
        invest_unit,
        trading_code,
        product,
        instrument,
        long_pos,
        avg_buy_price,
        s_pos,
        avg_sell_price,
        prev_sttl,
        sttl_today,
        mtm_p_l,
        margin_occupied,
        s_h,
        market_value_long,
        market_value_short,
        source_file,
        raw_payload
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = []
    for r in records:
        params.append(
            (
                r.invest_unit,
                r.trading_code,
                r.product,
                r.instrument,
                r.long_pos,
                r.avg_buy_price,
                r.s_pos,
                r.avg_sell_price,
                r.prev_sttl,
                r.sttl_today,
                r.mtm_p_l,
                r.margin_occupied,
                r.s_h,
                r.market_value_long,
                r.market_value_short,
                r.source_file,
                r.raw_payload,
            )
        )

    conn.executemany(sql, params)
    return len(records)