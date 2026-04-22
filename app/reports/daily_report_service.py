import csv
import sqlite3
from pathlib import Path

from app.config import OUTPUT_DIR
from app.reports.markdown_builder import build_markdown_report
from app.reports.sql_loader import load_sql
from app.utils.log_utils import setup_logger

logger = setup_logger()


def generate_daily_report(conn: sqlite3.Connection, output_csv: bool = True) -> dict[str, Path]:
    sql = load_sql("report_daily_summary_v2.sql")
    cursor = conn.execute(sql)

    columns = [desc[0] for desc in cursor.description]
    rows_raw = cursor.fetchall()
    rows = [dict(zip(columns, row)) for row in rows_raw]

    logger.info("日报查询完成 rows=%s", len(rows))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, Path] = {}

    if output_csv:
        csv_path = OUTPUT_DIR / "daily_report.csv"
        export_to_csv(columns, rows_raw, csv_path)
        outputs["csv"] = csv_path
        logger.info("CSV日报已导出: %s", csv_path)

    if rows:
        date_from = rows[0].get("date_from", "unknown")
        md_path = OUTPUT_DIR / f"daily_report_{date_from}.md"
        content = build_markdown_report(rows)

        with md_path.open("w", encoding="utf-8") as f:
            f.write(content)

        outputs["markdown"] = md_path
        logger.info("Markdown日报已生成: %s", md_path)

    return outputs


def export_to_csv(columns, rows, file_path: Path) -> None:
    with file_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)