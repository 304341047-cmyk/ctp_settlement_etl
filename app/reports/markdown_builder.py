from __future__ import annotations

from typing import Any


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _num(value: Any, digits: int = 2) -> str:
    v = _to_float(value)
    if v is None:
        return ""
    return f"{v:,.{digits}f}"


def _color(value: Any, is_percent: bool = False) -> str:
    v = _to_float(value)
    if v is None:
        return "black"

    if is_percent:
        # 风险度单独口径：高风险橙色
        if v >= 85:
            return "orange"
        return "black"

    if v > 0:
        return "red"
    if v < 0:
        return "green"
    return "black"


def _color_value(value: Any, is_percent: bool = False, bold: bool = False) -> str:
    v = _to_float(value)
    if v is None:
        text = ""
        return f"**{text}**" if bold else text

    color = _color(v, is_percent=is_percent)
    if is_percent:
        text = f"{v:.2f}%"
    else:
        text = f"{v:+,.2f}" if v != 0 else f"{v:,.2f}"

    html = f'<span style="color:{color}">{text}</span>'
    return f"**{html}**" if bold else html


def _diff_color(value: Any) -> str:
    v = _to_float(value)
    if v is None:
        return ""

    # 勾稽差额：0为黑色，非0统一绿色保留你原来的视觉习惯
    color = "black" if abs(v) < 1e-9 else "green"
    text = f"{v:+,.2f}" if v != 0 else f"{v:,.2f}"
    return f'<span style="color:{color}">{text}</span>'


def _status_badge(pass_count: int, total_count: int, fail_count: int, warn_count: int = 0) -> str:
    if fail_count > 0:
        return f'<span style="color:red">存在失败（通过 {pass_count}/{total_count}）</span>'
    if warn_count > 0:
        return f'<span style="color:orange">有警告（通过 {pass_count}/{total_count}）</span>'
    return f'<span style="color:green">全部通过（{pass_count}/{total_count}）</span>'


def build_markdown_report(rows: list[dict[str, Any]]) -> str:
    lines: list[str] = []

    for idx, row in enumerate(rows):
        account_id = row.get("account_id", "")
        client_name = row.get("client_name", "")
        date_from = row.get("date_from", "")
        source_file = row.get("source_file", "")

        pass_count = int(row.get("validation_pass", 0) or 0)
        warn_count = int(row.get("validation_warn", 0) or 0)
        fail_count = int(row.get("validation_fail", 0) or 0)
        total_count = int(row.get("validation_total", 0) or 0)

        lines.append(f"## 账户：{account_id}（{client_name}）")
        lines.append(f"- 日期：{date_from}")
        lines.append(f"- 文件：`{source_file}`")
        lines.append("")
        lines.append("### 总览")
        lines.append("")
        lines.append(f"- 客户权益：**{_num(row.get('client_equity'))}**")
        lines.append(f"- 市值权益：**{_num(row.get('market_value_equity'))}**")
        lines.append(f"- 出入金：{_color_value(row.get('deposit_withdrawal'))}")
        lines.append(f"- 保证金占用：{_num(row.get('margin_occupied'))}")
        lines.append(f"- 可用资金：{_num(row.get('fund_avail'))}")
        lines.append(f"- 风险度：**{_color_value(row.get('risk_degree'), is_percent=True)}**")
        lines.append("")
        lines.append("### 盈亏归因")
        lines.append("")
        lines.append(f"- 当日总盈亏（含手续费）：{_color_value(row.get('total_pnl'))}")
        lines.append(f"- 当日盈亏：**{_color_value(row.get('pnl'))}**")
        lines.append(f"- 当日期货盈亏：**{_color_value(row.get('futures_pnl'))}**")
        lines.append(f"- 当日期权盈亏：**{_color_value(row.get('option_pnl'))}**")

        total_fee = _to_float(row.get("total_fee"))
        total_fee_display = -total_fee if total_fee is not None else None
        lines.append(f"- 手续费合计：{_color_value(total_fee_display)}")
        lines.append("")
        lines.append("### 期权市值")
        lines.append("")
        lines.append(f"- 权利金变动：{_color_value(row.get('premium_change'))}")
        lines.append(f"- 期权市值变动：{_color_value(row.get('option_market_value_change'))}")
        lines.append(f"- 当日期权市值：{_num(row.get('option_market_value'))}")
        lines.append(f"- 上日期权市值：{_num(row.get('prev_option_market_value'))}")
        lines.append("")
        lines.append("### 交易概览")
        lines.append("")
        lines.append(f"- 成交笔数：{int(row.get('trade_count', 0) or 0)}")
        lines.append(f"- 成交手数：{_num(row.get('trade_lots'))}")
        lines.append(f"- 成交额：{_num(row.get('turnover'))}")
        lines.append("")
        lines.append("### 持仓概览")
        lines.append("")
        lines.append(f"- 持仓条目数：{int(row.get('position_count', 0) or 0)}")
        lines.append(f"- 多头持仓合计：{_num(row.get('long_pos_total'))}")
        lines.append(f"- 空头持仓合计：{_num(row.get('short_pos_total'))}")
        lines.append(f"- 多头期权市值：{_num(row.get('market_value_long_total'))}")
        lines.append(f"- 空头期权市值：{_num(row.get('market_value_short_total'))}")
        lines.append("")
        lines.append("### 行权概览")
        lines.append("")
        lines.append(f"- 行权笔数：{int(row.get('exercise_count', 0) or 0)}")
        lines.append(f"- 行权数量：{_num(row.get('exercise_lots'))}")
        lines.append(f"- 行权盈亏：{_color_value(row.get('exercise_p_l_total'))}")
        lines.append(f"- 行权手续费：{_num(row.get('exercise_fee_total'))}")
        lines.append("")
        lines.append("### 核验结果")
        lines.append("")
        lines.append(f"- 计算客户权益：{_num(row.get('customer_equity_calc_value'))}")
        lines.append(f"- 计算市值权益：{_num(row.get('market_value_equity_calc_value'))}")
        lines.append(f"- 市值权益勾稽差额：{_diff_color(row.get('market_value_equity_check_diff'))}")
        lines.append(f"- 客户权益勾稽差额：{_diff_color(row.get('customer_equity_check_diff'))}")
        lines.append(f"- 状态：{_status_badge(pass_count, total_count, fail_count, warn_count)}")
        lines.append(f"- 通过：{pass_count}")
        lines.append(f"- 警告：{warn_count}")
        lines.append(f"- 失败：{fail_count}")

        if idx < len(rows) - 1:
            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)