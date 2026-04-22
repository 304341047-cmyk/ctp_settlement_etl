from dataclasses import dataclass
from typing import Optional


@dataclass
class PositionsDetail:
    invest_unit: Optional[str] = None
    exchange: Optional[str] = None
    trading_code: Optional[str] = None
    product: Optional[str] = None
    instrument: Optional[str] = None
    open_date: Optional[str] = None
    s_h: Optional[str] = None
    b_s: Optional[str] = None
    position_qty: Optional[float] = None
    pos_open_price: Optional[float] = None
    prev_sttl: Optional[float] = None
    settlement_price: Optional[float] = None
    accum_p_l: Optional[float] = None
    mtm_p_l: Optional[float] = None
    margin: Optional[float] = None
    market_value: Optional[float] = None
    account_id: Optional[str] = None

    source_file: str = ""
    raw_payload: Optional[str] = None