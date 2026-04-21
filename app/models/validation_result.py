from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    source_file: str
    rule_code: str
    rule_name: str
    status: str
    actual_value: Optional[str] = None
    expected_value: Optional[str] = None
    diff_value: Optional[float] = None
    message: Optional[str] = None