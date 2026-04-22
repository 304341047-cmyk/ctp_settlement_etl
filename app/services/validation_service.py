from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.models import ValidationResult
from app.utils.log_utils import setup_logger

logger = setup_logger()


class ValidationService:
    def __init__(self, tolerance: float = 0.01) -> None:
        self.tolerance = tolerance

    def validate(self, parsed: dict[str, Any]) -> list[ValidationResult]:
        results: list[ValidationResult] = []

        account_rows = parsed.get("account_summary", [])
        if not account_rows:
            results.append(
                self._warn(
                    check_name="account_summary_exists",
                    details="缺少资金状况，无法执行主核验",
                    source_file=self._guess_source_file(parsed),
                )
            )
            return results

        account = account_rows[0]
        source_file = account.source_file

        # 1. 客户权益勾稽
        results.append(self.check_customer_equity(account))

        # 2. 市值权益勾稽
        results.append(self.check_market_value_equity(account))

        # 3. 风险度检查
        results.append(self.check_risk_degree(account))

        # 4. 出入金汇总检查
        results.append(
            self.check_deposit_withdrawal_consistency(
                account=account,
                deposit_rows=parsed.get("deposit_withdrawal", []),
                source_file=source_file,
            )
        )

        # 5. 成交汇总基础检查
        results.append(
            self.check_transaction_fee_non_negative(
                parsed.get("transaction_record", []),
                source_file=source_file,
            )
        )

        # 6. 持仓汇总基础检查
        results.append(
            self.check_positions_market_value_non_negative(
                parsed.get("positions", []),
                source_file=source_file,
            )
        )

        logger.info(
            "核验完成 source_file=%s results=%s",
            source_file,
            len(results),
        )
        return results

    # =========================
    # 具体检查项
    # =========================

    def check_customer_equity(self, account) -> ValidationResult:
        """
        客户权益勾稽：
        期初结存
        + 出入金
        + 平仓盈亏
        + 持仓盯市盈亏
        + 交割盈亏
        + 权利金收入
        - 权利金支出
        - 手续费
        - 行权手续费
        - 交割手续费
        = 客户权益
        """
        required_values = [
            account.balance_b_f,
            account.deposit_withdrawal,
            account.realized_p_l,
            account.mtm_p_l,
            account.delivery_p_l,
            account.premium_received,
            account.premium_paid,
            account.commission,
            account.exercise_fee,
            account.delivery_fee,
            account.client_equity,
        ]

        if any(v is None for v in required_values):
            return self._warn(
                check_name="customer_equity_check",
                details="客户权益勾稽字段不完整，已跳过严格校验",
                source_file=account.source_file,
            )

        actual = (
            (account.balance_b_f or 0)
            + (account.deposit_withdrawal or 0)
            + (account.realized_p_l or 0)
            + (account.mtm_p_l or 0)
            + (account.delivery_p_l or 0)
            + (account.premium_received or 0)
            - (account.premium_paid or 0)
            - (account.commission or 0)
            - (account.exercise_fee or 0)
            - (account.delivery_fee or 0)
        )
        expected = account.client_equity or 0
        diff = actual - expected

        return self._result_from_diff(
            check_name="customer_equity_check",
            actual_value=actual,
            expected_value=expected,
            diff_value=diff,
            tolerance=self.tolerance,
            source_file=account.source_file,
        )

    def check_market_value_equity(self, account) -> ValidationResult:
        """
        市值权益勾稽：
        客户权益 - 多头期权市值 + 空头期权市值 = 市值权益
        """
        required_values = [
            account.client_equity,
            account.market_value_long,
            account.market_value_short,
            account.market_value_equity,
        ]

        if any(v is None for v in required_values):
            return self._warn(
                check_name="market_value_equity_check",
                details="市值权益勾稽字段不完整，已跳过严格校验",
                source_file=account.source_file,
            )

        actual = (
            (account.client_equity or 0)
            + (account.market_value_long or 0)
            - (account.market_value_short or 0)
        )
        expected = account.market_value_equity or 0
        diff = actual - expected

        return self._result_from_diff(
            check_name="market_value_equity_check",
            actual_value=actual,
            expected_value=expected,
            diff_value=diff,
            tolerance=self.tolerance,
            source_file=account.source_file,
        )

    def check_risk_degree(self, account) -> ValidationResult:
        """
        风险度只做基础检查：
        - 若保证金占用和客户权益齐全，则核验风险度是否接近 margin_occupied / client_equity * 100
        """
        required_values = [
            account.margin_occupied,
            account.client_equity,
            account.risk_degree,
        ]

        if any(v is None for v in required_values):
            return self._warn(
                check_name="risk_degree_check",
                details="风险度字段不完整，已跳过严格校验",
                source_file=account.source_file,
            )

        if abs(account.client_equity or 0) < 1e-12:
            return self._warn(
                check_name="risk_degree_check",
                details="客户权益为0，无法计算风险度",
                source_file=account.source_file,
            )

        actual = (account.margin_occupied or 0) / (account.client_equity or 1) * 100
        expected = account.risk_degree or 0
        diff = actual - expected

        # 风险度是百分比，允许误差稍微大一点
        return self._result_from_diff(
            check_name="risk_degree_check",
            actual_value=actual,
            expected_value=expected,
            diff_value=diff,
            tolerance=0.05,
            source_file=account.source_file,
        )

    def check_deposit_withdrawal_consistency(self, account, deposit_rows, source_file: str) -> ValidationResult:
        """
        核验资金状况里的出入金，是否和出入金明细汇总一致。
        公式：sum(deposit - withdrawal) == account.deposit_withdrawal
        """
        if account.deposit_withdrawal is None:
            return self._warn(
                check_name="deposit_withdrawal_check",
                details="资金状况缺少出入金字段，已跳过严格校验",
                source_file=source_file,
            )

        if not deposit_rows:
            return ValidationResult(
                check_name="deposit_withdrawal_check",
                status="PASS",
                actual_value=None,
                expected_value=None,
                diff_value=None,
                tolerance=None,
                details="无出入金明细，跳过校验",
                source_file=source_file,
            )

        actual = 0.0
        for r in deposit_rows:
            actual += (r.deposit or 0) - (r.withdrawal or 0)

        expected = account.deposit_withdrawal or 0
        diff = actual - expected

        return self._result_from_diff(
            check_name="deposit_withdrawal_check",
            actual_value=actual,
            expected_value=expected,
            diff_value=diff,
            tolerance=self.tolerance,
            source_file=source_file,
        )

    def check_transaction_fee_non_negative(self, txn_rows, source_file: str) -> ValidationResult:
        """
        基础健全性检查：手续费不应为负数。
        """
        if not txn_rows:
            return ValidationResult(
                check_name="transaction_fee_non_negative",
                status="PASS",
                actual_value=None,
                expected_value=None,
                diff_value=None,
                tolerance=None,
                details="无成交记录，跳过检查",
                source_file=source_file,
            )

        negative_count = sum(1 for r in txn_rows if (r.fee is not None and r.fee < 0))
        if negative_count > 0:
            return ValidationResult(
                check_name="transaction_fee_non_negative",
                status="FAIL",
                actual_value=float(negative_count),
                expected_value=0.0,
                diff_value=float(negative_count),
                tolerance=0.0,
                details=f"发现 {negative_count} 条成交记录手续费为负数",
                source_file=source_file,
            )

        return ValidationResult(
            check_name="transaction_fee_non_negative",
            status="PASS",
            actual_value=0.0,
            expected_value=0.0,
            diff_value=0.0,
            tolerance=0.0,
            details="成交记录手续费检查通过",
            source_file=source_file,
        )

    def check_positions_market_value_non_negative(self, pos_rows, source_file: str) -> ValidationResult:
        """
        基础健全性检查：期权市值不应为负数。
        """
        if not pos_rows:
            return ValidationResult(
                check_name="positions_market_value_non_negative",
                status="PASS",
                actual_value=None,
                expected_value=None,
                diff_value=None,
                tolerance=None,
                details="无持仓汇总，跳过检查",
                source_file=source_file,
            )

        invalid_count = 0
        for r in pos_rows:
            if r.market_value_long is not None and r.market_value_long < 0:
                invalid_count += 1
            if r.market_value_short is not None and r.market_value_short < 0:
                invalid_count += 1

        if invalid_count > 0:
            return ValidationResult(
                check_name="positions_market_value_non_negative",
                status="FAIL",
                actual_value=float(invalid_count),
                expected_value=0.0,
                diff_value=float(invalid_count),
                tolerance=0.0,
                details=f"发现 {invalid_count} 个负期权市值字段",
                source_file=source_file,
            )

        return ValidationResult(
            check_name="positions_market_value_non_negative",
            status="PASS",
            actual_value=0.0,
            expected_value=0.0,
            diff_value=0.0,
            tolerance=0.0,
            details="持仓汇总期权市值检查通过",
            source_file=source_file,
        )

    # =========================
    # 工具函数
    # =========================

    def _result_from_diff(
        self,
        check_name: str,
        actual_value: float,
        expected_value: float,
        diff_value: float,
        tolerance: float,
        source_file: str,
    ) -> ValidationResult:
        status = "PASS" if abs(diff_value) <= tolerance else "FAIL"
        details = f"差额={diff_value:,.6f}, 容差={tolerance:,.6f}"

        return ValidationResult(
            check_name=check_name,
            status=status,
            actual_value=actual_value,
            expected_value=expected_value,
            diff_value=diff_value,
            tolerance=tolerance,
            details=details,
            source_file=source_file,
        )

    def _warn(self, check_name: str, details: str, source_file: str) -> ValidationResult:
        return ValidationResult(
            check_name=check_name,
            status="WARN",
            actual_value=None,
            expected_value=None,
            diff_value=None,
            tolerance=None,
            details=details,
            source_file=source_file,
        )

    def _guess_source_file(self, parsed: dict[str, Any]) -> str:
        for key in [
            "account_summary",
            "deposit_withdrawal",
            "transaction_record",
            "exercise_statement",
            "position_closed",
            "positions_detail",
            "positions",
        ]:
            rows = parsed.get(key, [])
            if rows:
                first = rows[0]
                source_file = getattr(first, "source_file", "")
                if source_file:
                    return source_file
        return ""