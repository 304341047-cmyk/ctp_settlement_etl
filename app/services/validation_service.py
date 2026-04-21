import sqlite3
from decimal import Decimal

from app.models import ValidationResult


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _sum_value(conn: sqlite3.Connection, table: str, column: str, source_file: str) -> Decimal:
    sql = f"SELECT COALESCE(SUM({column}), 0) FROM {table} WHERE source_file = ?"
    row = conn.execute(sql, (source_file,)).fetchone()
    return _to_decimal(row[0] if row else 0)


def _count_rows(conn: sqlite3.Connection, table: str, source_file: str) -> int:
    sql = f"SELECT COUNT(*) FROM {table} WHERE source_file = ?"
    row = conn.execute(sql, (source_file,)).fetchone()
    return int(row[0] if row else 0)


def _get_account_summary_row(conn: sqlite3.Connection, source_file: str):
    sql = """
    SELECT *
    FROM account_summary
    WHERE source_file = ?
    LIMIT 1
    """
    return conn.execute(sql, (source_file,)).fetchone()


def _build_compare_result(
    source_file: str,
    rule_code: str,
    rule_name: str,
    actual,
    expected,
    tolerance: Decimal = Decimal("0.01"),
):
    actual_dec = _to_decimal(actual)
    expected_dec = _to_decimal(expected)
    diff = actual_dec - expected_dec

    status = "PASS" if abs(diff) <= tolerance else "FAIL"

    return ValidationResult(
        source_file=source_file,
        rule_code=rule_code,
        rule_name=rule_name,
        status=status,
        actual_value=str(actual_dec),
        expected_value=str(expected_dec),
        diff_value=float(diff),
        message=f"{rule_name}: actual={actual_dec}, expected={expected_dec}, diff={diff}",
    )


def _build_count_result(
    source_file: str,
    rule_code: str,
    rule_name: str,
    actual_count: int,
    expected_count: int,
):
    status = "PASS" if actual_count == expected_count else "FAIL"

    return ValidationResult(
        source_file=source_file,
        rule_code=rule_code,
        rule_name=rule_name,
        status=status,
        actual_value=str(actual_count),
        expected_value=str(expected_count),
        diff_value=float(actual_count - expected_count),
        message=f"{rule_name}: actual={actual_count}, expected={expected_count}",
    )


def _build_nonnegative_count_result(
    source_file: str,
    rule_code: str,
    rule_name: str,
    actual_count: int,
):
    status = "PASS" if actual_count >= 0 else "FAIL"

    return ValidationResult(
        source_file=source_file,
        rule_code=rule_code,
        rule_name=rule_name,
        status=status,
        actual_value=str(actual_count),
        expected_value=">=0",
        diff_value=None,
        message=f"{rule_name}: actual={actual_count}",
    )


def validate_source_file(conn: sqlite3.Connection, source_file: str) -> list[ValidationResult]:
    results: list[ValidationResult] = []

    account_row = _get_account_summary_row(conn, source_file)
    if not account_row:
        results.append(
            ValidationResult(
                source_file=source_file,
                rule_code="R000",
                rule_name="account_summary exists",
                status="FAIL",
                message="account_summary 不存在，无法进行金额勾稽",
            )
        )
        return results

    # R201 account_summary 唯一
    account_count = _count_rows(conn, "account_summary", source_file)
    results.append(
        _build_count_result(
            source_file=source_file,
            rule_code="R201",
            rule_name="account_summary row count",
            actual_count=account_count,
            expected_count=1,
        )
    )

    # R001-R005 基础条数检查：适配无成交/无行权/无持仓
    count_rules = [
        ("transaction_record", "R001", "transaction_record count should be >= 0"),
        ("exercise_statement", "R002", "exercise_statement count should be >= 0"),
        ("position_closed", "R003", "position_closed count should be >= 0"),
        ("positions_detail", "R004", "positions_detail count should be >= 0"),
        ("positions", "R005", "positions count should be >= 0"),
    ]

    for table, code, name in count_rules:
        actual = _count_rows(conn, table, source_file)
        results.append(
            _build_nonnegative_count_result(
                source_file=source_file,
                rule_code=code,
                rule_name=name,
                actual_count=actual,
            )
        )

    # R101 平仓盈亏
    results.append(
        _build_compare_result(
            source_file=source_file,
            rule_code="R101",
            rule_name="sum(position_closed.realized_p_l) == account_summary.realized_p_l",
            actual=_sum_value(conn, "position_closed", "realized_p_l", source_file),
            expected=account_row["realized_p_l"],
        )
    )

    # R102 持仓盯市盈亏
    results.append(
        _build_compare_result(
            source_file=source_file,
            rule_code="R102",
            rule_name="sum(positions_detail.mtm_p_l) == account_summary.mtm_p_l",
            actual=_sum_value(conn, "positions_detail", "mtm_p_l", source_file),
            expected=account_row["mtm_p_l"],
        )
    )

    # R103 保证金占用
    results.append(
        _build_compare_result(
            source_file=source_file,
            rule_code="R103",
            rule_name="sum(positions.margin_occupied) == account_summary.margin_occupied",
            actual=_sum_value(conn, "positions", "margin_occupied", source_file),
            expected=account_row["margin_occupied"],
        )
    )

    # R104 多头期权市值
    results.append(
        _build_compare_result(
            source_file=source_file,
            rule_code="R104",
            rule_name="sum(positions.market_value_long) == account_summary.market_value_long",
            actual=_sum_value(conn, "positions", "market_value_long", source_file),
            expected=account_row["market_value_long"],
        )
    )

    # R105 空头期权市值
    results.append(
        _build_compare_result(
            source_file=source_file,
            rule_code="R105",
            rule_name="sum(positions.market_value_short) == account_summary.market_value_short",
            actual=_sum_value(conn, "positions", "market_value_short", source_file),
            expected=account_row["market_value_short"],
        )
    )

    return results