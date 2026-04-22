from __future__ import annotations

from typing import Any


def clean_str(value: Any) -> str | None:
    if value is None:
        return None

    s = str(value).strip()
    if not s:
        return None

    return s


def clean_float(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip()
    if not s:
        return None

    s = s.replace(",", "")
    s = s.replace("％", "%")

    if s in {"-", "--", "—", "N/A", "None", "null"}:
        return None

    if s.endswith("%"):
        try:
            return float(s[:-1])
        except ValueError:
            return None

    try:
        return float(s)
    except ValueError:
        return None


def clean_int(value: Any) -> int | None:
    f = clean_float(value)
    if f is None:
        return None
    return int(f)