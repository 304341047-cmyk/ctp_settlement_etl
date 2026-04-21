import hashlib
from pathlib import Path


def file_md5(file_path: Path, chunk_size: int = 8192) -> str:
    md5 = hashlib.md5()
    with file_path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            md5.update(chunk)
    return md5.hexdigest()