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
    s_h: Optional[str] = None
    b_s: Optional[str] = None
    exercise_abandon: Optional[str] = None
    volume_exercised: Optional[float] = None
    ex_price: Optional[float] = None
    amount_exercised: Optional[float] = None
    exercise_p_l: Optional[float] = None
    exercise_fee: Optional[float] = None

    source_file: str = ""
    raw_payload: Optional[str] = None