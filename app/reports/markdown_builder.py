def _num(value, digits=2):
    if value is None:
        return "-"
    try:
        return f"{float(value):,.{digits}f}"
    except Exception:
        return str(value)


def _signed_num(value, digits=2):
    if value is None:
        return "-"
    try:
        v = float(value)
        sign = "+" if v > 0 else ""
        return f"{sign}{v:,.{digits}f}"
    except Exception:
        return str(value)


def _color_value(value, digits=2, is_percent=False):
    if value is None:
        return "-"

    try:
        v = float(value)
    except Exception:
        return str(value)

    if is_percent:
        if v >= 90:
            color = "red"
        elif v >= 70:
            color = "orange"
        else:
            color = "black"
        return f'<span style="color:{color}">{v:.2f}%</span>'

    if v > 0:
        color = "red"
    elif v < 0:
        color = "green"
    else:
        color = "black"

    sign = "+" if v > 0 else ""
    return f'<span style="color:{color}">{sign}{v:,.{digits}f}</span>'


def _diff_color(value, digits=2):
    return _color_value(value, digits=digits, is_percent=False)


def _status_badge(pass_count, total_count, fail_count):
    if total_count == 0:
        return '<span style="color:gray">无核验数据</span>'
    if fail_count and fail_count > 0:
        return f'<span style="color:red">未通过（{pass_count}/{total_count}）</span>'
    return f'<span style="color:green">全部通过（{pass_count}/{total_count}）</span>'


def build_markdown_report(rows: list[dict]) -> str:
    if not rows:
        return "# 交易日报\n\n无数据"

    lines = ["# 交易日报", ""]

    for row in rows:
        date = row.get("date_from", "")
        account_id = row.get("account_id", "")
        client_name = row.get("client_name", "")
        source_file = row.get("source_file", "")

        lines.append(f"## 账户：{account_id}（{client_name}）")
        lines.append(f"- 日期：{date}")
        lines.append(f"- 文件：`{source_file}`")
        lines.append("")

        # 总览
        lines.append("### 总览")
        lines.append("")
        lines.append(f"- 客户权益：**{_num(row.get('client_equity'))}**")
        lines.append(f"- 市值权益：**{_num(row.get('market_value_equity'))}**")
        lines.append(f"- 当日期权市值：**{_num(row.get('option_market_value'))}**")
        lines.append(f"- 当日期货盈亏：**{_color_value(row.get('futures_pnl'))}**")
        lines.append(f"- 当日期权盈亏：**{_color_value(row.get('option_pnl'))}**")
        lines.append(f"- 当日总盈亏：**{_color_value(row.get('total_pnl'))}**")
        lines.append(f"- 风险度：**{_color_value(row.get('risk_degree'), is_percent=True)}**")
        lines.append("")

        # 资金归因
        lines.append("### 资金归因")
        lines.append("")
        lines.append(f"- 上日权益（结存）：{_num(row.get('balance_b_f'))}")
        lines.append(f"- 出入金：{_color_value(row.get('deposit_withdrawal'))}")
        lines.append(f"- 手续费合计：{_color_value(-float(row.get('total_fee') or 0))}")
        lines.append(f"- 权利金变动（收入-支出）：{_color_value(row.get('premium_change'))}")
        lines.append(f"- 期货盈亏（Realized + MTM）：{_color_value(row.get('futures_pnl'))}")
        lines.append(f"- 计算客户权益：{_num(row.get('customer_equity_calc_value'))}")
        lines.append(f"- 实际客户权益：{_num(row.get('client_equity'))}")
        lines.append(f"- 客户权益勾稽差额：{_diff_color(row.get('customer_equity_check_diff'))}")
        lines.append("")

        # 期权归因
        lines.append("### 期权归因")
        lines.append("")
        lines.append(f"- 上日期权市值：{_num(row.get('prev_option_market_value'))}")
        lines.append(f"- 当日期权市值：{_num(row.get('option_market_value'))}")
        lines.append(f"- 期权市值变动：{_color_value(row.get('option_market_value_change'))}")
        lines.append(f"- 权利金变动：{_color_value(row.get('premium_change'))}")
        lines.append(f"- 期权盈亏：{_color_value(row.get('option_pnl'))}")
        lines.append("")

        # 市值权益勾稽
        lines.append("### 市值权益勾稽")
        lines.append("")
        lines.append(f"- 客户权益：{_num(row.get('client_equity'))}")
        lines.append(f"- 期权市值变动：{_color_value(row.get('option_market_value_change'))}")
        lines.append(f"- 计算市值权益：{_num(row.get('market_value_equity_calc_value'))}")
        lines.append(f"- 实际市值权益：{_num(row.get('market_value_equity'))}")
        lines.append(f"- 市值权益勾稽差额：{_diff_color(row.get('market_value_equity_check_diff'))}")
        lines.append("")

        # 交易概览
        lines.append("### 交易概览")
        lines.append("")
        lines.append(f"- 成交笔数：{row.get('transaction_count', 0)}")
        lines.append(f"- 成交手数：{_num(row.get('transaction_lots_sum'))}")
        lines.append(f"- 成交额：{_num(row.get('transaction_turnover_sum'))}")
        lines.append("")

        # 行权概览
        lines.append("### 行权概览")
        lines.append("")
        lines.append(f"- 行权笔数：{row.get('exercise_statement_count', 0)}")
        lines.append(f"- 行权数量：{_num(row.get('exercise_volume_sum'))}")
        lines.append(f"- 行权盈亏：{_color_value(row.get('exercise_p_l_sum'))}")
        lines.append(f"- 行权手续费：{_num(row.get('exercise_fee'))}")
        lines.append("")

        # 持仓概览
        lines.append("### 持仓概览")
        lines.append("")
        lines.append(f"- 持仓条目数：{row.get('positions_count', 0)}")
        lines.append(f"- 多头持仓合计：{_num(row.get('positions_long_pos_sum'))}")
        lines.append(f"- 空头持仓合计：{_num(row.get('positions_s_pos_sum'))}")
        lines.append(f"- 多头期权市值：{_num(row.get('market_value_long'))}")
        lines.append(f"- 空头期权市值：{_num(row.get('market_value_short'))}")
        lines.append(f"- 保证金占用：{_num(row.get('margin_occupied'))}")
        lines.append("")

        # 核验
        pass_count = row.get("validation_pass", 0) or 0
        total_count = row.get("validation_total", 0) or 0
        fail_count = row.get("validation_fail", 0) or 0

        lines.append("### 核验结果")
        lines.append("")
        lines.append(f"- 状态：{_status_badge(pass_count, total_count, fail_count)}")
        lines.append(f"- 通过：{pass_count}")
        lines.append(f"- 警告：{row.get('validation_warn', 0) or 0}")
        lines.append(f"- 失败：{fail_count}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)