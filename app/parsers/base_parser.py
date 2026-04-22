from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseParser(ABC):
    name = "BaseParser"

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        raise NotImplementedError

    @abstractmethod
    def parse(self, file_path: Path) -> dict[str, Any]:
        raise NotImplementedError

    def empty_result(self) -> dict[str, Any]:
        return {
            "account_summary": [],
            "deposit_withdrawal": [],
            "transaction_record": [],
            "exercise_statement": [],
            "position_closed": [],
            "positions_detail": [],
            "positions": [],
            "debug_sections": {},
        }