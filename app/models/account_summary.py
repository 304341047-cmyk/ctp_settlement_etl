from dataclasses import dataclass
from typing import Optional


@dataclass
class AccountSummary:
    creation_date: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    account_id: Optional[str] = None
    currency: Optional[str] = None

    balance_b_f: Optional[float] = None
    deposit_withdrawal: Optional[float] = None
    realized_p_l: Optional[float] = None
    mtm_p_l: Optional[float] = None
    exercise_p_l: Optional[float] = None
    commission: Optional[float] = None
    exercise_fee: Optional[float] = None
    delivery_fee: Optional[float] = None
    new_fx_pledge: Optional[float] = None
    fx_redemption: Optional[float] = None
    chg_in_pledge_amt: Optional[float] = None
    premium_received: Optional[float] = None
    premium_paid: Optional[float] = None
    delivery_p_l: Optional[float] = None

    initial_margin: Optional[float] = None
    balance_c_f: Optional[float] = None
    pledge_amount: Optional[float] = None
    client_equity: Optional[float] = None
    fx_pledge_occ: Optional[float] = None
    margin_occupied: Optional[float] = None
    delivery_margin: Optional[float] = None
    market_value_long: Optional[float] = None
    market_value_short: Optional[float] = None
    market_value_equity: Optional[float] = None
    fund_avail: Optional[float] = None
    risk_degree: Optional[float] = None
    margin_call: Optional[float] = None
    chg_in_fx_pledge: Optional[float] = None

    source_file: str = ""
    raw_payload: Optional[str] = None