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
        s_h,
        b_s,
        exercise_abandon,
        volume_exercised,
        ex_price,
        amount_exercised,
        exercise_p_l,
        exercise_fee,
        source_file,
        raw_payload
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                r.s_h,
                r.b_s,
                r.exercise_abandon,
                r.volume_exercised,
                r.ex_price,
                r.amount_exercised,
                r.exercise_p_l,
                r.exercise_fee,
                r.source_file,
                r.raw_payload,
            )
        )

    conn.executemany(sql, params)
    return len(records)