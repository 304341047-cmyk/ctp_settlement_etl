import sqlite3
from typing import Iterable

from app.models import AccountSummary


def insert_many(
    conn: sqlite3.Connection,
    records: Iterable[AccountSummary],
) -> int:
    records = list(records)
    if not records:
        return 0

    sql = """
    INSERT INTO account_summary (
        creation_date,
        date_from,
        date_to,
        client_id,
        client_name,
        account_id,
        currency,
        balance_b_f,
        deposit_withdrawal,
        realized_p_l,
        mtm_p_l,
        exercise_p_l,
        commission,
        exercise_fee,
        delivery_fee,
        new_fx_pledge,
        fx_redemption,
        chg_in_pledge_amt,
        premium_received,
        premium_paid,
        delivery_p_l,
        initial_margin,
        balance_c_f,
        pledge_amount,
        client_equity,
        fx_pledge_occ,
        margin_occupied,
        delivery_margin,
        market_value_long,
        market_value_short,
        market_value_equity,
        fund_avail,
        risk_degree,
        margin_call,
        chg_in_fx_pledge,
        source_file,
        raw_payload
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?
    )
    """

    params = [
        (
            r.creation_date,
            r.date_from,
            r.date_to,
            r.client_id,
            r.client_name,
            r.account_id,
            r.currency,
            r.balance_b_f,
            r.deposit_withdrawal,
            r.realized_p_l,
            r.mtm_p_l,
            r.exercise_p_l,
            r.commission,
            r.exercise_fee,
            r.delivery_fee,
            r.new_fx_pledge,
            r.fx_redemption,
            r.chg_in_pledge_amt,
            r.premium_received,
            r.premium_paid,
            r.delivery_p_l,
            r.initial_margin,
            r.balance_c_f,
            r.pledge_amount,
            r.client_equity,
            r.fx_pledge_occ,
            r.margin_occupied,
            r.delivery_margin,
            r.market_value_long,
            r.market_value_short,
            r.market_value_equity,
            r.fund_avail,
            r.risk_degree,
            r.margin_call,
            r.chg_in_fx_pledge,
            r.source_file,
            r.raw_payload,
        )
        for r in records
    ]

    conn.executemany(sql, params)
    return len(records)