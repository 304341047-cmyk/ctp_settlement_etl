import sqlite3
from typing import Any

from app.repositories.account_summary_repo import insert_many as insert_account_summary
from app.repositories.transaction_record_repo import insert_many as insert_transaction_records
from app.repositories.exercise_statement_repo import insert_many as insert_exercise_statements
from app.repositories.position_closed_repo import insert_many as insert_position_closed
from app.repositories.positions_detail_repo import insert_many as insert_positions_detail
from app.repositories.positions_repo import insert_many as insert_positions
from app.repositories.validation_result_repo import insert_many as insert_validation_results


def save_parsed_result(conn: sqlite3.Connection, parsed: dict[str, Any]) -> dict[str, int]:
    saved_counts = {
        "account_summary": 0,
        "transaction_record": 0,
        "exercise_statement": 0,
        "position_closed": 0,
        "positions_detail": 0,
        "positions": 0,
    }

    saved_counts["account_summary"] = insert_account_summary(
        conn,
        parsed.get("account_summary", []),
    )

    saved_counts["transaction_record"] = insert_transaction_records(
        conn,
        parsed.get("transaction_record", []),
    )

    saved_counts["exercise_statement"] = insert_exercise_statements(
        conn,
        parsed.get("exercise_statement", []),
    )

    saved_counts["position_closed"] = insert_position_closed(
        conn,
        parsed.get("position_closed", []),
    )

    saved_counts["positions_detail"] = insert_positions_detail(
        conn,
        parsed.get("positions_detail", []),
    )

    saved_counts["positions"] = insert_positions(
        conn,
        parsed.get("positions", []),
    )

    return saved_counts

def save_validation_results(conn: sqlite3.Connection, results) -> int:
    return insert_validation_results(conn, results)