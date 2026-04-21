from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceFileRecord:
    source_file: str
    file_md5: str
    parser_name: Optional[str] = None
    process_status: str = "SUCCESS"
    error_message: Optional[str] = None