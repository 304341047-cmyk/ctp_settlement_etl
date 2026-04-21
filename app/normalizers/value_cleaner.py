from decimal import Decimal


def clean_str(value: str | None) -> str | None:
    if value is None:
        return None
    v = value.strip()
    return v if v else None


def clean_float(value: str | None) -> float | None:
    if value is None:
        return None

    v = value.strip().replace(",", "").replace("%", "")

    if not v:
        return None

    try:
        return float(Decimal(v))
    except Exception:
        return None


def clean_int(value: str | None) -> int | None:
    f = clean_float(value)
    if f is None:
        return None
    return int(f)