import sqlite3
from typing import Iterable

from app.models import ExerciseStatement


def insert_many(
    conn: sqlite3.Connection,
    records: Iterable[ExerciseStatement],
) -> int:
    records = list(records)
    if not records:
        return 0

    sql = """
    INSERT INTO exercise_statement (
        date,
        invest_unit,
        exchange,
        trading_code,
        product,
        instrument,
        b_s,
        strike_price,
        exercise_price,
        lots,
        turnover,
        exercise_p_l,
        exercise_fee,
        account_id,
        source_file,
        raw_payload
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            r.strike_price,
            r.exercise_price,
            r.lots,
            r.turnover,
            r.exercise_p_l,
            r.exercise_fee,
            r.account_id,
            r.source_file,
            r.raw_payload,
        )
        for r in records
    ]

    conn.executemany(sql, params)
    return len(records)