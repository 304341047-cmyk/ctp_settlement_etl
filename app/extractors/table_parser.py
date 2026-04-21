from dataclasses import dataclass, field


@dataclass
class ParsedTable:
    raw_lines: list[str] = field(default_factory=list)
    header_lines: list[str] = field(default_factory=list)
    english_header_lines: list[str] = field(default_factory=list)
    data_lines: list[str] = field(default_factory=list)
    summary_lines: list[str] = field(default_factory=list)


def extract_table_lines(section_text: str) -> ParsedTable:
    result = ParsedTable()

    for raw_line in section_text.splitlines():
        line = raw_line.rstrip()

        if not line.strip():
            continue

        if not line.strip().startswith("|"):
            continue

        if is_separator_line(line):
            continue

        result.raw_lines.append(line)

        if is_summary_line(line):
            result.summary_lines.append(line)
            continue

        if is_english_header_line(line):
            result.english_header_lines.append(line)
            continue

        if is_header_line(line):
            result.header_lines.append(line)
            continue

        if is_data_line(line):
            result.data_lines.append(line)

    return result


def parse_pipe_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def parse_data_rows(lines: list[str]) -> list[list[str]]:
    return [parse_pipe_row(line) for line in lines]


def is_separator_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return True

    chars = set(s)
    return chars.issubset(set("-|= \t"))


def is_summary_line(line: str) -> bool:
    s = line.replace(" ", "")
    return s.startswith("|共") or "共" in s and "条" in s


def is_english_header_line(line: str) -> bool:
    keywords = [
        "Date",
        "Exchange",
        "Instrument",
        "Product",
        "TradingCode",
        "Trans.No.",
        "Amount Exercised",
        "Market Value",
        "Avg Buy Price",
        "Avg Sell Price",
    ]
    return any(keyword in line for keyword in keywords)


def is_header_line(line: str) -> bool:
    header_keywords = [
        "成交日期",
        "投资单元",
        "交易所",
        "交易编码",
        "品种",
        "合约",
        "买/卖",
        "投/保",
        "成交价",
        "手数",
        "成交额",
        "开平",
        "手续费",
        "平仓盈亏",
        "权利金收支",
        "交易日",
        "是否行权",
        "行权数量",
        "行权价格",
        "行权金额",
        "平仓日期",
        "开仓日期",
        "持仓量",
        "开仓价",
        "昨结算",
        "结算价",
        "浮动盈亏",
        "盯市盈亏",
        "保证金",
        "期权市值",
        "持仓汇总",
        "买持",
        "卖持",
        "买开仓均价",
        "卖开仓均价",
    ]
    return any(keyword in line for keyword in header_keywords)


def is_data_line(line: str) -> bool:
    cells = parse_pipe_row(line)
    if not cells:
        return False

    first_cell = cells[0].strip()
    if not first_cell:
        return False

    # 常见数据行特征：
    # 1. 第一列是日期 20260413
    # 2. 第一列是账号/投资单元 81183126
    # 3. 第一列是纯数字但不是“共xx条”
    if first_cell.isdigit() and len(first_cell) in (8, 6, 5):
        return True

    # 持仓汇总/持仓明细有时第一列就是投资单元
    if first_cell.isdigit():
        return True

    return False