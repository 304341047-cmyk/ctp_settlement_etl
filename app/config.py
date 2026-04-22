from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
INPUT_DIR = BASE_DIR / "input"

# 新增统一父目录
PROCESSED_DATA_DIR = BASE_DIR / "processed_data"

ARCHIVE_DIR = PROCESSED_DATA_DIR / "archive"
ERROR_DIR = PROCESSED_DATA_DIR / "error"
OUTPUT_DIR = PROCESSED_DATA_DIR / "output"

LOG_DIR = BASE_DIR / "logs"
SQL_DIR = BASE_DIR / "app" / "sql"

DB_PATH = DATA_DIR / "settlement.db"

DEFAULT_TEXT_ENCODING_CANDIDATES = [
    "utf-8",
    "utf-8-sig",
    "gbk",
    "gb18030",
]

LOG_FILE = LOG_DIR / "app.log"


def ensure_directories() -> None:
    for path in [
        DATA_DIR,
        INPUT_DIR,
        PROCESSED_DATA_DIR,
        ARCHIVE_DIR,
        ERROR_DIR,
        OUTPUT_DIR,
        LOG_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)