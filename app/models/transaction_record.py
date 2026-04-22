from dataclasses import dataclass
from typing import Optional


@dataclass
class TransactionRecord:
    date: Optional[str] = None
    invest_unit: Optional[str] = None
    exchange: Optional[str] = None
    trading_code: Optional[str] = None
    product: Optional[str] = None
    instrument: Optional[str] = None
    b_s: Optional[str] = None
    s_h: Optional[str] = None
    price: Optional[float] = None
    lots: Optional[float] = None
    turnover: Optional[float] = None
    o_c: Optional[str] = None
    fee: Optional[float] = None
    realized_p_l: Optional[float] = None
    premium_received_paid: Optional[float] = None
    trans_no: Optional[str] = None
    account_id: Optional[str] = None

    source_file: str = ""
    raw_payload: Optional[str] = None