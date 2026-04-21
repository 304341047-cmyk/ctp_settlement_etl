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
    positon: Optional[float] = None
    open_price: Optional[float] = None
    prev_sttl: Optional[float] = None
    sttl_today: Optional[float] = None
    accum_p_l: Optional[float] = None
    mtm_p_l: Optional[float] = None
    margin: Optional[float] = None
    market_val: Optional[float] = None
    market_val_chg: Optional[float] = None

    source_file: str = ""
    raw_payload: Optional[str] = None