from app.extractors.table_parser import parse_pipe_row


def normalize_header(header_line: str) -> list[str]:
    """
    把英文表头转成 snake_case 字段名
    """
    cols = parse_pipe_row(header_line)

    return [normalize_column_name(c) for c in cols]


def normalize_column_name(col: str) -> str:
    c = col.strip()

    c = c.replace(".", "")
    c = c.replace("/", "_")
    c = c.replace(" ", "_")
    c = c.replace("-", "_")
    c = c.replace("(", "")
    c = c.replace(")", "")

    return c.lower()