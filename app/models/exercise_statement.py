from dataclasses import dataclass
from typing import Optional


@dataclass
class ExerciseStatement:
    date: Optional[str] = None
    invest_unit: Optional[str] = None
    exchange: Optional[str] = None
    trading_code: Optional[str] = None
    product: Optional[str] = None
    instrument: Optional[str] = None
    b_s: Optional[str] = None
    strike_price: Optional[float] = None
    exercise_price: Optional[float] = None
    lots: Optional[float] = None
    turnover: Optional[float] = None
    exercise_p_l: Optional[float] = None
    exercise_fee: Optional[float] = None
    account_id: Optional[str] = None

    source_file: str = ""
    raw_payload: Optional[str] = None