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
        balance_c_f,
        deposit_withdrawal,
        initial_margin,
        realized_p_l,
        mtm_p_l,
        market_value_equity,
        client_equity,
        exercise_p_l,
        fx_pledge_occ,
        commission,
        exercise_fee,
        margin_occupied,
        delivery_margin,
        market_value_short,
        market_value_long,
        new_fx_pledge,
        fx_redemption,
        delivery_fee,
        pledge_amount,
        chg_in_pledge_amt,
        fund_avail,
        premium_received,
        premium_paid,
        risk_degree,
        margin_call,
        delivery_p_l,
        chg_in_fx_pledge,
        source_file,
        raw_payload
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = []
    for r in records:
        params.append(
            (
                r.creation_date,
                r.date_from,
                r.date_to,
                r.client_id,
                r.client_name,
                r.account_id,
                r.currency,
                r.balance_b_f,
                r.balance_c_f,
                r.deposit_withdrawal,
                r.initial_margin,
                r.realized_p_l,
                r.mtm_p_l,
                r.market_value_equity,
                r.client_equity,
                r.exercise_p_l,
                r.fx_pledge_occ,
                r.commission,
                r.exercise_fee,
                r.margin_occupied,
                r.delivery_margin,
                r.market_value_short,
                r.market_value_long,
                r.new_fx_pledge,
                r.fx_redemption,
                r.delivery_fee,
                r.pledge_amount,
                r.chg_in_pledge_amt,
                r.fund_avail,
                r.premium_received,
                r.premium_paid,
                r.risk_degree,
                r.margin_call,
                r.delivery_p_l,
                r.chg_in_fx_pledge,
                r.source_file,
                r.raw_payload,
            )
        )

    conn.executemany(sql, params)
    return len(records)