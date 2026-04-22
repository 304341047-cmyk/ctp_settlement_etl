import json
import re
from typing import Any

from app.extractors.section_splitter import split_sections
from app.extractors.table_parser import extract_table_lines, parse_data_rows
from app.models import (
    AccountSummary,
    DepositWithdrawal,
    ExerciseStatement,
    PositionClosed,
    Positions,
    PositionsDetail,
    TransactionRecord,
)
from app.normalizers.field_mapper import (
    check_required_headers,
    normalize_header,
)
from app.normalizers.value_cleaner import clean_float, clean_str
from app.utils.log_utils import setup_logger

logger = setup_logger()


class CtpSettlementParser:
    def parse(self, full_text: str, source_file: str) -> dict[str, Any]:
        sections = split_sections(full_text)

        result: dict[str, Any] = {
            "account_summary": [],
            "deposit_withdrawal": [],
            "transaction_record": [],
            "exercise_statement": [],
            "position_closed": [],
            "positions_detail": [],
            "positions": [],
            "warnings": [],
        }

        if "account_summary" in sections:
            account_summary = self.build_account_summary(
                full_text=full_text,
                section_text=sections["account_summary"].content,
                source_file=source_file,
            )
            result["account_summary"] = [account_summary]

        if "deposit_withdrawal" in sections:
            parsed_table = extract_table_lines(sections["deposit_withdrawal"].content)
            records, warnings = self.build_deposit_withdrawal(parsed_table, source_file)
            result["deposit_withdrawal"] = records
            result["warnings"].extend(warnings)

        if "transaction_record" in sections:
            parsed_table = extract_table_lines(sections["transaction_record"].content)
            records, warnings = self.build_transaction_records(parsed_table, source_file)
            result["transaction_record"] = records
            result["warnings"].extend(warnings)

        if "exercise_statement" in sections:
            parsed_table = extract_table_lines(sections["exercise_statement"].content)
            records, warnings = self.build_exercise_statements(parsed_table, source_file)
            result["exercise_statement"] = records
            result["warnings"].extend(warnings)

        if "position_closed" in sections:
            parsed_table = extract_table_lines(sections["position_closed"].content)
            records, warnings = self.build_position_closed(parsed_table, source_file)
            result["position_closed"] = records
            result["warnings"].extend(warnings)

        if "positions_detail" in sections:
            parsed_table = extract_table_lines(sections["positions_detail"].content)
            records, warnings = self.build_positions_detail(parsed_table, source_file)
            result["positions_detail"] = records
            result["warnings"].extend(warnings)

        if "positions" in sections:
            parsed_table = extract_table_lines(sections["positions"].content)
            records, warnings = self.build_positions(parsed_table, source_file)
            result["positions"] = records
            result["warnings"].extend(warnings)

        logger.info(
            "解析完成 source_file=%s account=%s deposit_withdrawal=%s txn=%s exercise=%s closed=%s pos_detail=%s pos=%s warnings=%s",
            source_file,
            len(result["account_summary"]),
            len(result["deposit_withdrawal"]),
            len(result["transaction_record"]),
            len(result["exercise_statement"]),
            len(result["position_closed"]),
            len(result["positions_detail"]),
            len(result["positions"]),
            len(result["warnings"]),
        )

        return result

    # =========================
    # 通用元信息提取
    # =========================

    def extract_meta(self, full_text: str) -> dict[str, Any]:
        creation_date_match = re.search(r"Creation Date[:：]\s*(\d{8})", full_text, re.IGNORECASE)
        client_id_match = re.search(r"Client ID[:：]\s*([A-Za-z0-9]+)", full_text, re.IGNORECASE)
        client_name_match = re.search(r"Client Name[:：]\s*(\S+)", full_text, re.IGNORECASE)
        account_id_match = re.search(r"AccountID[:：]\s*([A-Za-z0-9]+)", full_text, re.IGNORECASE)
        currency_match = re.search(r"Currency[:：]\s*([A-Za-z]+)", full_text, re.IGNORECASE)

        date_range_match = re.search(r"Date[:：]\s*(\d{8})-(\d{8})", full_text, re.IGNORECASE)
        single_date_match = re.search(r"Date[:：]\s*(\d{8})", full_text, re.IGNORECASE)

        if date_range_match:
            date_from = clean_str(date_range_match.group(1))
            date_to = clean_str(date_range_match.group(2))
        elif single_date_match:
            date_from = clean_str(single_date_match.group(1))
            date_to = clean_str(single_date_match.group(1))
        else:
            date_from = None
            date_to = None

        return {
            "creation_date": clean_str(creation_date_match.group(1)) if creation_date_match else None,
            "date_from": date_from,
            "date_to": date_to,
            "client_id": clean_str(client_id_match.group(1)) if client_id_match else None,
            "client_name": clean_str(client_name_match.group(1)) if client_name_match else None,
            "account_id": clean_str(account_id_match.group(1)) if account_id_match else None,
            "currency": clean_str(currency_match.group(1)) if currency_match else None,
        }

    # =========================
    # 资金状况
    # =========================

    def build_account_summary(
        self,
        full_text: str,
        section_text: str,
        source_file: str,
    ) -> AccountSummary:
        meta = self.extract_meta(full_text)
        field_map = self.extract_account_summary_map(section_text)

        row = AccountSummary(
            creation_date=meta["creation_date"],
            date_from=meta["date_from"],
            date_to=meta["date_to"],
            client_id=meta["client_id"],
            client_name=meta["client_name"],
            account_id=meta["account_id"],
            currency=meta["currency"],

            balance_b_f=field_map.get("balance_b_f"),
            deposit_withdrawal=field_map.get("deposit_withdrawal"),
            realized_p_l=field_map.get("realized_p_l"),
            mtm_p_l=field_map.get("mtm_p_l"),
            exercise_p_l=field_map.get("exercise_p_l"),
            commission=field_map.get("commission"),
            exercise_fee=field_map.get("exercise_fee"),
            delivery_fee=field_map.get("delivery_fee"),
            new_fx_pledge=field_map.get("new_fx_pledge"),
            fx_redemption=field_map.get("fx_redemption"),
            chg_in_pledge_amt=field_map.get("chg_in_pledge_amt"),
            premium_received=field_map.get("premium_received"),
            premium_paid=field_map.get("premium_paid"),
            delivery_p_l=field_map.get("delivery_p_l"),

            initial_margin=field_map.get("initial_margin"),
            balance_c_f=field_map.get("balance_c_f"),
            pledge_amount=field_map.get("pledge_amount"),
            client_equity=field_map.get("client_equity"),
            fx_pledge_occ=field_map.get("fx_pledge_occ"),
            margin_occupied=field_map.get("margin_occupied"),
            delivery_margin=field_map.get("delivery_margin"),
            market_value_long=field_map.get("market_value_long"),
            market_value_short=field_map.get("market_value_short"),
            market_value_equity=field_map.get("market_value_equity"),
            fund_avail=field_map.get("fund_avail"),
            risk_degree=field_map.get("risk_degree"),
            margin_call=field_map.get("margin_call"),
            chg_in_fx_pledge=field_map.get("chg_in_fx_pledge"),

            source_file=source_file,
            raw_payload=json.dumps(field_map, ensure_ascii=False),
        )
        return row

    def extract_account_summary_map(self, section_text: str) -> dict[str, float | str | None]:
        """
        将资金状况区块解析成:
        英文字段 -> 数值
        不依赖左右顺序，只要一行里有 “英文标签: 数值” 就抓。
        """
        alias_map = {
            "balance b/f": "balance_b_f",
            "balance c/f": "balance_c_f",
            "deposit/withdrawal": "deposit_withdrawal",
            "initial margin": "initial_margin",
            "realized p/l": "realized_p_l",
            "mtm p/l": "mtm_p_l",
            "exercise p/l": "exercise_p_l",
            "commission": "commission",
            "exercise fee": "exercise_fee",
            "delivery fee": "delivery_fee",
            "new fx pledge": "new_fx_pledge",
            "fx redemption": "fx_redemption",
            "chg in pledge amt": "chg_in_pledge_amt",
            "premium received": "premium_received",
            "premium paid": "premium_paid",
            "delivery p/l": "delivery_p_l",
            "pledge amount": "pledge_amount",
            "client equity": "client_equity",
            "fx pledge occ": "fx_pledge_occ",
            "fx pledge occ.": "fx_pledge_occ",
            "margin occupied": "margin_occupied",
            "delivery margin": "delivery_margin",
            "market value(long)": "market_value_long",
            "market value(short)": "market_value_short",
            "market value(equity)": "market_value_equity",
            "fund avail": "fund_avail",
            "fund avail.": "fund_avail",
            "risk degree": "risk_degree",
            "margin call": "margin_call",
            "chg in fx pledge": "chg_in_fx_pledge",
        }

        field_map: dict[str, float | str | None] = {}

        pattern = re.compile(
            r"([A-Za-z][A-Za-z0-9\s/().-]*?)\s*[：:]\s*([-\d,.]+%?)",
            re.IGNORECASE,
        )

        for line in section_text.splitlines():
            matches = pattern.findall(line)
            for label, value in matches:
                label_key = label.strip().lower()
                label_key = label_key.replace("  ", " ")
                key = alias_map.get(label_key)
                if not key:
                    continue
                field_map[key] = clean_float(value)

        return field_map

    # =========================
    # 各表格通用处理
    # =========================

    def parse_table(
        self,
        parsed_table,
        section_name: str,
    ) -> tuple[list[dict[str, Any]], list[str]]:
        warnings: list[str] = []

        if not parsed_table.english_header_lines:
            warnings.append(f"{section_name} 缺少英文表头")
            return [], warnings

        header_line = parsed_table.english_header_lines[0]
        headers = normalize_header(header_line)

        warnings.extend(check_required_headers(section_name, headers))

        rows = parse_data_rows(parsed_table.data_lines)
        records: list[dict[str, Any]] = []

        for idx, row in enumerate(rows, start=1):
            if len(row) != len(headers):
                warnings.append(
                    f"{section_name} 第{idx}行列数不匹配: headers={len(headers)} row={len(row)}"
                )
                continue

            row_dict = dict(zip(headers, row))
            records.append(row_dict)

        return records, warnings

    # =========================
    # 出入金明细
    # =========================

    def build_deposit_withdrawal(self, parsed_table, source_file: str):
        row_dicts, warnings = self.parse_table(parsed_table, "deposit_withdrawal")

        results: list[DepositWithdrawal] = []
        for row_dict in row_dicts:
            obj = DepositWithdrawal(
                date=clean_str(row_dict.get("date")),
                type=clean_str(row_dict.get("type")),
                deposit=clean_float(row_dict.get("deposit")),
                withdrawal=clean_float(row_dict.get("withdrawal")),
                exchange_rate=clean_float(row_dict.get("exchange_rate")),
                account_id=clean_str(row_dict.get("account_id")),
                note=clean_str(row_dict.get("note")),
                source_file=source_file,
                raw_payload=json.dumps(row_dict, ensure_ascii=False),
            )
            results.append(obj)

        return results, warnings

    # =========================
    # 成交记录
    # =========================

    def build_transaction_records(self, parsed_table, source_file: str):
        row_dicts, warnings = self.parse_table(parsed_table, "transaction_record")

        results: list[TransactionRecord] = []
        for row_dict in row_dicts:
            obj = TransactionRecord(
                date=clean_str(row_dict.get("date")),
                invest_unit=clean_str(row_dict.get("invest_unit")),
                exchange=clean_str(row_dict.get("exchange")),
                trading_code=clean_str(row_dict.get("trading_code")),
                product=clean_str(row_dict.get("product")),
                instrument=clean_str(row_dict.get("instrument")),
                b_s=clean_str(row_dict.get("b_s")),
                s_h=clean_str(row_dict.get("s_h")),
                price=clean_float(row_dict.get("price")),
                lots=clean_float(row_dict.get("lots")),
                turnover=clean_float(row_dict.get("turnover")),
                o_c=clean_str(row_dict.get("o_c")),
                fee=clean_float(row_dict.get("fee")),
                realized_p_l=clean_float(row_dict.get("realized_p_l")),
                premium_received_paid=clean_float(
                    row_dict.get("premium_received_paid")
                ),
                trans_no=clean_str(row_dict.get("trans_no")),
                account_id=clean_str(row_dict.get("account_id")),
                source_file=source_file,
                raw_payload=json.dumps(row_dict, ensure_ascii=False),
            )
            results.append(obj)

        return results, warnings

    # =========================
    # 行权明细
    # =========================

    def build_exercise_statements(self, parsed_table, source_file: str):
        row_dicts, warnings = self.parse_table(parsed_table, "exercise_statement")

        results: list[ExerciseStatement] = []
        for row_dict in row_dicts:
            obj = ExerciseStatement(
                date=clean_str(row_dict.get("date")),
                invest_unit=clean_str(row_dict.get("invest_unit")),
                exchange=clean_str(row_dict.get("exchange")),
                trading_code=clean_str(row_dict.get("trading_code")),
                product=clean_str(row_dict.get("product")),
                instrument=clean_str(row_dict.get("instrument")),
                b_s=clean_str(row_dict.get("b_s")),
                strike_price=clean_float(row_dict.get("strike_price")),
                exercise_price=clean_float(row_dict.get("exercise_price")),
                lots=clean_float(row_dict.get("lots")),
                turnover=clean_float(row_dict.get("turnover")),
                exercise_p_l=clean_float(row_dict.get("exercise_p_l")),
                exercise_fee=clean_float(row_dict.get("exercise_fee")),
                account_id=clean_str(row_dict.get("account_id")),
                source_file=source_file,
                raw_payload=json.dumps(row_dict, ensure_ascii=False),
            )
            results.append(obj)

        return results, warnings

    # =========================
    # 平仓明细
    # =========================

    def build_position_closed(self, parsed_table, source_file: str):
        row_dicts, warnings = self.parse_table(parsed_table, "position_closed")

        results: list[PositionClosed] = []
        for row_dict in row_dicts:
            obj = PositionClosed(
                close_date=clean_str(row_dict.get("close_date")),
                invest_unit=clean_str(row_dict.get("invest_unit")),
                exchange=clean_str(row_dict.get("exchange")),
                trading_code=clean_str(row_dict.get("trading_code")),
                product=clean_str(row_dict.get("product")),
                instrument=clean_str(row_dict.get("instrument")),
                open_date=clean_str(row_dict.get("open_date")),
                s_h=clean_str(row_dict.get("s_h")),
                b_s=clean_str(row_dict.get("b_s")),
                lots=clean_float(row_dict.get("lots")),
                pos_open_price=clean_float(row_dict.get("pos_open_price")),
                prev_sttl=clean_float(row_dict.get("prev_sttl")),
                trans_price=clean_float(row_dict.get("trans_price")),
                realized_p_l=clean_float(row_dict.get("realized_p_l")),
                premium_received_paid=clean_float(
                    row_dict.get("premium_received_paid")
                ),
                account_id=clean_str(row_dict.get("account_id")),
                source_file=source_file,
                raw_payload=json.dumps(row_dict, ensure_ascii=False),
            )
            results.append(obj)

        return results, warnings

    # =========================
    # 持仓明细
    # =========================

    def build_positions_detail(self, parsed_table, source_file: str):
        row_dicts, warnings = self.parse_table(parsed_table, "positions_detail")

        results: list[PositionsDetail] = []
        for row_dict in row_dicts:
            obj = PositionsDetail(
                invest_unit=clean_str(row_dict.get("invest_unit")),
                exchange=clean_str(row_dict.get("exchange")),
                trading_code=clean_str(row_dict.get("trading_code")),
                product=clean_str(row_dict.get("product")),
                instrument=clean_str(row_dict.get("instrument")),
                open_date=clean_str(row_dict.get("open_date")),
                s_h=clean_str(row_dict.get("s_h")),
                b_s=clean_str(row_dict.get("b_s")),
                position_qty=clean_float(
                    row_dict.get("position_qty") or row_dict.get("positon")
                ),
                pos_open_price=clean_float(
                    row_dict.get("pos_open_price") or row_dict.get("open_price")
                ),
                prev_sttl=clean_float(row_dict.get("prev_sttl")),
                settlement_price=clean_float(
                    row_dict.get("settlement_price") or row_dict.get("sttl_today")
                ),
                accum_p_l=clean_float(row_dict.get("accum_p_l")),
                mtm_p_l=clean_float(row_dict.get("mtm_p_l")),
                margin=clean_float(row_dict.get("margin")),
                market_value=clean_float(
                    row_dict.get("market_value")
                    or row_dict.get("market_val")
                    or row_dict.get("market_value_options")
                ),
                account_id=clean_str(row_dict.get("account_id")),
                source_file=source_file,
                raw_payload=json.dumps(row_dict, ensure_ascii=False),
            )
            results.append(obj)

        return results, warnings

    # =========================
    # 持仓汇总
    # =========================

    def build_positions(self, parsed_table, source_file: str):
        row_dicts, warnings = self.parse_table(parsed_table, "positions")

        results: list[Positions] = []
        for row_dict in row_dicts:
            obj = Positions(
                invest_unit=clean_str(row_dict.get("invest_unit")),
                trading_code=clean_str(row_dict.get("trading_code")),
                product=clean_str(row_dict.get("product")),
                instrument=clean_str(row_dict.get("instrument")),
                long_pos=clean_float(
                    row_dict.get("long_pos") or row_dict.get("b_pos")
                ),
                avg_buy_price=clean_float(row_dict.get("avg_buy_price")),
                short_pos=clean_float(
                    row_dict.get("short_pos") or row_dict.get("s_pos")
                ),
                avg_sell_price=clean_float(row_dict.get("avg_sell_price")),
                prev_sttl=clean_float(row_dict.get("prev_sttl")),
                sttl_today=clean_float(row_dict.get("sttl_today")),
                mtm_p_l=clean_float(row_dict.get("mtm_p_l")),
                margin_occupied=clean_float(row_dict.get("margin_occupied")),
                s_h=clean_str(row_dict.get("s_h")),
                market_value_long=clean_float(
                    row_dict.get("market_value_long") or row_dict.get("market_valuelong")
                ),
                market_value_short=clean_float(
                    row_dict.get("market_value_short") or row_dict.get("market_valueshort")
                ),
                account_id=clean_str(row_dict.get("account_id")),
                source_file=source_file,
                raw_payload=json.dumps(row_dict, ensure_ascii=False),
            )
            results.append(obj)

        return results, warnings