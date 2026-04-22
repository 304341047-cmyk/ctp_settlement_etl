from app.extractors.table_parser import parse_pipe_row


# 统一后的内部字段别名映射
# 规则：
# 1. 先把表头做标准化（小写、去点号、括号转下划线等）
# 2. 再映射到系统内部统一字段名
HEADER_ALIAS = {
    # -------------------------
    # 通用
    # -------------------------
    "date": "date",
    "accountid": "account_id",
    "clientid": "client_id",
    "clientname": "client_name",
    "currency": "currency",
    "exchange": "exchange",
    "product": "product",
    "instrument": "instrument",
    "investunit": "invest_unit",
    "tradingcode": "trading_code",
    "transno": "trans_no",
    "trans_no": "trans_no",
    "b_s": "b_s",
    "s_h": "s_h",
    "fee": "fee",
    "lots": "lots",
    "turnover": "turnover",
    "price": "price",

    # -------------------------
    # account_summary 资金状况
    # -------------------------
    "balance_b_f": "balance_b_f",
    "balance_c_f": "balance_c_f",
    "deposit_withdrawal": "deposit_withdrawal",
    "initial_margin": "initial_margin",
    "realized_p_l": "realized_p_l",
    "mtm_p_l": "mtm_p_l",
    "exercise_p_l": "exercise_p_l",
    "commission": "commission",
    "exercise_fee": "exercise_fee",
    "delivery_fee": "delivery_fee",
    "new_fx_pledge": "new_fx_pledge",
    "fx_redemption": "fx_redemption",
    "chg_in_pledge_amt": "chg_in_pledge_amt",
    "premium_received": "premium_received",
    "premium_paid": "premium_paid",
    "delivery_p_l": "delivery_p_l",
    "pledge_amount": "pledge_amount",
    "client_equity": "client_equity",
    "fx_pledge_occ": "fx_pledge_occ",
    "margin_occupied": "margin_occupied",
    "delivery_margin": "delivery_margin",
    "market_value_long": "market_value_long",
    "market_value_short": "market_value_short",
    "market_value_equity": "market_value_equity",
    "fund_avail": "fund_avail",
    "risk_degree": "risk_degree",
    "margin_call": "margin_call",
    "chg_in_fx_pledge": "chg_in_fx_pledge",

    # -------------------------
    # deposit_withdrawal 出入金明细
    # -------------------------
    "type": "type",
    "deposit": "deposit",
    "withdrawal": "withdrawal",
    "exchangerate": "exchange_rate",
    "exchange_rate": "exchange_rate",
    "note": "note",

    # -------------------------
    # transaction_record 成交记录
    # -------------------------
    "o_c": "o_c",
    "realized_p_l": "realized_p_l",
    "premium_received_paid": "premium_received_paid",
    "premium_receivedpaid": "premium_received_paid",

    # 兼容旧写法
    "premium_r_p": "premium_received_paid",

    # -------------------------
    # exercise_statement 行权明细
    # -------------------------
    "strike_price": "strike_price",
    "exercise_price": "exercise_price",

    # -------------------------
    # position_closed 平仓明细
    # -------------------------
    "close_date": "close_date",
    "open_date": "open_date",
    "pos_open_price": "pos_open_price",
    "position_open_price": "pos_open_price",
    "trans_price": "trans_price",
    "transaction_price": "trans_price",

    # 平仓权利金收支
    "premium_received_paid": "premium_received_paid",
    "premium_receivedpaid": "premium_received_paid",

    # -------------------------
    # positions_detail 持仓明细
    # -------------------------
    # 新账单英文拼的是 Positon，这里统一成 position_qty
    "positon": "position_qty",
    "position": "position_qty",
    "position_qty": "position_qty",

    "pos_open_price": "pos_open_price",
    "open_price": "pos_open_price",

    "prev_sttl": "prev_sttl",
    "settlement_price": "settlement_price",
    "sttl_today": "settlement_price",

    "accum_p_l": "accum_p_l",
    "margin": "margin",

    "market_value_options": "market_value",
    "market_valueoption": "market_value",
    "market_val": "market_value",
    "market_value": "market_value",

    # 某些旧表可能会有这个字段，但新结构不需要强依赖
    "market_val_chg": "market_val_chg",
    "market_value_change": "market_val_chg",

    # -------------------------
    # positions 持仓汇总
    # -------------------------
    "long_pos": "long_pos",
    "avg_buy_price": "avg_buy_price",
    "short_pos": "short_pos",
    "avg_sell_price": "avg_sell_price",
    "sttl_today": "sttl_today",
    "margin_occupied": "margin_occupied",
    "market_value_long": "market_value_long",
    "market_value_short": "market_value_short",

    # 兼容旧字段名
    "b_pos": "long_pos",
    "s_pos": "short_pos",
    "market_valuelong": "market_value_long",
    "market_valueshort": "market_value_short",
}


def normalize_header(header_line: str) -> list[str]:
    """
    将英文表头行解析并映射为内部统一字段名。
    """
    cols = parse_pipe_row(header_line)
    return [normalize_column_name(col) for col in cols]


def normalize_column_name(col: str) -> str:
    """
    表头标准化规则：
    - 去首尾空格
    - 小写
    - 去点号
    - 斜杠转下划线
    - 空格转下划线
    - 连字符转下划线
    - 括号内容保留下来，但括号本身去掉
    - 连续下划线压缩
    - 再走 HEADER_ALIAS 做统一映射
    """
    c = col.strip().lower()

    # 常见符号标准化
    c = c.replace("（", "(").replace("）", ")")
    c = c.replace(".", "")
    c = c.replace("/", "_")
    c = c.replace("-", "_")
    c = c.replace(" ", "_")

    # 去括号，但保留内容
    c = c.replace("(", "_").replace(")", "")

    # 压缩多余下划线
    while "__" in c:
        c = c.replace("__", "_")

    c = c.strip("_")

    return HEADER_ALIAS.get(c, c)


# 各区块建议的“关键字段”。
# 用于 parser 层做缺字段提示，不在这里直接报错。
REQUIRED_HEADERS = {
    "deposit_withdrawal": {
        "date",
        "type",
        "deposit",
        "withdrawal",
        "account_id",
    },
    "transaction_record": {
        "date",
        "instrument",
        "b_s",
        "price",
        "lots",
    },
    "exercise_statement": {
        "date",
        "instrument",
        "b_s",
        "lots",
    },
    "position_closed": {
        "close_date",
        "instrument",
        "b_s",
        "lots",
    },
    "positions_detail": {
        "instrument",
        "b_s",
        "position_qty",
    },
    "positions": {
        "instrument",
        "long_pos",
        "short_pos",
    },
}


def check_required_headers(section_name: str, headers: list[str]) -> list[str]:
    """
    返回缺失字段告警，不中断解析。
    由 parser 决定如何记录/展示 warning。
    """
    required = REQUIRED_HEADERS.get(section_name, set())
    actual = set(headers)

    missing = sorted(required - actual)
    if not missing:
        return []

    return [f"{section_name} 缺少字段: {', '.join(missing)}"]