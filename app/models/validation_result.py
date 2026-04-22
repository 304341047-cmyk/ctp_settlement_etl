from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    check_name: str = ""
    status: str = ""
    actual_value: Optional[float] = None
    expected_value: Optional[float] = None
    diff_value: Optional[float] = None
    tolerance: Optional[float] = None
    details: Optional[str] = None

    source_file: str = ""
    created_at: Optional[str] = None