from pathlib import Path
from typing import Any
import json
import re

from app.extractors.section_splitter import split_sections
from app.extractors.table_parser import extract_table_lines, parse_data_rows
from app.extractors.text_reader import read_text_file
from app.models import (
    AccountSummary,
    TransactionRecord,
    ExerciseStatement,
    PositionClosed,
    PositionsDetail,
    Positions,
)
from app.utils.log_utils import setup_logger
from app.normalizers.field_mapper import normalize_header
from app.normalizers.value_cleaner import clean_float, clean_str
from app.parsers.base_parser import BaseParser

logger = setup_logger()

class CtpSettlementParser(BaseParser):
    name = "CtpSettlementParser"

    def can_parse(self, file_path: Path) -> bool:
        if file_path.suffix.lower() != ".txt":
            return False

        try:
            text = read_text_file(file_path)
        except Exception:
            return False

        keywords = ["交易结算单", "资金状况", "成交记录"]
        hit_count = sum(1 for keyword in keywords if keyword in text)
        return hit_count >= 2

    def parse(self, file_path: Path) -> dict[str, Any]:
        text = read_text_file(file_path)
        sections = split_sections(text)

        result = self.empty_result()
        debug_sections = {}
        source_file = file_path.name

        for section_key, section_block in sections.items():
            parsed_table = extract_table_lines(section_block.content)

            debug_sections[section_key] = {
                "title": section_block.title,
                "raw_line_count": len(parsed_table.raw_lines),
                "header_count": len(parsed_table.header_lines),
                "english_header_count": len(parsed_table.english_header_lines),
                "data_count": len(parsed_table.data_lines),
                "summary_count": len(parsed_table.summary_lines),
                "sample_data_rows": parsed_table.data_lines[:2],
            }

        if "account_summary" in sections:
            result["account_summary"] = self.build_account_summary(
                text,
                sections["account_summary"].content,
                source_file,
            )

        if "transaction_record" in sections:
            trade_table = extract_table_lines(sections["transaction_record"].content)
            result["transaction_record"] = self.build_transaction_records(
                trade_table,
                source_file,
            )

        if "exercise_statement" in sections:
            exercise_table = extract_table_lines(sections["exercise_statement"].content)
            result["exercise_statement"] = self.build_exercise_statements(
                exercise_table,
                source_file,
            )

        if "position_closed" in sections:
            close_table = extract_table_lines(sections["position_closed"].content)
            result["position_closed"] = self.build_position_closed(
                close_table,
                source_file,
            )

        if "positions_detail" in sections:
            detail_table = extract_table_lines(sections["positions_detail"].content)
            result["positions_detail"] = self.build_positions_detail(
                detail_table,
                source_file,
            )

        if "positions" in sections:
            positions_table = extract_table_lines(sections["positions"].content)
            result["positions"] = self.build_positions(
                positions_table,
                source_file,
            )

        result["debug_sections"] = debug_sections
        return result

    def extract_text(self, text: str, pattern: str):
        match = re.search(pattern, text, re.MULTILINE)
        if not match:
            return None
        return clean_str(match.group(1))

    def extract_number(self, text: str, pattern: str):
        match = re.search(pattern, text, re.MULTILINE)
        if not match:
            return None
        return clean_float(match.group(1))

    def build_account_summary(self, full_text: str, section_text: str, source_file: str):
        creation_date = self.extract_text(
            full_text,
            r"Creation Date[：:]\s*(\d{8})",
        )

        date_match = re.search(
            r"Date:\s*(\d{8})-(\d{8})",
            full_text,
            re.MULTILINE,
        )
        date_from = clean_str(date_match.group(1)) if date_match else None
        date_to = clean_str(date_match.group(2)) if date_match else None

        client_id = self.extract_text(
            full_text,
            r"Client ID:\s*(\S+)",
        )
        client_name = self.extract_text(
            full_text,
            r"Client Name:\s*(\S+)",
        )
        account_id = self.extract_text(
            full_text,
            r"AccountID:\s*(\S+)",
        )
        currency = self.extract_text(
            section_text,
            r"Currency\s*:\s*([A-Za-z0-9\u4e00-\u9fa5]+)",
        )

        row = {
            "creation_date": creation_date,
            "date_from": date_from,
            "date_to": date_to,
            "client_id": client_id,
            "client_name": client_name,
            "account_id": account_id,
            "currency": currency,

            "balance_b_f": self.extract_number(section_text, r"Balance b/f:\s*([-\d.]+)"),
            "balance_c_f": self.extract_number(section_text, r"Balance c/f:\s*([-\d.]+)"),
            "deposit_withdrawal": self.extract_number(section_text, r"Deposit/Withdrawal:\s*([-\d.]+)"),
            "initial_margin": self.extract_number(section_text, r"Initial Margin:\s*([-\d.]+)"),
            "realized_p_l": self.extract_number(section_text, r"Realized P/L:\s*([-\d.]+)"),
            "mtm_p_l": self.extract_number(section_text, r"MTM P/L:\s*([-\d.]+)"),
            "market_value_equity": self.extract_number(section_text, r"market value\(equity\):\s*([-\d.]+)"),
            "client_equity": self.extract_number(section_text, r"Client Equity:\s*([-\d.]+)"),
            "exercise_p_l": self.extract_number(section_text, r"Exercise P/L:\s*([-\d.]+)"),
            "fx_pledge_occ": self.extract_number(section_text, r"FX Pledge Occ\.\s*:\s*([-\d.]+)"),
            "commission": self.extract_number(section_text, r"Commission:\s*([-\d.]+)"),
            "exercise_fee": self.extract_number(section_text, r"Exercise Fee:\s*([-\d.]+)"),
            "margin_occupied": self.extract_number(section_text, r"Margin Occupied:\s*([-\d.]+)"),
            "delivery_margin": self.extract_number(section_text, r"Delivery Margin:\s*([-\d.]+)"),
            "market_value_short": self.extract_number(section_text, r"market value\(short\):\s*([-\d.]+)"),
            "market_value_long": self.extract_number(section_text, r"market value\(long\):\s*([-\d.]+)"),
            "new_fx_pledge": self.extract_number(section_text, r"New FX Pledge:\s*([-\d.]+)"),
            "fx_redemption": self.extract_number(section_text, r"FX Redemption:\s*([-\d.]+)"),
            "delivery_fee": self.extract_number(section_text, r"Delivery Fee:\s*([-\d.]+)"),
            "pledge_amount": self.extract_number(section_text, r"Pledge Amount:\s*([-\d.]+)"),
            "chg_in_pledge_amt": self.extract_number(section_text, r"Chg in Pledge Amt:\s*([-\d.]+)"),
            "fund_avail": self.extract_number(section_text, r"Fund Avail\.\s*:\s*([-\d.]+)"),
            "premium_received": self.extract_number(section_text, r"premium received:\s*([-\d.]+)"),
            "premium_paid": self.extract_number(section_text, r"premium paid:\s*([-\d.]+)"),
            "risk_degree": self.extract_number(section_text, r"Risk Degree:\s*([-\d.]+%?)"),
            "margin_call": self.extract_number(section_text, r"Margin Call:\s*([-\d.]+)"),
            "delivery_p_l": self.extract_number(section_text, r"Delivery P/L:\s*([-\d.]+)"),
            "chg_in_fx_pledge": self.extract_number(section_text, r"Chg in FX Pledge:\s*([-\d.]+)"),
        }

        obj = AccountSummary(
            creation_date=row["creation_date"],
            date_from=row["date_from"],
            date_to=row["date_to"],
            client_id=row["client_id"],
            client_name=row["client_name"],
            account_id=row["account_id"],
            currency=row["currency"],
            balance_b_f=row["balance_b_f"],
            balance_c_f=row["balance_c_f"],
            deposit_withdrawal=row["deposit_withdrawal"],
            initial_margin=row["initial_margin"],
            realized_p_l=row["realized_p_l"],
            mtm_p_l=row["mtm_p_l"],
            market_value_equity=row["market_value_equity"],
            client_equity=row["client_equity"],
            exercise_p_l=row["exercise_p_l"],
            fx_pledge_occ=row["fx_pledge_occ"],
            commission=row["commission"],
            exercise_fee=row["exercise_fee"],
            margin_occupied=row["margin_occupied"],
            delivery_margin=row["delivery_margin"],
            market_value_short=row["market_value_short"],
            market_value_long=row["market_value_long"],
            new_fx_pledge=row["new_fx_pledge"],
            fx_redemption=row["fx_redemption"],
            delivery_fee=row["delivery_fee"],
            pledge_amount=row["pledge_amount"],
            chg_in_pledge_amt=row["chg_in_pledge_amt"],
            fund_avail=row["fund_avail"],
            premium_received=row["premium_received"],
            premium_paid=row["premium_paid"],
            risk_degree=row["risk_degree"],
            margin_call=row["margin_call"],
            delivery_p_l=row["delivery_p_l"],
            chg_in_fx_pledge=row["chg_in_fx_pledge"],
            source_file=source_file,
            raw_payload=json.dumps(row, ensure_ascii=False),
        )

        return [obj]

    def build_transaction_records(self, parsed_table, source_file):
        if not parsed_table.english_header_lines:
            return []

        header_line = parsed_table.english_header_lines[0]
        headers = normalize_header(header_line)
        rows = parse_data_rows(parsed_table.data_lines)

        results = []

        for row in rows:
            if len(row) != len(headers):
                continue

            row_dict = dict(zip(headers, row))

            obj = TransactionRecord(
                date=clean_str(row_dict.get("date")),
                invest_unit=clean_str(row_dict.get("investunit")),
                exchange=clean_str(row_dict.get("exchange")),
                trading_code=clean_str(row_dict.get("tradingcode")),
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
                premium_r_p=clean_float(row_dict.get("premium_r_p")),
                trans_no=clean_str(row_dict.get("transno")),
                source_file=source_file,
                raw_payload=json.dumps(row_dict, ensure_ascii=False),
            )
            results.append(obj)

        return results

    def build_exercise_statements(self, parsed_table, source_file):
        if not parsed_table.english_header_lines:
            return []

        header_line = parsed_table.english_header_lines[0]
        headers = normalize_header(header_line)
        rows = parse_data_rows(parsed_table.data_lines)

        results = []

        for row in rows:
            if len(row) != len(headers):
                continue

            row_dict = dict(zip(headers, row))

            obj = ExerciseStatement(
                date=clean_str(row_dict.get("date")),
                invest_unit=clean_str(row_dict.get("investunit")),
                exchange=clean_str(row_dict.get("exchange")),
                trading_code=clean_str(row_dict.get("tradingcode")),
                product=clean_str(row_dict.get("product")),
                instrument=clean_str(row_dict.get("instrument")),
                s_h=clean_str(row_dict.get("s_h")),
                b_s=clean_str(row_dict.get("b_s")),
                exercise_abandon=clean_str(row_dict.get("exercise_abandon")),
                volume_exercised=clean_float(row_dict.get("volume_exercised")),
                ex_price=clean_float(row_dict.get("ex_price")),
                amount_exercised=clean_float(row_dict.get("amount_exercised")),
                exercise_p_l=clean_float(row_dict.get("exercise_p_l")),
                exercise_fee=clean_float(row_dict.get("exercise_fee")),
                source_file=source_file,
                raw_payload=json.dumps(row_dict, ensure_ascii=False),
            )
            results.append(obj)

        return results

    def build_position_closed(self, parsed_table, source_file):
        if not parsed_table.english_header_lines:
            return []

        header_line = parsed_table.english_header_lines[0]
        headers = normalize_header(header_line)
        rows = parse_data_rows(parsed_table.data_lines)

        results = []

        for row in rows:
            if len(row) != len(headers):
                continue

            row_dict = dict(zip(headers, row))

            obj = PositionClosed(
                close_date=clean_str(row_dict.get("close_date")),
                invest_unit=clean_str(row_dict.get("investunit")),
                exchange=clean_str(row_dict.get("exchange")),
                trading_code=clean_str(row_dict.get("tradingcode")),
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
                premium_received_paid=clean_float(row_dict.get("premium_received_paid")),
                premium_netting=clean_float(row_dict.get("premium_netting")),
                source_file=source_file,
                raw_payload=json.dumps(row_dict, ensure_ascii=False),
            )
            results.append(obj)

        return results

    def build_positions_detail(self, parsed_table, source_file):
        if not parsed_table.english_header_lines:
            return []

        header_line = parsed_table.english_header_lines[0]
        headers = normalize_header(header_line)
        rows = parse_data_rows(parsed_table.data_lines)

        results = []

        for row in rows:
            if len(row) != len(headers):
                continue

            row_dict = dict(zip(headers, row))

            obj = PositionsDetail(
                invest_unit=clean_str(row_dict.get("investunit")),
                exchange=clean_str(row_dict.get("exchange")),
                trading_code=clean_str(row_dict.get("tradingcode")),
                product=clean_str(row_dict.get("product")),
                instrument=clean_str(row_dict.get("instrument")),
                open_date=clean_str(row_dict.get("open_date")),
                s_h=clean_str(row_dict.get("s_h")),
                b_s=clean_str(row_dict.get("b_s")),
                positon=clean_float(row_dict.get("positon")),
                open_price=clean_float(row_dict.get("open_price")),
                prev_sttl=clean_float(row_dict.get("prev_sttl")),
                sttl_today=clean_float(row_dict.get("sttl_today")),
                accum_p_l=clean_float(row_dict.get("accum_p_l")),
                mtm_p_l=clean_float(row_dict.get("mtm_p_l")),
                margin=clean_float(row_dict.get("margin")),
                market_val=clean_float(row_dict.get("market_val")),
                market_val_chg=clean_float(row_dict.get("market_val_chg")),
                source_file=source_file,
                raw_payload=json.dumps(row_dict, ensure_ascii=False),
            )
            results.append(obj)

        return results

    def build_positions(self, parsed_table, source_file):
        if not parsed_table.english_header_lines:
            return []

        header_line = parsed_table.english_header_lines[0]
        headers = normalize_header(header_line)
        rows = parse_data_rows(parsed_table.data_lines)

        results = []

        for row in rows:
            if len(row) != len(headers):
                continue

            row_dict = dict(zip(headers, row))

            obj = Positions(
                invest_unit=clean_str(row_dict.get("investunit")),
                trading_code=clean_str(row_dict.get("tradingcode")),
                product=clean_str(row_dict.get("product")),
                instrument=clean_str(row_dict.get("instrument")),
                long_pos=clean_float(row_dict.get("long_pos")),
                avg_buy_price=clean_float(row_dict.get("avg_buy_price")),
                s_pos=clean_float(row_dict.get("s_pos")),
                avg_sell_price=clean_float(row_dict.get("avg_sell_price")),
                prev_sttl=clean_float(row_dict.get("prev_sttl")),
                sttl_today=clean_float(row_dict.get("sttl_today")),
                mtm_p_l=clean_float(row_dict.get("mtm_p_l")),
                margin_occupied=clean_float(row_dict.get("margin_occupied")),
                s_h=clean_str(row_dict.get("s_h")),
                market_value_long=clean_float(row_dict.get("market_valuelong")),
                market_value_short=clean_float(row_dict.get("market_valueshort")),
                source_file=source_file,
                raw_payload=json.dumps(row_dict, ensure_ascii=False),
            )
            results.append(obj)

        return results