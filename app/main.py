from pathlib import Path

from app.config import ensure_directories
from app.db import get_connection, init_db
from app.db_writer import save_parsed_result, save_validation_results
from app.parser_registry import ParserRegistry
from app.repositories.source_file_repo import (
    exists_by_md5,
    insert_source_file_record,
)
from app.reports.daily_report_service import generate_daily_report
from app.services.validation_service import validate_source_file
from app.utils.file_utils import list_txt_files, move_to_archive, move_to_error
from app.utils.hash_utils import file_md5
from app.utils.log_utils import setup_logger


logger = setup_logger()


def process_file(file_path: Path, registry: ParserRegistry) -> None:
    logger.info("开始处理文件: %s", file_path.name)

    parser = registry.get_parser(file_path)
    if parser is None:
        raise ValueError(f"没有匹配的解析器: {file_path.name}")

    md5 = file_md5(file_path)

    with get_connection() as conn:
        if exists_by_md5(conn, md5):
            logger.info("文件已处理，跳过: %s", file_path.name)
            move_to_archive(file_path)
            return

        parsed = parser.parse(file_path)

        # 调试信息写入文件日志，不刷控制台
        if parsed.get("debug_sections"):
            for section_key, info in parsed["debug_sections"].items():
                logger.debug(
                    "区块=%s | 标题=%s | 数据行=%s | 表头=%s | 英文表头=%s | 汇总=%s",
                    section_key,
                    info["title"],
                    info["data_count"],
                    info["header_count"],
                    info["english_header_count"],
                    info["summary_count"],
                )

        saved_counts = save_parsed_result(conn, parsed)
        logger.info("入库结果: %s", saved_counts)

        validation_results = validate_source_file(conn, file_path.name)
        validation_count = save_validation_results(conn, validation_results)

        pass_count = sum(1 for x in validation_results if x.status == "PASS")
        warn_count = sum(1 for x in validation_results if x.status == "WARN")
        fail_count = sum(1 for x in validation_results if x.status == "FAIL")

        logger.info(
            "核验结果: total=%s, pass=%s, warn=%s, fail=%s",
            validation_count,
            pass_count,
            warn_count,
            fail_count,
        )

        insert_source_file_record(
            conn=conn,
            source_file=file_path.name,
            file_md5=md5,
            parser_name=parser.name,
            process_status="SUCCESS",
            error_message=None,
        )
        conn.commit()

    move_to_archive(file_path)
    logger.info("处理完成: %s", file_path.name)


def main() -> None:
    ensure_directories()
    init_db()

    registry = ParserRegistry()
    files = list_txt_files()

    if not files:
        logger.info("input 目录下没有 txt 文件，直接生成现有数据库日报")
    else:
        for file_path in files:
            try:
                process_file(file_path, registry)
            except Exception as e:
                logger.exception("处理失败: %s", file_path.name)
                try:
                    with get_connection() as conn:
                        md5 = file_md5(file_path)
                        insert_source_file_record(
                            conn=conn,
                            source_file=file_path.name,
                            file_md5=md5,
                            parser_name="UNKNOWN",
                            process_status="FAILED",
                            error_message=str(e),
                        )
                        conn.commit()
                except Exception:
                    logger.exception("写入失败记录时出错: %s", file_path.name)

                move_to_error(file_path)

    try:
        logger.info("开始生成日报")
        with get_connection() as conn:
            generate_daily_report(conn, output_csv=True)
        logger.info("日报生成完成")
    except Exception:
        logger.exception("生成日报失败")


if __name__ == "__main__":
    main()