import csv
import sqlite3
from pathlib import Path

from app.reports.sql_loader import load_sql
from app.reports.markdown_builder import build_markdown_report
from app.utils.log_utils import setup_logger


logger = setup_logger()


def generate_daily_report(conn: sqlite3.Connection, output_csv: bool = True):
    sql = load_sql("report_daily_summary_v2.sql")

    cursor = conn.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows_raw = cursor.fetchall()
    rows = [dict(zip(columns, row)) for row in rows_raw]

    logger.info("日报查询完成: rows=%s", len(rows))

    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)

    if output_csv:
        csv_path = output_dir / "daily_report.csv"
        export_to_csv(columns, rows_raw, csv_path)
        logger.info("CSV日报已导出: %s", csv_path)

    if rows:
        date = rows[0].get("date_from", "unknown")
        md_path = output_dir / f"daily_report_{date}.md"

        content = build_markdown_report(rows)

        with md_path.open("w", encoding="utf-8") as f:
            f.write(content)

        logger.info("Markdown日报已生成: %s", md_path)


def export_to_csv(columns, rows, file_path):
    with file_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)