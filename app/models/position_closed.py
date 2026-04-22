from dataclasses import dataclass
from typing import Optional


@dataclass
class PositionClosed:
    close_date: Optional[str] = None
    invest_unit: Optional[str] = None
    exchange: Optional[str] = None
    trading_code: Optional[str] = None
    product: Optional[str] = None
    instrument: Optional[str] = None
    open_date: Optional[str] = None
    s_h: Optional[str] = None
    b_s: Optional[str] = None
    lots: Optional[float] = None
    pos_open_price: Optional[float] = None
    prev_sttl: Optional[float] = None
    trans_price: Optional[float] = None
    realized_p_l: Optional[float] = None
    premium_received_paid: Optional[float] = None
    account_id: Optional[str] = None

    source_file: str = ""
    raw_payload: Optional[str] = None