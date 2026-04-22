from __future__ import annotations

import sqlite3
from pathlib import Path

from app.config import DB_PATH, ensure_directories
from app.db_writer import save_parsed_result, save_validation_results
from app.extractors.text_reader import read_text_file
from app.parsers.ctp_settlement_parser import CtpSettlementParser
from app.reports.daily_report_service import generate_daily_report
from app.db import init_db
from app.services.validation_service import ValidationService
from app.utils.file_utils import list_txt_files, move_to_archive, move_to_error
from app.utils.log_utils import setup_logger
from app.utils.hash_utils import file_md5
from app.repositories.source_file_repo import exists_by_md5, insert_source_file_record

logger = setup_logger()


def process_file(conn: sqlite3.Connection, file_path: Path) -> None:
    logger.info("开始处理文件: %s", file_path)

    parser = CtpSettlementParser()
    validator = ValidationService()

    try:
        md5_value = file_md5(file_path)

        if exists_by_md5(conn, md5_value):
            logger.warning("检测到重复文件，跳过入库: %s md5=%s", file_path.name, md5_value)
            move_to_archive(file_path)
            return

        full_text = read_text_file(file_path)
        parsed = parser.parse(full_text, source_file=file_path.name)

        warnings = parsed.get("warnings", [])
        if warnings:
            for w in warnings:
                logger.warning("解析告警 [%s]: %s", file_path.name, w)

        saved_counts = save_parsed_result(conn, parsed)

        validation_results = validator.validate(parsed)
        validation_count = save_validation_results(conn, validation_results)

        insert_source_file_record(
            conn,
            source_file=file_path.name,
            file_md5=md5_value,
            parser_name="CtpSettlementParser",
            process_status="SUCCESS",
            error_message=None,
        )

        conn.commit()

        logger.info(
            "文件处理完成: %s | 入库=%s | 核验=%s",
            file_path.name,
            saved_counts,
            validation_count,
        )

        move_to_archive(file_path)

    except Exception as e:
        conn.rollback()
        logger.exception("处理失败: %s | error=%s", file_path.name, e)
        move_to_error(file_path)


def main() -> None:
    ensure_directories()
    init_db()

    files = list_txt_files()
    if not files:
        logger.info("input 目录下没有待处理文件")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        for file_path in files:
            process_file(conn, file_path)

        outputs = generate_daily_report(conn, output_csv=True)
        logger.info("日报生成完成: %s", outputs)

    finally:
        conn.close()


if __name__ == "__main__":
    main()