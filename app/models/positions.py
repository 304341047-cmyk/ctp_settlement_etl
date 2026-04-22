from dataclasses import dataclass
from typing import Optional


@dataclass
class Positions:
    invest_unit: Optional[str] = None
    trading_code: Optional[str] = None
    product: Optional[str] = None
    instrument: Optional[str] = None
    long_pos: Optional[float] = None
    avg_buy_price: Optional[float] = None
    short_pos: Optional[float] = None
    avg_sell_price: Optional[float] = None
    prev_sttl: Optional[float] = None
    sttl_today: Optional[float] = None
    mtm_p_l: Optional[float] = None
    margin_occupied: Optional[float] = None
    s_h: Optional[str] = None
    market_value_long: Optional[float] = None
    market_value_short: Optional[float] = None
    account_id: Optional[str] = None

    source_file: str = ""
    raw_payload: Optional[str] = None