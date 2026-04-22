from dataclasses import dataclass
from typing import Optional


@dataclass
class DepositWithdrawal:
    date: Optional[str] = None
    type: Optional[str] = None
    deposit: Optional[float] = None
    withdrawal: Optional[float] = None
    exchange_rate: Optional[float] = None
    account_id: Optional[str] = None
    note: Optional[str] = None

    source_file: str = ""
    raw_payload: Optional[str] = None