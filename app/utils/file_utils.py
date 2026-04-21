import shutil
from pathlib import Path

from app.config import ARCHIVE_DIR, ERROR_DIR, INPUT_DIR


def list_txt_files():
    return sorted(INPUT_DIR.glob("*.txt"))


def move_to_archive(file_path: Path) -> Path:
    target = ARCHIVE_DIR / file_path.name
    if file_path.exists():
        shutil.move(str(file_path), str(target))
    return target


def move_to_error(file_path: Path) -> Path:
    target = ERROR_DIR / file_path.name
    if file_path.exists():
        shutil.move(str(file_path), str(target))
    return target