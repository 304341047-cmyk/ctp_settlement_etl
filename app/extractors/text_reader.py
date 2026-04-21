from pathlib import Path

from app.config import DEFAULT_TEXT_ENCODING_CANDIDATES


def read_text_file(file_path: Path) -> str:
    last_error = None

    for encoding in DEFAULT_TEXT_ENCODING_CANDIDATES:
        try:
            text = file_path.read_text(encoding=encoding)
            return normalize_text(text)
        except Exception as e:
            last_error = e

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"无法读取文件 {file_path.name}，尝试编码 {DEFAULT_TEXT_ENCODING_CANDIDATES} 均失败，最后错误: {last_error}",
    )


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\ufeff", "")
    text = text.replace("\x00", "")
    return text